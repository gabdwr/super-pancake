"""
Contract ABIs for BSC/PancakeSwap Interaction

Contains minimal ABIs for:
- PancakeSwap V2 Router
- Uniswap V2 Pair (compatible with PancakeSwap)
- ERC20 Token Standard
"""

from web3 import Web3
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# PancakeSwap V2 Router ABI (Key Functions Only)
# =============================================================================

ROUTER_ABI = [
    # Get amounts out (price quote)
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"}
        ],
        "name": "getAmountsOut",
        "outputs": [
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    # Swap exact ETH for tokens
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": [
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "stateMutability": "payable",
        "type": "function"
    },
    # Swap exact ETH for tokens supporting fee-on-transfer
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokensSupportingFeeOnTransferTokens",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    # Swap exact tokens for ETH
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForETH",
        "outputs": [
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    # Swap exact tokens for ETH supporting fee-on-transfer
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForETHSupportingFeeOnTransferTokens",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    # Factory address
    {
        "inputs": [],
        "name": "factory",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    # WETH address
    {
        "inputs": [],
        "name": "WETH",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# =============================================================================
# Uniswap V2 Pair ABI (Compatible with PancakeSwap Pairs)
# =============================================================================

PAIR_ABI = [
    # Get reserves
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "blockTimestampLast", "type": "uint32"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    # Token0 address
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    # Token1 address
    {
        "constant": True,
        "inputs": [],
        "name": "token1",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    # Total supply (LP tokens)
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    # Get price cumulative last
    {
        "constant": True,
        "inputs": [],
        "name": "price0CumulativeLast",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "price1CumulativeLast",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# =============================================================================
# ERC20 Token ABI (Standard Functions)
# =============================================================================

ERC20_ABI = [
    # Balance of
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    # Total supply
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    # Decimals
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    # Symbol
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    # Name
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    # Allowance
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    # Approve
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    # Transfer
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

# =============================================================================
# Helper Functions
# =============================================================================

def get_router_contract(w3: Web3, router_address: str):
    """
    Get PancakeSwap Router contract instance

    Args:
        w3: Web3 instance
        router_address: Router contract address

    Returns:
        Contract instance
    """
    try:
        checksum_address = Web3.to_checksum_address(router_address)
        contract = w3.eth.contract(address=checksum_address, abi=ROUTER_ABI)
        return contract
    except Exception as e:
        logger.error(f"Error creating router contract: {e}")
        raise


def get_pair_contract(w3: Web3, pair_address: str):
    """
    Get Pair contract instance

    Args:
        w3: Web3 instance
        pair_address: Pair contract address

    Returns:
        Contract instance
    """
    try:
        checksum_address = Web3.to_checksum_address(pair_address)
        contract = w3.eth.contract(address=checksum_address, abi=PAIR_ABI)
        return contract
    except Exception as e:
        logger.error(f"Error creating pair contract: {e}")
        raise


def get_token_contract(w3: Web3, token_address: str):
    """
    Get ERC20 Token contract instance

    Args:
        w3: Web3 instance
        token_address: Token contract address

    Returns:
        Contract instance
    """
    try:
        checksum_address = Web3.to_checksum_address(token_address)
        contract = w3.eth.contract(address=checksum_address, abi=ERC20_ABI)
        return contract
    except Exception as e:
        logger.error(f"Error creating token contract: {e}")
        raise


def validate_contract_abi(w3: Web3, address: str, abi: list, function_name: str) -> bool:
    """
    Validate that a contract has a specific function

    Args:
        w3: Web3 instance
        address: Contract address
        abi: Contract ABI
        function_name: Function name to check

    Returns:
        True if function exists, False otherwise
    """
    try:
        checksum_address = Web3.to_checksum_address(address)
        contract = w3.eth.contract(address=checksum_address, abi=abi)

        # Check if function exists
        if hasattr(contract.functions, function_name):
            return True
        return False
    except Exception as e:
        logger.error(f"Error validating contract ABI: {e}")
        return False


# =============================================================================
# ABI Exports for Easy Import
# =============================================================================

__all__ = [
    'ROUTER_ABI',
    'PAIR_ABI',
    'ERC20_ABI',
    'get_router_contract',
    'get_pair_contract',
    'get_token_contract',
    'validate_contract_abi'
]


# =============================================================================
# Test/Validation
# =============================================================================

if __name__ == "__main__":
    print("Contract ABIs Test")
    print("=" * 60)
    print(f"Router ABI functions: {len(ROUTER_ABI)}")
    print(f"Pair ABI functions: {len(PAIR_ABI)}")
    print(f"ERC20 ABI functions: {len(ERC20_ABI)}")
    print("=" * 60)

    # List all router functions
    print("\nRouter Functions:")
    for func in ROUTER_ABI:
        print(f"  - {func.get('name', 'constructor')}")

    print("\nPair Functions:")
    for func in PAIR_ABI:
        print(f"  - {func.get('name', 'N/A')}")

    print("\nERC20 Functions:")
    for func in ERC20_ABI:
        print(f"  - {func.get('name', 'N/A')}")

    print("\n✅ ABIs loaded successfully")
