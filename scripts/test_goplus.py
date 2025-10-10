#!/usr/bin/env python3
"""
Test script for GoPlus Security API (no authentication required)

This script verifies that the GoPlus API works without any API key.
Free tier provides 30 calls/minute (43,200/day) with no authentication.

Usage:
    python scripts/test_goplus.py
"""

import requests
import json


def test_goplus_api():
    """
    Test GoPlus Security API with WBNB (known safe token) on BSC
    """
    print("=" * 60)
    print("GoPlus Security API Test (No Authentication)")
    print("=" * 60)
    print()

    # Test parameters
    chain_id = "56"  # BSC (Binance Smart Chain)
    test_address = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"  # WBNB

    # API endpoint - NO API KEY REQUIRED!
    url = f"https://api.gopluslabs.io/api/v1/token_security/{chain_id}"
    params = {"contract_addresses": test_address}

    print(f"Testing token: WBNB (Wrapped BNB)")
    print(f"Chain: BSC (chain_id={chain_id})")
    print(f"Address: {test_address}")
    print(f"API URL: {url}")
    print()
    print("Making API call (no authentication)...")

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            print("✅ SUCCESS! GoPlus API is working!")
            print()
            print("-" * 60)
            print("API Response:")
            print("-" * 60)

            data = response.json()

            # Pretty print the response
            print(json.dumps(data, indent=2))
            print()

            # Parse and display key security info
            if data.get("code") == 1 and data.get("result"):
                result = data["result"].get(test_address.lower(), {})

                print("-" * 60)
                print("Security Analysis Summary:")
                print("-" * 60)
                print(f"Token Name: {result.get('token_name', 'N/A')}")
                print(f"Token Symbol: {result.get('token_symbol', 'N/A')}")
                print(f"Holder Count: {result.get('holder_count', 'N/A')}")
                print(f"Total Supply: {result.get('total_supply', 'N/A')}")
                print()
                print("Security Checks:")
                print(f"  - Is Open Source: {result.get('is_open_source', 'N/A')}")
                print(f"  - Is Proxy: {result.get('is_proxy', 'N/A')}")
                print(f"  - Is Mintable: {result.get('is_mintable', 'N/A')}")
                print(f"  - Can Take Back Ownership: {result.get('can_take_back_ownership', 'N/A')}")
                print(f"  - Is Honeypot: {result.get('is_honeypot', 'N/A')}")
                print(f"  - Buy Tax: {result.get('buy_tax', 'N/A')}")
                print(f"  - Sell Tax: {result.get('sell_tax', 'N/A')}")
                print()

            print("-" * 60)
            print("Rate Limit Info:")
            print("-" * 60)
            print("Free Tier: 30 calls/minute")
            print("Daily Limit: 43,200 calls/day")
            print("No API key required!")
            print()
            print("✅ GoPlus API is ready to use in your bot!")

        elif response.status_code == 429:
            print("⚠️  Rate limit exceeded (30 calls/minute)")
            print("Wait 60 seconds and try again")

        elif response.status_code == 401:
            print("❌ Authentication error")
            print("This shouldn't happen - GoPlus free tier doesn't require auth!")

        else:
            print(f"❌ API returned error code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        print("Check your internet connection or try again")

    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
        print("Check your internet connection")

    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    test_goplus_api()
