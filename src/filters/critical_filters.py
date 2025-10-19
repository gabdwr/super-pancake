"""
Critical Filters Module (v3 - Configurable)

This module implements static Tier 1 filters to automatically tag tokens as PASS/FAIL/PENDING.
These filters are designed to catch obvious scams and low-quality tokens before
they enter the watchlist.

CHANGES in v3:
- All filter thresholds now configurable via environment variables
- Keeps your exact strategy private (not committed to git)
- Allows easy tuning without code changes

CHANGES in v2:
- Added PENDING status for tokens with missing GoPlus data
- Relaxed thresholds for newly discovered tokens
- Fixed GoPlus data validation

7 Critical Filters (CONFIGURABLE VIA .env):
1. is_honeypot == False (configurable: FILTER_ALLOW_HONEYPOT)
2. lp_locked_percent >= FILTER_MIN_LP_LOCKED (default: 30)
3. concentration_score >= FILTER_MIN_CONCENTRATION (default: 50)
4. liquidity_usd >= FILTER_MIN_LIQUIDITY_USD (default: 20000)
5. buy_tax <= FILTER_MAX_BUY_TAX (default: 10)
6. sell_tax <= FILTER_MAX_SELL_TAX (default: 10)
7. is_mintable == False (configurable: FILTER_ALLOW_MINTABLE)
"""

import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Load filter thresholds from environment variables
# These are YOUR secret strategy - not committed to git!
def _get_bool_env(key: str, default: bool) -> bool:
    """Helper to parse boolean environment variables"""
    val = os.getenv(key, str(default)).lower()
    return val in ('true', '1', 'yes', 'on')

def _get_float_env(key: str, default: float) -> float:
    """Helper to parse float environment variables"""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        logger.warning(f"Invalid value for {key}, using default: {default}")
        return default

# Filter Configuration (loaded from .env)
FILTER_ALLOW_HONEYPOT = _get_bool_env('FILTER_ALLOW_HONEYPOT', False)
FILTER_MIN_LP_LOCKED = _get_float_env('FILTER_MIN_LP_LOCKED', 30.0)
FILTER_MIN_CONCENTRATION = _get_float_env('FILTER_MIN_CONCENTRATION', 50.0)
FILTER_MIN_LIQUIDITY_USD = _get_float_env('FILTER_MIN_LIQUIDITY_USD', 20000.0)
FILTER_MAX_BUY_TAX = _get_float_env('FILTER_MAX_BUY_TAX', 10.0)
FILTER_MAX_SELL_TAX = _get_float_env('FILTER_MAX_SELL_TAX', 10.0)
FILTER_ALLOW_MINTABLE = _get_bool_env('FILTER_ALLOW_MINTABLE', False)

# Log loaded configuration (on module import)
logger.info("🔧 Critical Filters Configuration:")
logger.info(f"   Allow Honeypot: {FILTER_ALLOW_HONEYPOT}")
logger.info(f"   Min LP Locked: {FILTER_MIN_LP_LOCKED}%")
logger.info(f"   Min Concentration: {FILTER_MIN_CONCENTRATION}")
logger.info(f"   Min Liquidity: ${FILTER_MIN_LIQUIDITY_USD:,.0f}")
logger.info(f"   Max Buy Tax: {FILTER_MAX_BUY_TAX}%")
logger.info(f"   Max Sell Tax: {FILTER_MAX_SELL_TAX}%")
logger.info(f"   Allow Mintable: {FILTER_ALLOW_MINTABLE}")


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
    Returns PENDING if GoPlus data is missing or invalid (API failure).

    Args:
        goplus_data: GoPlus security data for the token
        dexscreener_data: DexScreener token data
        pairs: List of DexScreener pairs for concentration calculation

    Returns:
        {
            'status': 'PASS' | 'FAIL' | 'PENDING',
            'reasons': List[str],  # Empty if PASS, contains failure reasons if FAIL/PENDING
            'details': {
                'is_honeypot': bool or None,
                'lp_locked_percent': float,
                'concentration_score': float,
                'liquidity_usd': float,
                'buy_tax': float or None,
                'sell_tax': float or None,
                'is_mintable': bool or None
            }
        }
    """
    reasons = []

    # CRITICAL: Validate GoPlus data before using it
    # If buy_tax or sell_tax is None/missing, GoPlus API failed or returned invalid data
    goplus_valid = (
        goplus_data and
        goplus_data.get('buy_tax') is not None and
        goplus_data.get('sell_tax') is not None and
        goplus_data.get('is_honeypot') is not None
    )

    if not goplus_valid:
        logger.info("⏸️  GoPlus data missing or invalid - marking as PENDING")

        # Calculate what we can without GoPlus
        concentration_score = calculate_concentration_score(pairs)
        liquidity_usd = 0.0
        if pairs:
            main_pair = max(pairs, key=lambda p: p.get('liquidity', {}).get('usd', 0))
            liquidity_usd = main_pair.get('liquidity', {}).get('usd', 0)

        return {
            'status': 'PENDING',
            'reasons': ['goplus_data_missing_or_invalid'],
            'details': {
                'is_honeypot': None,
                'lp_locked_percent': 0.0,
                'concentration_score': concentration_score,
                'liquidity_usd': round(liquidity_usd, 2),
                'buy_tax': None,
                'sell_tax': None,
                'is_mintable': None
            }
        }

    # GoPlus data is valid - extract values
    is_honeypot = goplus_data.get('is_honeypot', False)
    is_mintable = goplus_data.get('is_mintable', False)

    # Parse tax values (GoPlus returns percentages 0-100)
    buy_tax = float(goplus_data.get('buy_tax', 0))
    sell_tax = float(goplus_data.get('sell_tax', 0))

    # Parse LP locked percentage
    lp_locked_percent = float(goplus_data.get('lp_locked_percent', 0))

    # Calculate concentration score from pairs
    concentration_score = calculate_concentration_score(pairs)

    # Extract liquidity from DexScreener (use main pair)
    liquidity_usd = 0.0
    if pairs:
        main_pair = max(pairs, key=lambda p: p.get('liquidity', {}).get('usd', 0))
        liquidity_usd = main_pair.get('liquidity', {}).get('usd', 0)

    # Apply filters with CONFIGURABLE THRESHOLDS (from .env)
    # Filter 1: is_honeypot check
    if not FILTER_ALLOW_HONEYPOT and is_honeypot:
        reasons.append('honeypot_detected')

    # Filter 2: LP locked percentage
    if lp_locked_percent < FILTER_MIN_LP_LOCKED:
        reasons.append(f'lp_locked_too_low_{lp_locked_percent:.1f}%')

    # Filter 3: Concentration score
    if concentration_score < FILTER_MIN_CONCENTRATION:
        reasons.append(f'concentration_too_low_{concentration_score:.1f}')

    # Filter 4: Minimum liquidity USD
    if liquidity_usd < FILTER_MIN_LIQUIDITY_USD:
        reasons.append(f'liquidity_too_low_${liquidity_usd:.0f}')

    # Filter 5: Maximum buy tax
    if buy_tax > FILTER_MAX_BUY_TAX:
        reasons.append(f'buy_tax_too_high_{buy_tax:.1f}%')

    # Filter 6: Maximum sell tax
    if sell_tax > FILTER_MAX_SELL_TAX:
        reasons.append(f'sell_tax_too_high_{sell_tax:.1f}%')

    # Filter 7: Mintable token check
    if not FILTER_ALLOW_MINTABLE and is_mintable:
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
        logger.info("✅ Token PASSED all critical filters")
    else:
        logger.info(f"❌ Token FAILED critical filters: {', '.join(reasons)}")

    return result
