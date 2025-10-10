"""
Execution Helper Functions

Utility functions for trade execution:
- Price quotes from router
- Gas estimation
- Deadline calculation
- Transaction parameter validation
- Display formatting

These helpers bridge the gap between validation and actual execution.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from web3 import Web3
from decimal import Decimal

from config.constants import (
    TX_DEADLINE_SECONDS,
    MAX_GAS_PRICE_GWEI,
    DEFAULT_GAS_LIMIT,
    GAS_ESTIMATE_BUFFER,
    WBNB_ADDRESS,
    PANCAKESWAP_ROUTER_V2
)
from config.contract_abis import get_router_contract, get_token_contract

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_current_price(
    token_address: str,
    amount_in_bnb: float,
    w3: Web3,
    router_address: str = PANCAKESWAP_ROUTER_V2
) -> Dict:
    """
    Get current price quote from PancakeSwap router

    Calls router.getAmountsOut() to get expected output tokens for a given BNB input.

    Args:
        token_address: Token contract address
        amount_in_bnb: Amount of BNB to trade
        w3: Web3 instance
        router_address: Router contract address

    Returns:
        {
            'expected_tokens': float,
            'price_per_token_bnb': float,
            'path': List[str],
            'is_valid': bool,
            'error': str or None
        }
    """
    result = {
        'expected_tokens': 0,
        'price_per_token_bnb': 0,
        'path': [],
        'is_valid': False,
        'error': None
    }

    try:
        # Get router contract
        router = get_router_contract(w3, router_address)

        # Convert BNB amount to Wei
        amount_in_wei = Web3.to_wei(amount_in_bnb, 'ether')

        # Setup path: BNB -> Token
        path = [
            Web3.to_checksum_address(WBNB_ADDRESS),
            Web3.to_checksum_address(token_address)
        ]
        result['path'] = path

        # Get amounts out
        amounts = router.functions.getAmountsOut(
            amount_in_wei,
            path
        ).call()

        # Parse result
        expected_tokens_wei = amounts[1]  # Output token amount
        expected_tokens = expected_tokens_wei / 1e18  # Convert from Wei

        result['expected_tokens'] = expected_tokens

        # Calculate price per token
        if expected_tokens > 0:
            result['price_per_token_bnb'] = amount_in_bnb / expected_tokens

        result['is_valid'] = True

        logger.info(f"Price quote: {amount_in_bnb} BNB -> {expected_tokens:.2f} tokens")

    except Exception as e:
        result['error'] = f"Failed to get price quote: {e}"
        logger.error(result['error'])

    return result


def calculate_deadline(seconds_from_now: int = TX_DEADLINE_SECONDS) -> int:
    """
    Calculate transaction deadline timestamp

    PancakeSwap router requires a deadline parameter to prevent
    transactions from being executed too late.

    Args:
        seconds_from_now: Seconds from now for deadline

    Returns:
        Unix timestamp deadline
    """
    deadline = int(time.time()) + seconds_from_now
    return deadline


def estimate_gas_for_swap(
    router_contract,
    swap_function_name: str,
    swap_params: Dict,
    from_address: str
) -> Dict:
    """
    Estimate gas required for swap transaction

    Args:
        router_contract: Router contract instance
        swap_function_name: Function name ('swapExactETHForTokens', etc.)
        swap_params: Parameters for swap function
        from_address: Sender address

    Returns:
        {
            'estimated_gas': int,
            'gas_with_buffer': int,
            'estimated_cost_bnb': float,
            'is_valid': bool,
            'error': str or None
        }
    """
    result = {
        'estimated_gas': 0,
        'gas_with_buffer': 0,
        'estimated_cost_bnb': 0,
        'is_valid': False,
        'error': None
    }

    try:
        # Get swap function
        swap_function = getattr(router_contract.functions, swap_function_name)

        # Estimate gas
        estimated_gas = swap_function(**swap_params).estimate_gas({
            'from': from_address,
            'value': swap_params.get('value', 0)
        })

        result['estimated_gas'] = estimated_gas

        # Add buffer
        gas_with_buffer = int(estimated_gas * GAS_ESTIMATE_BUFFER)
        result['gas_with_buffer'] = gas_with_buffer

        # Get current gas price
        w3 = router_contract.w3
        gas_price_wei = w3.eth.gas_price

        # Calculate cost
        cost_wei = gas_with_buffer * gas_price_wei
        cost_bnb = Web3.from_wei(cost_wei, 'ether')
        result['estimated_cost_bnb'] = float(cost_bnb)

        result['is_valid'] = True

        logger.info(f"Gas estimate: {gas_with_buffer:,} units (cost: {cost_bnb:.6f} BNB)")

    except Exception as e:
        # If estimation fails, use default
        result['estimated_gas'] = DEFAULT_GAS_LIMIT
        result['gas_with_buffer'] = DEFAULT_GAS_LIMIT
        result['error'] = f"Gas estimation failed, using default: {e}"
        logger.warning(result['error'])

    return result


def validate_transaction_params(tx_params: Dict) -> Tuple[bool, List[str]]:
    """
    Validate transaction parameters before submission

    Args:
        tx_params: Transaction parameters dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check required fields
    required_fields = ['from', 'to']
    for field in required_fields:
        if field not in tx_params:
            errors.append(f"Missing required field: {field}")

    # Validate gas price
    if 'gasPrice' in tx_params:
        gas_price_gwei = Web3.from_wei(tx_params['gasPrice'], 'gwei')
        if gas_price_gwei > MAX_GAS_PRICE_GWEI:
            errors.append(f"Gas price {gas_price_gwei:.2f} Gwei exceeds maximum {MAX_GAS_PRICE_GWEI} Gwei")

    # Validate gas limit
    if 'gas' in tx_params:
        if tx_params['gas'] > 5_000_000:  # Unreasonably high
            errors.append(f"Gas limit {tx_params['gas']:,} seems too high")
        elif tx_params['gas'] < 21_000:  # Minimum for any transaction
            errors.append(f"Gas limit {tx_params['gas']:,} too low")

    # Validate value (if present)
    if 'value' in tx_params:
        if tx_params['value'] < 0:
            errors.append("Transaction value cannot be negative")

    # Validate addresses
    for field in ['from', 'to']:
        if field in tx_params:
            try:
                Web3.to_checksum_address(tx_params[field])
            except Exception:
                errors.append(f"Invalid address format for {field}: {tx_params[field]}")

    is_valid = len(errors) == 0
    return is_valid, errors


def format_slippage_for_display(slippage_decimal: float) -> str:
    """
    Format slippage percentage for display

    Args:
        slippage_decimal: Slippage as decimal (e.g., 0.02 for 2%)

    Returns:
        Formatted string (e.g., "2.00%")
    """
    return f"{slippage_decimal * 100:.2f}%"


def format_token_amount(amount: float, decimals: int = 18) -> str:
    """
    Format token amount for display

    Args:
        amount: Token amount
        decimals: Token decimals

    Returns:
        Formatted string with appropriate precision
    """
    if amount >= 1_000_000:
        return f"{amount/1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"{amount/1_000:.2f}K"
    elif amount >= 1:
        return f"{amount:.2f}"
    else:
        return f"{amount:.6f}"


def format_bnb_amount(amount_bnb: float) -> str:
    """
    Format BNB amount for display

    Args:
        amount_bnb: Amount in BNB

    Returns:
        Formatted string
    """
    return f"{amount_bnb:.4f} BNB"


def format_usd_amount(amount_usd: float) -> str:
    """
    Format USD amount for display

    Args:
        amount_usd: Amount in USD

    Returns:
        Formatted string
    """
    if amount_usd >= 1_000_000:
        return f"${amount_usd/1_000_000:.2f}M"
    elif amount_usd >= 1_000:
        return f"${amount_usd/1_000:.2f}K"
    else:
        return f"${amount_usd:.2f}"


def get_token_decimals(token_address: str, w3: Web3) -> int:
    """
    Get token decimals from contract

    Args:
        token_address: Token contract address
        w3: Web3 instance

    Returns:
        Token decimals (default 18 if query fails)
    """
    try:
        token_contract = get_token_contract(w3, token_address)
        decimals = token_contract.functions.decimals().call()
        return decimals
    except Exception as e:
        logger.warning(f"Failed to get token decimals, using default 18: {e}")
        return 18


def prepare_swap_params(
    amount_out_min: int,
    path: List[str],
    to_address: str,
    deadline: Optional[int] = None,
    value_wei: Optional[int] = None
) -> Dict:
    """
    Prepare parameters for PancakeSwap swap functions

    Args:
        amount_out_min: Minimum output tokens (Wei)
        path: Token path [WBNB, Token]
        to_address: Recipient address
        deadline: Transaction deadline (calculated if None)
        value_wei: Value to send (for ETH swaps)

    Returns:
        Dictionary of parameters for swap function
    """
    if deadline is None:
        deadline = calculate_deadline()

    params = {
        'amountOutMin': amount_out_min,
        'path': path,
        'to': Web3.to_checksum_address(to_address),
        'deadline': deadline
    }

    if value_wei is not None:
        params['value'] = value_wei

    return params


def calculate_price_from_reserves(
    reserve_in: int,
    reserve_out: int,
    decimals_in: int = 18,
    decimals_out: int = 18
) -> float:
    """
    Calculate price from pool reserves

    Args:
        reserve_in: Reserve of input token
        reserve_out: Reserve of output token
        decimals_in: Decimals of input token
        decimals_out: Decimals of output token

    Returns:
        Price (output per input)
    """
    if reserve_in == 0:
        return 0

    # Convert to human-readable amounts
    reserve_in_readable = reserve_in / (10 ** decimals_in)
    reserve_out_readable = reserve_out / (10 ** decimals_out)

    price = reserve_out_readable / reserve_in_readable
    return price


def check_sufficient_balance(
    wallet_address: str,
    required_bnb: float,
    w3: Web3
) -> Tuple[bool, float]:
    """
    Check if wallet has sufficient BNB balance

    Args:
        wallet_address: Wallet address to check
        required_bnb: Required BNB amount
        w3: Web3 instance

    Returns:
        Tuple of (has_sufficient, current_balance)
    """
    try:
        balance_wei = w3.eth.get_balance(Web3.to_checksum_address(wallet_address))
        balance_bnb = Web3.from_wei(balance_wei, 'ether')

        has_sufficient = balance_bnb >= required_bnb

        logger.info(f"Wallet balance: {balance_bnb:.4f} BNB (required: {required_bnb:.4f} BNB)")

        return has_sufficient, float(balance_bnb)

    except Exception as e:
        logger.error(f"Failed to check balance: {e}")
        return False, 0


# =============================================================================
# Testing and Validation
# =============================================================================

if __name__ == "__main__":
    print("Execution Helper Functions Test")
    print("=" * 60)

    # Test 1: Deadline calculation
    print("\nTest 1: Deadline Calculation")
    deadline = calculate_deadline(300)
    print(f"  Current time: {int(time.time())}")
    print(f"  Deadline (+5min): {deadline}")

    # Test 2: Formatting functions
    print("\nTest 2: Formatting Functions")
    print(f"  Token amount: {format_token_amount(1_234_567.89)}")
    print(f"  BNB amount: {format_bnb_amount(0.12345)}")
    print(f"  USD amount: {format_usd_amount(45_678.90)}")
    print(f"  Slippage: {format_slippage_for_display(0.025)}")

    # Test 3: Transaction params validation
    print("\nTest 3: Transaction Params Validation")
    valid_params = {
        'from': '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
        'to': '0x10ED43C718714eb63d5aA57B78B54704E256024E',
        'gas': 300_000,
        'gasPrice': Web3.to_wei(5, 'gwei'),
        'value': Web3.to_wei(0.1, 'ether')
    }
    is_valid, errors = validate_transaction_params(valid_params)
    print(f"  Valid params: {is_valid}")
    if errors:
        for error in errors:
            print(f"    Error: {error}")

    # Test 4: Price from reserves
    print("\nTest 4: Price from Reserves")
    price = calculate_price_from_reserves(
        reserve_in=100 * 1e18,  # 100 BNB
        reserve_out=1_000_000 * 1e18  # 1M tokens
    )
    print(f"  Price: 1 BNB = {price:,.2f} tokens")

    print("\n" + "=" * 60)
    print("✅ Execution helpers module loaded successfully")
