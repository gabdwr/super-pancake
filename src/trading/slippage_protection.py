"""
Slippage Protection Module

Calculates and enforces slippage protection for token swaps.
Uses constant product formula (x*y=k) for accurate slippage estimation.

Modern 2025 feature: Dynamic slippage tolerance based on pool quality analysis.
"""

import logging
from typing import Dict, Optional, Tuple
from web3 import Web3

from config.constants import (
    DEFAULT_SLIPPAGE_TOLERANCE,
    MAX_SLIPPAGE_TOLERANCE,
    LOW_SLIPPAGE_TOLERANCE,
    MEDIUM_SLIPPAGE_TOLERANCE,
    HIGH_SLIPPAGE_ALERT_THRESHOLD,
    SLIPPAGE_BY_POOL_QUALITY,
    SLIPPAGE_BY_LIQUIDITY_SCORE,
    ABORT_ON_HIGH_SLIPPAGE
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_slippage_tolerance(token_data: Dict) -> float:
    """
    Calculate dynamic slippage tolerance based on pool quality

    Uses liquidity analysis results to determine appropriate slippage tolerance.
    Higher quality pools get lower slippage tolerance (more strict).

    Args:
        token_data: Token dictionary with liquidity_analysis field

    Returns:
        Slippage tolerance as percentage (e.g., 2.0 = 2%)
    """
    # Check if liquidity analysis exists
    liquidity_analysis = token_data.get('liquidity_analysis', {})

    if not liquidity_analysis:
        logger.warning("No liquidity analysis found, using default slippage tolerance")
        return DEFAULT_SLIPPAGE_TOLERANCE

    # Get recommendation (PASS, CAUTION, REJECT)
    recommendation = liquidity_analysis.get('recommendation', 'CAUTION')

    # Get slippage flag from analysis
    slippage_data = liquidity_analysis.get('analysis', {}).get('slippage', {})
    slippage_flag = slippage_data.get('flag', 'MEDIUM')

    # Method 1: Use recommendation-based tolerance
    recommendation_tolerance = SLIPPAGE_BY_LIQUIDITY_SCORE.get(recommendation)

    # Method 2: Use slippage flag-based tolerance
    flag_tolerance = SLIPPAGE_BY_POOL_QUALITY.get(slippage_flag, MEDIUM_SLIPPAGE_TOLERANCE)

    # Use the more conservative (lower) of the two
    if recommendation_tolerance is None:
        logger.error(f"Token has REJECT recommendation, should not trade")
        return None

    tolerance = min(recommendation_tolerance, flag_tolerance)

    logger.info(f"Dynamic slippage tolerance: {tolerance}% (recommendation={recommendation}, flag={slippage_flag})")

    return tolerance


def estimate_price_impact(
    amount_in: float,
    reserve_in: float,
    reserve_out: float,
    fee_percent: float = 0.25
) -> float:
    """
    Estimate price impact using constant product formula (x*y=k)

    PancakeSwap V2 uses 0.25% fee (0.17% to LPs, 0.08% burned)

    Formula:
    amount_out = (amount_in * (1 - fee) * reserve_out) / (reserve_in + amount_in * (1 - fee))
    price_impact = (amount_in / reserve_in) * 100

    Args:
        amount_in: Input amount (in input token)
        reserve_in: Reserve of input token in pool
        reserve_out: Reserve of output token in pool
        fee_percent: Trading fee percentage (default 0.25% for PancakeSwap)

    Returns:
        Estimated price impact as percentage
    """
    if reserve_in <= 0 or reserve_out <= 0:
        logger.error("Invalid reserves")
        return 100.0  # 100% slippage if reserves invalid

    # Apply fee
    amount_in_with_fee = amount_in * (1 - fee_percent / 100)

    # Calculate amount out using constant product formula
    numerator = amount_in_with_fee * reserve_out
    denominator = reserve_in + amount_in_with_fee

    amount_out = numerator / denominator

    # Calculate price impact
    # Price impact = change in reserve ratio
    new_reserve_in = reserve_in + amount_in
    new_reserve_out = reserve_out - amount_out

    price_before = reserve_out / reserve_in
    price_after = new_reserve_out / new_reserve_in

    price_impact = abs((price_after - price_before) / price_before) * 100

    return price_impact


def calculate_minimum_output_tokens(
    expected_output: float,
    slippage_tolerance: float
) -> float:
    """
    Calculate minimum output tokens (amountOutMin) for slippage protection

    This is the value passed to PancakeSwap router to enforce maximum slippage.

    Args:
        expected_output: Expected number of output tokens
        slippage_tolerance: Slippage tolerance as percentage (e.g., 2.0 = 2%)

    Returns:
        Minimum output tokens (amountOutMin)
    """
    if slippage_tolerance < 0 or slippage_tolerance > 100:
        logger.error(f"Invalid slippage tolerance: {slippage_tolerance}%")
        slippage_tolerance = DEFAULT_SLIPPAGE_TOLERANCE

    # Calculate minimum output
    slippage_multiplier = 1 - (slippage_tolerance / 100)
    min_output = expected_output * slippage_multiplier

    logger.debug(f"Expected: {expected_output}, Min: {min_output} (tolerance: {slippage_tolerance}%)")

    return min_output


def should_abort_high_slippage(
    estimated_slippage: float,
    max_tolerance: Optional[float] = None
) -> Tuple[bool, str]:
    """
    Determine if trade should be aborted due to high slippage

    Args:
        estimated_slippage: Estimated slippage percentage
        max_tolerance: Maximum tolerable slippage (uses config default if None)

    Returns:
        Tuple of (should_abort, reason)
    """
    if max_tolerance is None:
        max_tolerance = MAX_SLIPPAGE_TOLERANCE

    # Check if slippage exceeds maximum
    if estimated_slippage > max_tolerance:
        reason = f"Estimated slippage {estimated_slippage:.2f}% exceeds maximum {max_tolerance:.2f}%"
        logger.warning(f"ABORT: {reason}")
        return True, reason

    # Check if slippage is high but within tolerance (warning)
    if estimated_slippage > HIGH_SLIPPAGE_ALERT_THRESHOLD:
        logger.warning(f"HIGH SLIPPAGE WARNING: {estimated_slippage:.2f}% (threshold: {HIGH_SLIPPAGE_ALERT_THRESHOLD}%)")

    return False, ""


def get_slippage_params_for_router(
    token_data: Dict,
    trade_amount_bnb: float,
    reserves: Optional[Dict] = None
) -> Dict:
    """
    Get complete slippage parameters for PancakeSwap router call

    This is the main function to use before executing a trade.
    Returns all parameters needed for swap execution with slippage protection.

    Args:
        token_data: Token data with liquidity analysis
        trade_amount_bnb: Trade amount in BNB
        reserves: Optional current reserves (if not provided, uses analysis data)

    Returns:
        Dictionary with:
        - slippage_tolerance: Calculated tolerance %
        - estimated_slippage: Estimated price impact %
        - amountOutMin: Minimum output tokens (for router)
        - should_abort: Whether to abort trade
        - abort_reason: Reason for abort (if applicable)
        - warnings: List of warnings
    """
    result = {
        'slippage_tolerance': DEFAULT_SLIPPAGE_TOLERANCE,
        'estimated_slippage': 0,
        'amountOutMin': 0,
        'should_abort': False,
        'abort_reason': '',
        'warnings': []
    }

    # Calculate dynamic slippage tolerance
    slippage_tolerance = calculate_slippage_tolerance(token_data)

    if slippage_tolerance is None:
        result['should_abort'] = True
        result['abort_reason'] = "Token has REJECT recommendation"
        return result

    result['slippage_tolerance'] = slippage_tolerance

    # Get liquidity analysis
    liquidity_analysis = token_data.get('liquidity_analysis', {})
    slippage_data = liquidity_analysis.get('analysis', {}).get('slippage', {})

    # Estimate slippage from analysis or calculate from reserves
    if reserves:
        # Calculate from actual reserves
        reserve_bnb = reserves.get('reserve_bnb', 0)
        reserve_token = reserves.get('reserve_token', 0)

        if reserve_bnb > 0 and reserve_token > 0:
            estimated_slippage = estimate_price_impact(
                amount_in=trade_amount_bnb,
                reserve_in=reserve_bnb,
                reserve_out=reserve_token
            )
            result['estimated_slippage'] = estimated_slippage
        else:
            result['warnings'].append("Invalid reserves provided")
    else:
        # Use analysis estimate
        estimated_slippage = slippage_data.get('estimated_slippage_percent', 0)
        result['estimated_slippage'] = estimated_slippage

    # Check if should abort due to high slippage
    if ABORT_ON_HIGH_SLIPPAGE:
        should_abort, reason = should_abort_high_slippage(
            result['estimated_slippage'],
            MAX_SLIPPAGE_TOLERANCE
        )
        if should_abort:
            result['should_abort'] = True
            result['abort_reason'] = reason
            return result

    # Calculate minimum output
    # Note: Actual expected_output should come from router.getAmountsOut()
    # This is a placeholder - will be calculated by execution_helpers
    result['amountOutMin'] = 0  # Placeholder, set by execution module

    logger.info(f"Slippage params: tolerance={slippage_tolerance}%, estimated={result['estimated_slippage']:.2f}%")

    return result


def format_slippage_for_display(slippage_decimal: float) -> str:
    """
    Format slippage for human-readable display

    Args:
        slippage_decimal: Slippage as decimal (e.g., 0.02 for 2%)

    Returns:
        Formatted string (e.g., "2.00%")
    """
    return f"{slippage_decimal * 100:.2f}%"


def calculate_slippage_from_prices(
    expected_price: float,
    execution_price: float
) -> float:
    """
    Calculate actual slippage from expected vs execution price

    Used for post-trade analysis.

    Args:
        expected_price: Expected price per token
        execution_price: Actual execution price per token

    Returns:
        Slippage as percentage
    """
    if expected_price <= 0:
        logger.error("Invalid expected price")
        return 0

    slippage = abs((execution_price - expected_price) / expected_price) * 100

    return slippage


# =============================================================================
# Validation and Testing
# =============================================================================

def validate_slippage_params(slippage_tolerance: float) -> bool:
    """
    Validate slippage parameters are within acceptable range

    Args:
        slippage_tolerance: Tolerance to validate

    Returns:
        True if valid, False otherwise
    """
    if slippage_tolerance < 0:
        logger.error("Slippage tolerance cannot be negative")
        return False

    if slippage_tolerance > MAX_SLIPPAGE_TOLERANCE:
        logger.error(f"Slippage tolerance {slippage_tolerance}% exceeds maximum {MAX_SLIPPAGE_TOLERANCE}%")
        return False

    return True


if __name__ == "__main__":
    print("Slippage Protection Module Test")
    print("=" * 60)

    # Test 1: Price impact calculation
    print("\nTest 1: Price Impact Calculation")
    impact = estimate_price_impact(
        amount_in=0.1,  # 0.1 BNB
        reserve_in=100,  # 100 BNB in pool
        reserve_out=1000000  # 1M tokens in pool
    )
    print(f"  Price impact for 0.1 BNB trade: {impact:.4f}%")

    # Test 2: Minimum output calculation
    print("\nTest 2: Minimum Output Calculation")
    expected = 10000  # Expect 10k tokens
    min_out = calculate_minimum_output_tokens(expected, 2.0)  # 2% slippage
    print(f"  Expected: {expected}, Min output (2% slippage): {min_out}")

    # Test 3: Slippage abort decision
    print("\nTest 3: Slippage Abort Decision")
    should_abort, reason = should_abort_high_slippage(6.0)  # 6% slippage
    print(f"  Should abort 6% slippage: {should_abort} - {reason}")

    # Test 4: Dynamic tolerance
    print("\nTest 4: Dynamic Slippage Tolerance")
    test_token = {
        'liquidity_analysis': {
            'recommendation': 'PASS',
            'total_score': 85,
            'analysis': {
                'slippage': {'flag': 'LOW'}
            }
        }
    }
    tolerance = calculate_slippage_tolerance(test_token)
    print(f"  Tolerance for PASS/LOW token: {tolerance}%")

    print("\n" + "=" * 60)
    print("✅ Slippage protection module loaded successfully")
