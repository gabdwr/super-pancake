"""
Supabase REST API Client
Alternative to direct PostgreSQL connection for GitHub Actions (IPv4-only environments)
Uses Supabase REST API which works over HTTPS (IPv4 compatible)
"""

import requests
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class SupabaseREST:
    """
    Supabase REST API client for IPv4-only environments like GitHub Actions.
    Uses HTTPS REST API instead of direct PostgreSQL connection.
    """

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")  # e.g., https://xxx.supabase.co
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")  # Public anon key

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables")

        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        self.base_url = f"{self.supabase_url}/rest/v1"

    def store_discovered_tokens(self, tokens_list: List[Dict]) -> Dict:
        """
        Store discovered tokens using Supabase REST API.

        Args:
            tokens_list: List of token dicts with keys:
                        - chain_id (str)
                        - address (str)
                        - dexscreener_url (str)
                        - discovered_at (float, unix timestamp)

        Returns:
            Dict with stats: {'total': int, 'inserted': int, 'skipped': int, 'errors': []}
        """
        if not tokens_list:
            logger.warning("No tokens to store")
            return {'total': 0, 'inserted': 0, 'skipped': 0, 'errors': []}

        stats = {
            'total': len(tokens_list),
            'inserted': 0,
            'skipped': 0,
            'errors': []
        }

        # Convert tokens to Supabase format
        records = []
        for token in tokens_list:
            try:
                discovered_timestamp = datetime.fromtimestamp(token.get('discovered_at', 0)).isoformat()
                records.append({
                    'chain_id': token.get('chain_id'),
                    'token_address': token.get('address'),
                    'dexscreener_url': token.get('dexscreener_url'),
                    'discovered_at': discovered_timestamp
                })
            except Exception as e:
                stats['errors'].append(f"Error formatting token {token.get('address')}: {e}")

        # Use upsert with on_conflict to handle duplicates
        try:
            url = f"{self.base_url}/discovered_tokens?on_conflict=chain_id,token_address"
            headers = self.headers.copy()
            headers['Prefer'] = 'resolution=ignore-duplicates,return=minimal'

            response = requests.post(
                url,
                headers=headers,
                json=records,
                timeout=30
            )

            if response.status_code == 201:
                stats['inserted'] = len(records)
                logger.info(f"✅ Inserted {stats['inserted']} new tokens")
            elif response.status_code == 200:
                stats['inserted'] = len(records)
                logger.info(f"📊 Processed {stats['inserted']} tokens (some may be duplicates)")
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"❌ Failed to insert tokens: {error_msg}")
                stats['errors'].append(error_msg)
                stats['skipped'] = len(records)

        except Exception as e:
            logger.error(f"❌ REST API error: {e}")
            stats['errors'].append(str(e))
            stats['skipped'] = len(records)

        logger.info(f"📊 Storage: {stats['inserted']} inserted, {stats['skipped']} skipped, {len(stats['errors'])} errors")
        return stats

    def store_time_series_data(self, metrics_data: Dict, token_address: str, chain_id: str) -> bool:
        """
        Store time-series data using REST API.

        Args:
            metrics_data: Dict from fetch_token_metrics()
            token_address: Token contract address
            chain_id: Blockchain identifier

        Returns:
            bool: True if successful
        """
        if not metrics_data:
            logger.warning(f"No metrics data for {token_address}")
            return False

        try:
            record = {
                'token_address': token_address,
                'chain_id': chain_id,
                'snapshot_at': datetime.now().isoformat(),

                # Basic price & liquidity
                'price_usd': metrics_data.get('price_usd'),
                'liquidity_usd': metrics_data.get('liquidity_usd'),
                'pair_count': metrics_data.get('pair_count'),

                # Market valuation
                'fdv': metrics_data.get('fdv'),
                'market_cap': metrics_data.get('market_cap'),

                # Volume - multi-timeframe
                'volume_24h': metrics_data.get('volume_24h'),
                'volume_h6': metrics_data.get('volume_h6'),
                'volume_h1': metrics_data.get('volume_h1'),
                'volume_m5': metrics_data.get('volume_m5'),

                # Price changes - multi-timeframe
                'price_change_24h': metrics_data.get('price_change_24h'),
                'price_change_h6': metrics_data.get('price_change_h6'),
                'price_change_h1': metrics_data.get('price_change_h1'),
                'price_change_m5': metrics_data.get('price_change_m5'),

                # Transactions - 24h
                'buys_24h': metrics_data.get('buys_24h'),
                'sells_24h': metrics_data.get('sells_24h'),

                # Transactions - 6h
                'buys_h6': metrics_data.get('buys_h6'),
                'sells_h6': metrics_data.get('sells_h6'),

                # Transactions - 1h
                'buys_h1': metrics_data.get('buys_h1'),
                'sells_h1': metrics_data.get('sells_h1'),

                # Transactions - 5m
                'buys_m5': metrics_data.get('buys_m5'),
                'sells_m5': metrics_data.get('sells_m5'),

                # Pair info
                'main_dex': metrics_data.get('main_dex'),
                'pair_address': metrics_data.get('pair_address'),
                'base_token_symbol': metrics_data.get('base_token_symbol'),
                'quote_token_symbol': metrics_data.get('quote_token_symbol'),
                'pair_created_at': metrics_data.get('pair_created_at'),

                # GoPlus holder data
                'holder_count': metrics_data.get('holder_count'),
                'top_holder_percent': metrics_data.get('top_holder_percent'),
                'lp_holder_count': metrics_data.get('lp_holder_count'),
                'lp_locked_percent': metrics_data.get('lp_locked_percent'),

                # GoPlus security flags
                'is_honeypot': metrics_data.get('is_honeypot'),
                'buy_tax': metrics_data.get('buy_tax'),
                'sell_tax': metrics_data.get('sell_tax'),
                'is_open_source': metrics_data.get('is_open_source'),
                'is_mintable': metrics_data.get('is_mintable'),
                'transfer_pausable': metrics_data.get('transfer_pausable'),
                'can_take_back_ownership': metrics_data.get('can_take_back_ownership'),
                'owner_address': metrics_data.get('owner_address'),

                # Liquidity concentration (future - from analysis)
                'concentration_ratio': metrics_data.get('concentration_ratio'),
                'concentration_score': metrics_data.get('concentration_score'),

                # Filter status (PASS/FAIL at this snapshot)
                'filter_status': metrics_data.get('filter_status'),
                'filter_fail_reasons': metrics_data.get('filter_fail_reasons', [])
            }

            url = f"{self.base_url}/time_series_data"
            headers = self.headers.copy()
            headers['Prefer'] = 'resolution=ignore-duplicates,return=minimal'

            response = requests.post(
                url,
                headers=headers,
                json=record,
                timeout=30
            )

            if response.status_code in [200, 201]:
                logger.debug(f"✅ Stored metrics for {token_address}")
                return True
            else:
                logger.error(f"❌ Failed to store metrics: HTTP {response.status_code}")
                logger.error(f"Response body: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error storing metrics: {e}")
            return False

    def get_all_tokens(self, chain_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all discovered tokens via REST API.

        Args:
            chain_id: Filter by chain (optional)
            limit: Max results (optional)

        Returns:
            List of token dicts
        """
        try:
            url = f"{self.base_url}/discovered_tokens"
            params = {"select": "*", "order": "discovered_at.desc"}

            if chain_id:
                params['chain_id'] = f"eq.{chain_id}"
            if limit:
                params['limit'] = limit

            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                tokens = response.json()
                logger.info(f"📊 Retrieved {len(tokens)} tokens")
                return tokens
            else:
                logger.error(f"❌ Failed to fetch tokens: HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"❌ Error fetching tokens: {e}")
            return []

    def get_cached_goplus_data(self, token_address: str) -> Optional[Dict]:
        """
        Get most recent GoPlus data for a token from time_series_data table.
        Used for graduated tokens to avoid redundant API calls.

        Args:
            token_address: Token contract address

        Returns:
            Dict with cached GoPlus data, or None if not available
        """
        try:
            url = f"{self.base_url}/time_series_data"
            params = {
                "select": "holder_count,top_holder_percent,lp_holder_count,lp_locked_percent,"
                          "is_honeypot,buy_tax,sell_tax,is_open_source,is_mintable,"
                          "transfer_pausable,can_take_back_ownership,owner_address",
                "token_address": f"eq.{token_address}",
                "order": "snapshot_at.desc",
                "limit": 1
            }

            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    logger.debug(f"✅ Retrieved cached GoPlus data for {token_address}")
                    return results[0]
                else:
                    logger.warning(f"⚠️  No cached data found for {token_address}")
                    return None
            else:
                logger.error(f"❌ Failed to fetch cached data: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Error fetching cached GoPlus data: {e}")
            return None

    def update_graduation_status(
        self,
        token_address: str,
        graduated: bool,
        consecutive_passes: int,
        last_goplus_check: Optional[datetime] = None
    ) -> bool:
        """
        Update graduation status for a token in discovered_tokens table.

        Args:
            token_address: Token contract address
            graduated: Graduation status
            consecutive_passes: Number of consecutive filter passes
            last_goplus_check: Timestamp of last GoPlus API call (defaults to now)

        Returns:
            bool: True if successful
        """
        try:
            url = f"{self.base_url}/discovered_tokens"
            params = {"token_address": f"eq.{token_address}"}

            if last_goplus_check is None:
                last_goplus_check = datetime.now()

            update_data = {
                'graduated': graduated,
                'consecutive_passes': consecutive_passes,
                'last_goplus_check': last_goplus_check.isoformat()
            }

            response = requests.patch(
                url,
                headers=self.headers,
                params=params,
                json=update_data,
                timeout=30
            )

            if response.status_code in [200, 204]:
                logger.debug(f"✅ Updated graduation status for {token_address}")
                return True
            else:
                logger.error(f"❌ Failed to update graduation status: HTTP {response.status_code}")
                logger.error(f"Response body: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Error updating graduation status: {e}")
            return False


# Example usage
if __name__ == "__main__":
    print("Testing Supabase REST API client...")

    client = SupabaseREST()

    # Test fetch
    tokens = client.get_all_tokens(limit=500)
    print(f"Found {len(tokens)} tokens")
