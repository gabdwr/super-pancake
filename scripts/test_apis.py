#!/usr/bin/env python3
"""
Test all API connections before starting development

This script tests:
1. DexScreener API (no auth)
2. GoPlus Security API (no auth)
3. Moralis API (requires key)
4. Alchemy BSC RPC (requires key)

Usage:
    python scripts/test_apis.py
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def test_dexscreener():
    """Test DexScreener API (no auth required)"""
    print("=" * 60)
    print("Testing DexScreener API")
    print("=" * 60)

    try:
        # Test with WBNB address
        url = "https://api.dexscreener.com/latest/dex/tokens/0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            pairs = data.get('pairs', [])
            print(f"✅ DexScreener API working! Found {len(pairs)} trading pairs for WBNB")
            if pairs:
                print(f"   Sample: {pairs[0].get('baseToken', {}).get('name')} on {pairs[0].get('dexId')}")
            return True
        else:
            print(f"❌ DexScreener API failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ DexScreener API error: {e}")
        return False

def test_goplus():
    """Test GoPlus Security API (no auth required)"""
    print("\n" + "=" * 60)
    print("Testing GoPlus Security API")
    print("=" * 60)

    try:
        # Test with WBNB on BSC
        url = "https://api.gopluslabs.io/api/v1/token_security/56"
        params = {"contract_addresses": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 1:
                print("✅ GoPlus API working! Security analysis received")
                result = list(data.get('result', {}).values())[0] if data.get('result') else {}
                if result:
                    print(f"   Token: {result.get('token_name')} ({result.get('token_symbol')})")
                    print(f"   Is Honeypot: {result.get('is_honeypot', 'N/A')}")
                    print(f"   Holder Count: {result.get('holder_count', 'N/A')}")
                return True
            else:
                print(f"❌ GoPlus API returned error code: {data.get('code')}")
                return False
        elif response.status_code == 429:
            print("⚠️  Rate limit exceeded (30/min) - API is working but too many requests")
            return True
        else:
            print(f"❌ GoPlus API failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ GoPlus API error: {e}")
        return False

def test_moralis():
    """Test Moralis API (requires key)"""
    print("\n" + "=" * 60)
    print("Testing Moralis API")
    print("=" * 60)

    api_key = os.getenv('MORALIS_API_KEY')
    if not api_key:
        print("❌ MORALIS_API_KEY not found in .env file")
        return False

    print(f"API Key found: {api_key[:20]}...")

    try:
        # Test with simple ERC20 price endpoint
        url = "https://deep-index.moralis.io/api/v2/erc20/0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c/price"
        headers = {"X-API-Key": api_key}
        params = {"chain": "bsc"}

        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print("✅ Moralis API working!")
            print(f"   WBNB Price: ${data.get('usdPrice', 'N/A')}")
            return True
        elif response.status_code == 401:
            print("❌ Moralis API authentication failed - check your API key")
            return False
        else:
            print(f"❌ Moralis API failed: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Moralis API error: {e}")
        return False

def test_alchemy():
    """Test Alchemy BSC RPC (requires key)"""
    print("\n" + "=" * 60)
    print("Testing Alchemy BSC RPC")
    print("=" * 60)

    rpc_url = os.getenv('ALCHEMY_BSC_RPC')
    if not rpc_url:
        print("❌ ALCHEMY_BSC_RPC not found in .env file")
        return False

    print(f"RPC URL: {rpc_url[:50]}...")

    try:
        # Test with JSON-RPC eth_blockNumber call
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }

        response = requests.post(rpc_url, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if 'result' in data:
                block_hex = data['result']
                block_number = int(block_hex, 16)
                print("✅ Alchemy BSC RPC working!")
                print(f"   Current BSC Block: {block_number:,}")
                return True
            else:
                print(f"❌ Alchemy RPC error: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Alchemy RPC failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Alchemy RPC error: {e}")
        return False

def main():
    """Run all API tests"""
    print("\n" + "🥞" * 30)
    print("SUPER PANCAKE - API CONNECTION TEST")
    print("🥞" * 30 + "\n")

    results = {
        "DexScreener": test_dexscreener(),
        "GoPlus": test_goplus(),
        "Moralis": test_moralis(),
        "Alchemy": test_alchemy()
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for api, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{api:20s} {status}")

    all_passed = all(results.values())

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL APIs WORKING! You're ready to start building!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start with Phase 2: Token Discovery")
        print("3. Read TASK_LIST.md → Phase 2.1")
    else:
        print("⚠️  Some APIs failed. Please fix the issues above before proceeding.")
        print("\nTroubleshooting:")
        if not results["Moralis"]:
            print("- Check MORALIS_API_KEY in .env file")
        if not results["Alchemy"]:
            print("- Check ALCHEMY_BSC_RPC in .env file")

    print("=" * 60 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
