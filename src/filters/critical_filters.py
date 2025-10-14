"""
Critical Filters Module

This module implements static Tier 1 filters to automatically tag tokens as PASS/FAIL.
These filters are designed to catch obvious scams and low-quality tokens before
they enter the watchlist.

7 Critical Filters:
1. is_honeypot == False
2. lp_locked_percent >= 60
3. concentration_score >= 60
4. liquidity_usd >= 50000
5. buy_tax <= 10
6. sell_tax <= 10
7. is_mintable == False
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def calculate_concentration_score(pairs: List[Dict]) -> float:
    """
    Calculate concentration score from DexScreener pairs data.

    This reuses the logic from liquidity.py to ensure consistency.

    Scoring:
    - 80-100: HEALTHY (concentrated, safe)
    - 50-79: CAUTION (moderate fragmentation)
    - 0-49: RED_FLAG (dangerously fragmented)

    Args:
        pairs: List of pair dictionaries from DexScreener

    Returns:
        Concentration score (0-100)
    """
    if not pairs:
        return 0.0

    # Sort pairs by liquidity (highest first)
    sorted_pairs = sorted(
        pairs,
        key=lambda p: p.get('liquidity', {}).get('usd', 0),
        reverse=True
    )

    total_liquidity = sum(p.get('liquidity', {}).get('usd', 0) for p in pairs)
    main_pair = sorted_pairs[0]
    main_pair_liquidity = main_pair.get('liquidity', {}).get('usd', 0)

    concentration_ratio = main_pair_liquidity / total_liquidity if total_liquidity > 0 else 0

    # Determine score based on liquidity tier
    if total_liquidity > 10_000_000:  # $10M+ = Established token
        if concentration_ratio >= 0.3 and main_pair_liquidity > 5_000_000:
            score = 80 + (concentration_ratio * 20)  # 80-100
        elif concentration_ratio >= 0.2:
            score = 50 + (concentration_ratio * 30)  # 50-80
        else:
            score = concentration_ratio * 50  # 0-50

    elif total_liquidity >= 500_000:  # $500K-$10M = Target range
        if concentration_ratio >= 0.75:  # 75%+ in main pair
            score = 85 + (concentration_ratio * 15)  # 85-100
        elif concentration_ratio >= 0.6:  # 60-75% acceptable
            score = 60 + (concentration_ratio * 25)  # 60-85
        else:  # <60% = fragmented (risky)
            score = concentration_ratio * 60  # 0-60

    else:  # <$500K = Low liquidity (very risky)
        if concentration_ratio >= 0.9:
            score = 40 + (concentration_ratio * 20)  # 40-60
        else:
            score = concentration_ratio * 40  # 0-40

    return round(score, 2)


def apply_critical_filters(
    goplus_data: Dict,
    dexscreener_data: Dict,
    pairs: List[Dict]
) -> Dict:
    """
    Apply 7 static critical filters to a token.

    Returns PASS only if ALL filters pass. Returns FAIL with reasons if any filter fails.

    Args:
        goplus_data: GoPlus security data for the token
        dexscreener_data: DexScreener token data
        pairs: List of DexScreener pairs for concentration calculation

    Returns:
        {
            'status': 'PASS' | 'FAIL',
            'reasons': List[str],  # Empty if PASS, contains failure reasons if FAIL
            'details': {
                'is_honeypot': bool,
                'lp_locked_percent': float,
                'concentration_score': float,
                'liquidity_usd': float,
                'buy_tax': float,
                'sell_tax': float,
                'is_mintable': bool
            }
        }
    """
    reasons = []

    # Extract GoPlus data (handle missing data gracefully)
    is_honeypot = goplus_data.get('is_honeypot', '1') == '1'  # Default to True (safe)
    is_mintable = goplus_data.get('is_mintable', '1') == '1'  # Default to True (safe)

    # Parse tax values (GoPlus returns strings like "0.05" for 5%)
    try:
        buy_tax = float(goplus_data.get('buy_tax', '1.0')) * 100  # Convert to percentage
    except (ValueError, TypeError):
        buy_tax = 100.0  # Default to 100% (safe)

    try:
        sell_tax = float(goplus_data.get('sell_tax', '1.0')) * 100  # Convert to percentage
    except (ValueError, TypeError):
        sell_tax = 100.0  # Default to 100% (safe)

    # Parse LP locked percentage
    try:
        lp_locked_percent = float(goplus_data.get('lp_holder_percent', '0'))
    except (ValueError, TypeError):
        lp_locked_percent = 0.0

    # Calculate concentration score from pairs
    concentration_score = calculate_concentration_score(pairs)

    # Extract liquidity from DexScreener (use main pair)
    liquidity_usd = 0.0
    if pairs:
        main_pair = max(pairs, key=lambda p: p.get('liquidity', {}).get('usd', 0))
        liquidity_usd = main_pair.get('liquidity', {}).get('usd', 0)

    # Apply filters
    # Filter 1: is_honeypot == False
    if is_honeypot:
        reasons.append('honeypot_detected')

    # Filter 2: lp_locked_percent >= 60
    if lp_locked_percent < 60:
        reasons.append(f'lp_locked_too_low_{lp_locked_percent:.1f}%')

    # Filter 3: concentration_score >= 60
    if concentration_score < 60:
        reasons.append(f'concentration_too_low_{concentration_score:.1f}')

    # Filter 4: liquidity_usd >= 50000
    if liquidity_usd < 50000:
        reasons.append(f'liquidity_too_low_${liquidity_usd:.0f}')

    # Filter 5: buy_tax <= 10
    if buy_tax > 10:
        reasons.append(f'buy_tax_too_high_{buy_tax:.1f}%')

    # Filter 6: sell_tax <= 10
    if sell_tax > 10:
        reasons.append(f'sell_tax_too_high_{sell_tax:.1f}%')

    # Filter 7: is_mintable == False
    if is_mintable:
        reasons.append('token_is_mintable')

    # Determine status
    status = 'PASS' if len(reasons) == 0 else 'FAIL'

    result = {
        'status': status,
        'reasons': reasons,
        'details': {
            'is_honeypot': is_honeypot,
            'lp_locked_percent': round(lp_locked_percent, 2),
            'concentration_score': concentration_score,
            'liquidity_usd': round(liquidity_usd, 2),
            'buy_tax': round(buy_tax, 2),
            'sell_tax': round(sell_tax, 2),
            'is_mintable': is_mintable
        }
    }

    # Log result
    if status == 'PASS':
        logger.info(f"Token PASSED all critical filters")
    else:
        logger.info(f"Token FAILED critical filters: {', '.join(reasons)}")

    return result
