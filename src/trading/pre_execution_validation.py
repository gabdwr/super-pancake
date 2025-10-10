"""
Pre-Execution Validation Module

Validates token conditions immediately before trade execution to prevent:
- Rugpulls-in-progress (liquidity being drained)
- Stale data execution (discovery data too old)
- Pool reserve imbalances
- Insufficient liquidity

Modern 2025 feature: Real-time on-chain validation before every trade.
"""

import logging
import time
import requests
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
from web3 import Web3

from config.settings import ALCHEMY_BSC_RPC
from config.constants import (
    MIN_LIQUIDITY_RETENTION_RATIO,
    LIQUIDITY_STALENESS_SECONDS,
    MIN_LIQUIDITY_RECHECK_USD,
    LIQUIDITY_DROP_WARNING_PERCENT,
    CRITICAL_LIQUIDITY_DROP_PERCENT,
    MIN_RESERVE_RATIO,
    MAX_RESERVE_RATIO,
    RESERVE_IMBALANCE_WARNING,
    ABORT_ON_LIQUIDITY_DROP,
    ABORT_ON_STALE_DATA,
    ABORT_ON_RESERVE_IMBALANCE,
    ABORT_ON_INSUFFICIENT_LIQUIDITY,
    WARN_ON_MODERATE_LIQUIDITY_DROP,
    WARN_ON_RESERVE_WARNING_LEVEL,
    RPC_RETRY_ATTEMPTS,
    RPC_RETRY_DELAY_SECONDS,
    RPC_TIMEOUT_SECONDS
)
from config.contract_abis import get_pair_contract, PAIR_ABI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_current_liquidity(
    token_address: str,
    original_liquidity: float,
    min_liquidity_required: float = MIN_LIQUIDITY_RECHECK_USD
) -> Dict:
    """
    Validate current liquidity hasn't dropped significantly since discovery

    Queries DexScreener API for current liquidity and compares to original.
    Detects rugpulls-in-progress where liquidity is being drained.

    Args:
        token_address: Token contract address
        original_liquidity: Original liquidity from discovery time
        min_liquidity_required: Minimum acceptable liquidity

    Returns:
        {
            'current_liquidity': float,
            'liquidity_change_percent': float,
            'is_valid': bool,
            'should_abort': bool,
            'warnings': List[str],
            'error': str or None
        }
    """
    result = {
        'current_liquidity': 0,
        'liquidity_change_percent': 0,
        'is_valid': False,
        'should_abort': False,
        'warnings': [],
        'error': None
    }

    try:
        # Query DexScreener for current pair data
        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            result['error'] = f"DexScreener API error: {response.status_code}"
            result['should_abort'] = True
            return result

        data = response.json()
        pairs = data.get('pairs', [])

        # Filter for BSC pairs
        bsc_pairs = [p for p in pairs if p.get('chainId') == 'bsc']

        if not bsc_pairs:
            result['error'] = "No BSC pairs found"
            result['should_abort'] = True
            return result

        # Get main pair (highest liquidity)
        main_pair = max(bsc_pairs, key=lambda p: p.get('liquidity', {}).get('usd', 0))
        current_liquidity = main_pair.get('liquidity', {}).get('usd', 0)

        result['current_liquidity'] = current_liquidity

        # Calculate change percentage
        if original_liquidity > 0:
            change = ((current_liquidity - original_liquidity) / original_liquidity) * 100
            result['liquidity_change_percent'] = change
        else:
            result['liquidity_change_percent'] = 0

        # Check if liquidity dropped below minimum
        if current_liquidity < min_liquidity_required:
            result['warnings'].append(f"Current liquidity ${current_liquidity:,.0f} below minimum ${min_liquidity_required:,.0f}")
            if ABORT_ON_INSUFFICIENT_LIQUIDITY:
                result['should_abort'] = True
                return result

        # Check for critical liquidity drop
        if result['liquidity_change_percent'] < -CRITICAL_LIQUIDITY_DROP_PERCENT:
            result['warnings'].append(f"CRITICAL: Liquidity dropped {abs(result['liquidity_change_percent']):.1f}%")
            if ABORT_ON_LIQUIDITY_DROP:
                result['should_abort'] = True
                return result

        # Check for moderate liquidity drop
        if result['liquidity_change_percent'] < -LIQUIDITY_DROP_WARNING_PERCENT:
            if WARN_ON_MODERATE_LIQUIDITY_DROP:
                result['warnings'].append(f"WARNING: Liquidity dropped {abs(result['liquidity_change_percent']):.1f}%")

        # Check retention ratio
        retention_ratio = current_liquidity / original_liquidity if original_liquidity > 0 else 0
        if retention_ratio < MIN_LIQUIDITY_RETENTION_RATIO:
            result['warnings'].append(f"Liquidity retention {retention_ratio:.1%} below minimum {MIN_LIQUIDITY_RETENTION_RATIO:.1%}")
            if ABORT_ON_LIQUIDITY_DROP:
                result['should_abort'] = True
                return result

        result['is_valid'] = True
        logger.info(f"Liquidity validation: ${current_liquidity:,.0f} (change: {result['liquidity_change_percent']:+.1f}%)")

    except Exception as e:
        result['error'] = f"Error validating liquidity: {e}"
        result['should_abort'] = True
        logger.error(result['error'])

    return result


def check_data_staleness(discovery_timestamp: datetime) -> Dict:
    """
    Check if discovery data is too old for safe execution

    Args:
        discovery_timestamp: Timestamp when token was discovered

    Returns:
        {
            'age_seconds': float,
            'is_stale': bool,
            'should_abort': bool,
            'warning': str or None
        }
    """
    result = {
        'age_seconds': 0,
        'is_stale': False,
        'should_abort': False,
        'warning': None
    }

    now = datetime.now()
    age = (now - discovery_timestamp).total_seconds()
    result['age_seconds'] = age

    if age > LIQUIDITY_STALENESS_SECONDS:
        result['is_stale'] = True
        result['warning'] = f"Discovery data is {age:.0f}s old (max: {LIQUIDITY_STALENESS_SECONDS}s)"

        if ABORT_ON_STALE_DATA:
            result['should_abort'] = True
            logger.warning(f"ABORT: {result['warning']}")
        else:
            logger.warning(result['warning'])

    return result


def get_current_pair_reserves(
    pair_address: str,
    w3: Optional[Web3] = None
) -> Dict:
    """
    Query on-chain reserves for a trading pair

    Args:
        pair_address: Pair contract address
        w3: Web3 instance (creates new one if not provided)

    Returns:
        {
            'reserve0': int,
            'reserve1': int,
            'blockTimestampLast': int,
            'ratio': float,
            'is_valid': bool,
            'error': str or None
        }
    """
    result = {
        'reserve0': 0,
        'reserve1': 0,
        'blockTimestampLast': 0,
        'ratio': 0,
        'is_valid': False,
        'error': None
    }

    # Create Web3 instance if not provided
    if w3 is None:
        try:
            w3 = Web3(Web3.HTTPProvider(ALCHEMY_BSC_RPC))
            if not w3.is_connected():
                # Fallback to public RPC
                w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
        except Exception as e:
            result['error'] = f"Failed to connect to BSC RPC: {e}"
            return result

    # Retry logic for RPC calls
    for attempt in range(RPC_RETRY_ATTEMPTS):
        try:
            # Get pair contract
            pair_contract = get_pair_contract(w3, pair_address)

            # Get reserves
            reserves = pair_contract.functions.getReserves().call()

            result['reserve0'] = reserves[0]
            result['reserve1'] = reserves[1]
            result['blockTimestampLast'] = reserves[2]

            # Calculate ratio
            if result['reserve1'] > 0:
                result['ratio'] = result['reserve0'] / result['reserve1']
            else:
                result['ratio'] = 0

            result['is_valid'] = True
            logger.info(f"Reserves: {result['reserve0']/1e18:.2f} / {result['reserve1']/1e18:.2f} (ratio: {result['ratio']:.4f})")
            break

        except Exception as e:
            if attempt < RPC_RETRY_ATTEMPTS - 1:
                logger.warning(f"RPC attempt {attempt+1} failed, retrying...")
                time.sleep(RPC_RETRY_DELAY_SECONDS)
            else:
                result['error'] = f"Failed to get reserves after {RPC_RETRY_ATTEMPTS} attempts: {e}"
                logger.error(result['error'])

    return result


def validate_pool_reserves(pair_address: str, w3: Optional[Web3] = None) -> Dict:
    """
    Validate pool reserves are balanced (not heavily skewed)

    Highly imbalanced pools can indicate:
    - Dump in progress
    - Low liquidity manipulation
    - Impermanent loss trap

    Args:
        pair_address: Pair contract address
        w3: Web3 instance (optional)

    Returns:
        {
            'ratio': float,
            'is_balanced': bool,
            'should_abort': bool,
            'warnings': List[str]
        }
    """
    result = {
        'ratio': 0,
        'is_balanced': False,
        'should_abort': False,
        'warnings': []
    }

    # Get current reserves
    reserves = get_current_pair_reserves(pair_address, w3)

    if not reserves['is_valid']:
        result['warnings'].append(f"Failed to get reserves: {reserves['error']}")
        result['should_abort'] = True
        return result

    ratio = reserves['ratio']
    result['ratio'] = ratio

    # Check if ratio is within acceptable range
    if ratio < MIN_RESERVE_RATIO or ratio > MAX_RESERVE_RATIO:
        result['warnings'].append(f"Reserve ratio {ratio:.4f} outside acceptable range ({MIN_RESERVE_RATIO}-{MAX_RESERVE_RATIO})")

        if ABORT_ON_RESERVE_IMBALANCE:
            result['should_abort'] = True
            logger.warning(f"ABORT: Severe reserve imbalance")
            return result

    # Check for warning level imbalance
    if ratio < (1/RESERVE_IMBALANCE_WARNING) or ratio > RESERVE_IMBALANCE_WARNING:
        if WARN_ON_RESERVE_WARNING_LEVEL:
            result['warnings'].append(f"Moderate reserve imbalance: ratio {ratio:.4f}")

    if not result['warnings']:
        result['is_balanced'] = True

    return result


def comprehensive_pre_execution_check(
    token_data: Dict,
    w3: Optional[Web3] = None
) -> Dict:
    """
    Master function: Run all pre-execution validation checks

    This is the main function to call before executing any trade.
    Runs all safety checks and returns comprehensive validation result.

    Args:
        token_data: Token data dictionary with liquidity_analysis and discovery_timestamp
        w3: Web3 instance (optional)

    Returns:
        {
            'is_valid': bool,
            'should_abort': bool,
            'checks': {
                'liquidity': Dict,
                'staleness': Dict,
                'reserves': Dict
            },
            'warnings': List[str],
            'errors': List[str],
            'abort_reasons': List[str]
        }
    """
    result = {
        'is_valid': False,
        'should_abort': False,
        'checks': {},
        'warnings': [],
        'errors': [],
        'abort_reasons': []
    }

    logger.info("Starting comprehensive pre-execution validation...")

    # Extract token info
    token_address = token_data.get('baseToken', {}).get('address')
    if not token_address:
        result['errors'].append("No token address found")
        result['should_abort'] = True
        return result

    # Get original liquidity from token data
    original_liquidity = token_data.get('liquidity', {}).get('usd', 0)
    discovery_timestamp = token_data.get('discovery_timestamp', datetime.now())

    # Check 1: Liquidity validation
    logger.info("  Check 1/3: Validating current liquidity...")
    liquidity_check = validate_current_liquidity(token_address, original_liquidity)
    result['checks']['liquidity'] = liquidity_check

    if liquidity_check['should_abort']:
        result['abort_reasons'].append(f"Liquidity check failed: {liquidity_check.get('error', 'Critical drop')}")
        result['should_abort'] = True

    result['warnings'].extend(liquidity_check['warnings'])
    if liquidity_check['error']:
        result['errors'].append(liquidity_check['error'])

    # Check 2: Data staleness
    logger.info("  Check 2/3: Checking data staleness...")
    staleness_check = check_data_staleness(discovery_timestamp)
    result['checks']['staleness'] = staleness_check

    if staleness_check['should_abort']:
        result['abort_reasons'].append(f"Data too stale: {staleness_check['warning']}")
        result['should_abort'] = True

    if staleness_check['warning']:
        result['warnings'].append(staleness_check['warning'])

    # Check 3: Pool reserves
    logger.info("  Check 3/3: Validating pool reserves...")
    pair_address = token_data.get('pairAddress')

    if pair_address:
        reserves_check = validate_pool_reserves(pair_address, w3)
        result['checks']['reserves'] = reserves_check

        if reserves_check['should_abort']:
            result['abort_reasons'].append("Reserve imbalance detected")
            result['should_abort'] = True

        result['warnings'].extend(reserves_check['warnings'])
    else:
        result['warnings'].append("No pair address provided, skipping reserve check")

    # Determine overall validity
    if not result['should_abort'] and not result['errors']:
        result['is_valid'] = True

    # Log summary
    if result['is_valid']:
        logger.info("✅ Pre-execution validation PASSED")
    else:
        logger.warning(f"❌ Pre-execution validation FAILED: {'; '.join(result['abort_reasons'])}")

    return result


def compare_liquidity_changes(
    original_liquidity: float,
    current_liquidity: float
) -> Dict:
    """
    Compare liquidity changes and categorize severity

    Args:
        original_liquidity: Original liquidity value
        current_liquidity: Current liquidity value

    Returns:
        {
            'change_percent': float,
            'change_usd': float,
            'severity': str ('normal', 'warning', 'critical'),
            'description': str
        }
    """
    change_usd = current_liquidity - original_liquidity
    change_percent = (change_usd / original_liquidity * 100) if original_liquidity > 0 else 0

    # Determine severity
    if abs(change_percent) < LIQUIDITY_DROP_WARNING_PERCENT:
        severity = 'normal'
        description = 'Normal liquidity fluctuation'
    elif abs(change_percent) < CRITICAL_LIQUIDITY_DROP_PERCENT:
        severity = 'warning'
        description = 'Moderate liquidity change - proceed with caution'
    else:
        severity = 'critical'
        description = 'Critical liquidity change - possible rugpull'

    return {
        'change_percent': change_percent,
        'change_usd': change_usd,
        'severity': severity,
        'description': description
    }


# =============================================================================
# Testing and Validation
# =============================================================================

if __name__ == "__main__":
    print("Pre-Execution Validation Module Test")
    print("=" * 60)

    # Test 1: Data staleness check
    print("\nTest 1: Data Staleness Check")
    old_timestamp = datetime.now() - timedelta(minutes=10)
    staleness = check_data_staleness(old_timestamp)
    print(f"  Age: {staleness['age_seconds']:.0f}s, Stale: {staleness['is_stale']}")

    # Test 2: Liquidity change comparison
    print("\nTest 2: Liquidity Change Comparison")
    comparison = compare_liquidity_changes(100000, 45000)
    print(f"  Change: {comparison['change_percent']:.1f}% - Severity: {comparison['severity']}")
    print(f"  Description: {comparison['description']}")

    print("\n" + "=" * 60)
    print("✅ Pre-execution validation module loaded successfully")
