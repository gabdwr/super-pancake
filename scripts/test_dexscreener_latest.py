#!/usr/bin/env python3
"""
Test script to get latest tokens from DexScreener

DexScreener doesn't have a direct "get latest tokens" endpoint, but we can:
1. Search for recent pairs on BSC
2. Use the search endpoint with common terms
3. Filter results by pairCreatedAt timestamp
"""

import requests
from datetime import datetime, timedelta
import json


def get_latest_pairs_search(query="", limit=50):
    """
    Get pairs using search endpoint

    Note: DexScreener doesn't have a "latest pairs" endpoint,
    so we search and filter by creation date
    """
    url = "https://api.dexscreener.com/latest/dex/search"

    # If no query, search for BNB (common on BSC)
    params = {"q": query or "BNB"}

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            pairs = data.get('pairs', [])

            # Filter for BSC only
            bsc_pairs = [p for p in pairs if p.get('chainId') == 'bsc']

            # Sort by creation date (newest first)
            bsc_pairs.sort(key=lambda x: x.get('pairCreatedAt', 0), reverse=True)

            return bsc_pairs[:limit]
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return []

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def get_token_info(token_address):
    """
    Get detailed info for a specific token on BSC
    """
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return data.get('pairs', [])
        else:
            return []

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def display_pair_info(pair, index=1):
    """Pretty print pair information"""

    # Calculate age
    created_at = pair.get('pairCreatedAt', 0)
    if created_at:
        created_date = datetime.fromtimestamp(created_at / 1000)  # Convert from ms
        age_days = (datetime.now() - created_date).days
        age_str = f"{age_days} days old"
    else:
        age_str = "Unknown age"

    # Extract data
    base_token = pair.get('baseToken', {})
    quote_token = pair.get('quoteToken', {})
    price_usd = pair.get('priceUsd', 'N/A')
    liquidity_usd = pair.get('liquidity', {}).get('usd', 0)
    volume_24h = pair.get('volume', {}).get('h24', 0)
    market_cap = pair.get('marketCap', 0)

    print(f"\n{'='*60}")
    print(f"#{index} - {base_token.get('name', 'Unknown')} ({base_token.get('symbol', 'N/A')})")
    print(f"{'='*60}")
    print(f"Address:     {base_token.get('address', 'N/A')}")
    print(f"Pair:        {base_token.get('symbol')}/{quote_token.get('symbol')}")
    print(f"DEX:         {pair.get('dexId', 'N/A').upper()}")
    print(f"Age:         {age_str}")
    print(f"Price:       ${price_usd}")
    print(f"Liquidity:   ${liquidity_usd:,.2f}" if liquidity_usd else "Liquidity:   N/A")
    print(f"Volume 24h:  ${volume_24h:,.2f}" if volume_24h else "Volume 24h:  N/A")
    print(f"Market Cap:  ${market_cap:,.2f}" if market_cap else "Market Cap:  N/A")
    print(f"Pair URL:    {pair.get('url', 'N/A')}")


def main():
    print("🥞 DexScreener - Latest BSC Tokens Test")
    print("=" * 60)
    print()

    print("Searching for recent BSC pairs...")
    print("(Note: DexScreener search is limited, not a true 'latest' endpoint)")
    print()

    # Try searching with different queries to find newer tokens
    queries = ["BNB", "USDT", "BUSD"]
    all_pairs = []

    for query in queries:
        print(f"Searching: {query}...")
        pairs = get_latest_pairs_search(query, limit=20)
        all_pairs.extend(pairs)

    # Remove duplicates by pair address
    unique_pairs = {}
    for pair in all_pairs:
        pair_addr = pair.get('pairAddress')
        if pair_addr and pair_addr not in unique_pairs:
            unique_pairs[pair_addr] = pair

    # Sort by creation date
    sorted_pairs = sorted(
        unique_pairs.values(),
        key=lambda x: x.get('pairCreatedAt', 0),
        reverse=True
    )

    # Show top 10 newest
    print(f"\n✅ Found {len(sorted_pairs)} unique BSC pairs")
    print(f"Showing top 10 newest pairs:")

    for i, pair in enumerate(sorted_pairs[:10], 1):
        display_pair_info(pair, i)

    print("\n" + "=" * 60)
    print("📝 Notes:")
    print("- DexScreener doesn't have a dedicated 'latest tokens' API")
    print("- To find new tokens systematically, you need to:")
    print("  1. Monitor blockchain events (pair creation)")
    print("  2. Use DexScreener web scraping")
    print("  3. Use third-party services (Moralis, Bitquery)")
    print("  4. Search repeatedly and filter by creation date")
    print("=" * 60)


if __name__ == "__main__":
    main()
