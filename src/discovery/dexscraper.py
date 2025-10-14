"""
DexScreener API Integration
Discover new tokens on BSC via DexScreener with advanced liquidity filtering
"""

import requests
from typing import List, Dict
import logging
from time import time, sleep
from datetime import datetime
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Dexscraper:
    """
    Interface to DexScreener API for token discovery

    Endpoints:
    - Token Profiles: Latest tokens with profiles
    - Search: Search for pairs by query
    - Token Pairs: Get pairs for specific token address

    Rate Limits:
    - 300 requests/minute for token/pair endpoints
    - 60 requests/minute for profiles
    """

    def __init__(self):
        self.api_token_profiles_latest = "https://api.dexscreener.com/token-profiles/latest/v1"
        self.target_chains = ['bsc', 'base', 'arbitrum', 'optimism']

        # Rate limiting: Track API call timestamps
        # DexScreener limits: 60/min for profiles, 300/min for token endpoints
        self.profile_calls = deque(maxlen=60)  # Last 60 profile API calls
        self.token_calls = deque(maxlen=300)   # Last 300 token API calls

    def _rate_limit_profiles(self):
        """
        Enforce rate limit for profile endpoint (60 requests/minute).
        Sleeps if necessary to stay under limit.
        """
        current_time = time()

        # Remove calls older than 60 seconds
        while self.profile_calls and current_time - self.profile_calls[0] > 60:
            self.profile_calls.popleft()

        # If at limit, wait until oldest call is 60+ seconds old
        if len(self.profile_calls) >= 60:
            sleep_time = 60 - (current_time - self.profile_calls[0])
            if sleep_time > 0:
                logger.warning(f"⏳ Rate limit: Sleeping {sleep_time:.1f}s for profile endpoint")
                sleep(sleep_time)
                self.profile_calls.popleft()

        # Record this call
        self.profile_calls.append(time())

    def _rate_limit_tokens(self):
        """
        Enforce rate limit for token endpoint (300 requests/minute).
        Sleeps if necessary to stay under limit.
        """
        current_time = time()

        # Remove calls older than 60 seconds
        while self.token_calls and current_time - self.token_calls[0] > 60:
            self.token_calls.popleft()

        # If at limit, wait until oldest call is 60+ seconds old
        if len(self.token_calls) >= 300:
            sleep_time = 60 - (current_time - self.token_calls[0])
            if sleep_time > 0:
                logger.warning(f"⏳ Rate limit: Sleeping {sleep_time:.1f}s for token endpoint")
                sleep(sleep_time)
                self.token_calls.popleft()

        # Record this call
        self.token_calls.append(time())

    def extract_token_info(self, coin: Dict) -> Dict:
        """
        Extract relevant token information from latest coin data

        Args:
            latest_coin: Data around the latest coins added to dexscreener

        Returns:
            Dict with cleaned token data
        """
        chain_id = coin.get('chainId')
        url = coin.get('url')
        token_address = coin.get('tokenAddress')

        if chain_id in self.target_chains:
            return {
                'chain_id': chain_id,
                'address': token_address,
                'dexscreener_url': url,
                'discovered_at': time(),
                'discovered_at_readable': datetime.now().isoformat()
            }

    def scrape_latest_tokens(self) -> List[Dict]:
        """
        Scrape the 30 latest tokens from dexscreener every minute

        Returns:
            List of token profile data
        """
        try:
            # Rate limit: 60 requests/minute for profiles
            self._rate_limit_profiles()

            response = requests.get(
                self.api_token_profiles_latest,
                headers={"Accept": "*/*"},
                timeout=30
            )

            if response.status_code == 200:
                self.token_profiles_data = response.json()
            else:
                logger.error(f"Error getting profiles: HTTP {response.status_code}")
                return []

            # Clean up response
            cleaned_up_response = []
            for coin in self.token_profiles_data:
                coin_extracted = self.extract_token_info(coin)
                if coin_extracted:
                    cleaned_up_response.append(coin_extracted)

            return cleaned_up_response

        except Exception as e:
            logger.error(f"Error scraping tokens: {e}")
            return []

    def fetch_token_metrics(self, token_address: str) -> Dict:
        """
        Fetch all metrics for a token from DexScreener API.
        Returns price, liquidity, volume, trading data across multiple timeframes.
        """
        # Rate limit: 300 requests/minute for token endpoints
        self._rate_limit_tokens()

        url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            logger.warning(f"Failed to fetch metrics for {token_address}: HTTP {response.status_code}")
            return None

        data = response.json()
        pairs = data.get('pairs', [])

        if not pairs:
            logger.warning(f"No pairs found for {token_address}")
            return None

        # Get main pair (highest liquidity)
        main_pair = max(pairs, key=lambda p: p.get('liquidity', {}).get('usd', 0))

        # Sum all liquidity
        total_liquidity = sum(p.get('liquidity', {}).get('usd', 0) for p in pairs)

        # Extract volume data for all timeframes
        volume = main_pair.get('volume', {})

        # Extract price change data for all timeframes
        price_change = main_pair.get('priceChange', {})

        # Extract transaction data for all timeframes
        txns = main_pair.get('txns', {})

        # Extract pair creation timestamp (Unix milliseconds -> datetime)
        pair_created_at = main_pair.get('pairCreatedAt')
        if pair_created_at:
            pair_created_at = datetime.fromtimestamp(pair_created_at / 1000).isoformat()

        return {
            # Basic price & liquidity
            'price_usd': float(main_pair.get('priceUsd', 0)),
            'liquidity_usd': total_liquidity,
            'pair_count': len(pairs),

            # Market valuation
            'fdv': main_pair.get('fdv'),
            'market_cap': main_pair.get('marketCap'),

            # Volume - multi-timeframe
            'volume_24h': volume.get('h24', 0),
            'volume_h6': volume.get('h6', 0),
            'volume_h1': volume.get('h1', 0),
            'volume_m5': volume.get('m5', 0),

            # Price changes - multi-timeframe
            'price_change_24h': price_change.get('h24', 0),
            'price_change_h6': price_change.get('h6', 0),
            'price_change_h1': price_change.get('h1', 0),
            'price_change_m5': price_change.get('m5', 0),

            # Transactions - 24h
            'buys_24h': txns.get('h24', {}).get('buys', 0),
            'sells_24h': txns.get('h24', {}).get('sells', 0),

            # Transactions - 6h
            'buys_h6': txns.get('h6', {}).get('buys', 0),
            'sells_h6': txns.get('h6', {}).get('sells', 0),

            # Transactions - 1h
            'buys_h1': txns.get('h1', {}).get('buys', 0),
            'sells_h1': txns.get('h1', {}).get('sells', 0),

            # Transactions - 5m
            'buys_m5': txns.get('m5', {}).get('buys', 0),
            'sells_m5': txns.get('m5', {}).get('sells', 0),

            # Pair info
            'main_dex': main_pair.get('dexId'),
            'pair_address': main_pair.get('pairAddress'),
            'base_token_symbol': main_pair.get('baseToken', {}).get('symbol'),
            'quote_token_symbol': main_pair.get('quoteToken', {}).get('symbol'),
            'pair_created_at': pair_created_at,

            # Raw pairs data (needed for concentration score calculation)
            'pairs': pairs
        }

    @property
    def scraped(self):
        """Main function for running a scrape job"""
        logger.info("Scraping DexScreener latest tokens...")
        logger.info("-" * 70)
        self.scraped_tokens = self.scrape_latest_tokens()
        logger.debug(f"Scraped tokens: {self.scraped_tokens}")
        logger.info(f"Tokens scraped: {len(self.scraped_tokens)}/30 were relevant to target chains")
        logger.info("=" * 70)
        return self.scraped_tokens