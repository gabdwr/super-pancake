"""
DexScreener API Integration
Discover new tokens on BSC via DexScreener with advanced liquidity filtering
"""

import requests
from typing import List, Dict
import logging
from time import time
from datetime import datetime

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