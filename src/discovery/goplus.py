"""
GoPlus Security API Client
Fetches holder data and security flags for tokens across multiple chains

API Docs: https://docs.gopluslabs.io/reference/token-security-api
"""

import requests
import logging
from typing import Dict, Optional
from time import time, sleep
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoPlus:
    """
    Interface to GoPlus Security API for token security analysis

    Data points:
     - holder_count - Total holders
     - top_holder_percent - Largest wallet %
     - lp_holder_count - LP token holders
     - lp_locked_percent - % of LP tokens locked/burned
     - is_honeypot - Scam flag
     - buy_tax - Buy fee %
     - sell_tax - Sell fee %
     - is_open_source - Verified contract
     - is_mintable - Can mint unlimited tokens
     - transfer_pausable - Can pause transfers
     - can_take_back_ownership - Ownership backdoor
     - owner_address - Contract owner address

    Rate Limits:
     - No official limit, throttled to 1 req/sec for safety
    """
    
    # Chain ID mapping (GoPlus uses numeric IDs)
    CHAIN_IDS = {
        'bsc': '56',
        'eth': '1',
        'polygon': '137',
        'arbitrum': '42161',
        'optimism': '10',
        'base': '8453'
    }
    
    def __init__(self):
        self.base_url = "https://api.gopluslabs.io/api/v1"
        
        # Rate limiting: 1 request per second (conservative)
        self.api_calls = deque(maxlen=60)
        
    def _rate_limit(self):
        """Enforce 1 request/second rate limit"""
        current_time = time()
        
        # Remove calls older than 60 seconds
        while self.api_calls and current_time - self.api_calls[0] > 60:
            self.api_calls.popleft()
        
        # If we've made 60 calls in last 60s, wait
        if len(self.api_calls) >= 60:
            sleep_time = 60 - (current_time - self.api_calls[0])
            if sleep_time > 0:
                logger.warning(f"⏳ GoPlus rate limit: Sleeping {sleep_time:.1f}s")
                sleep(sleep_time)
                self.api_calls.popleft()
        
        # Also enforce minimum 1s between calls
        if self.api_calls:
            time_since_last = current_time - self.api_calls[-1]
            if time_since_last < 1.0:
                sleep(1.0 - time_since_last)
        
        self.api_calls.append(time())
    
    def fetch_token_security(self, token_address: str, chain_id: str = 'bsc', max_retries: int = 3) -> Optional[Dict]:
        """
        Fetch security data for a token from GoPlus API with retry logic

        Args:
            token_address: Token contract address
            chain_id: Chain identifier ('bsc', 'eth', 'arbitrum', etc.)
            max_retries: Number of retry attempts if rate limited

        Returns:
            Dict with security metrics, or None if failed
        """
        # Convert chain_id to numeric format
        numeric_chain_id = self.CHAIN_IDS.get(chain_id.lower(), '56')

        # GoPlus expects lowercase addresses
        token_address = token_address.lower()

        url = f"{self.base_url}/token_security/{numeric_chain_id}"
        params = {'contract_addresses': token_address}

        for attempt in range(max_retries):
            try:
                # Apply rate limiting before each attempt
                self._rate_limit()

                response = requests.get(url, params=params, timeout=10)

                # Handle rate limiting (429 or 503)
                if response.status_code in [429, 503]:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5  # 5s, 10s, 15s
                        logger.warning(f"⏳ GoPlus rate limited, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                        sleep(wait_time)
                        continue
                    else:
                        logger.warning(f"GoPlus API rate limited after {max_retries} attempts")
                        return None

                if response.status_code != 200:
                    logger.warning(f"GoPlus API error: HTTP {response.status_code}")
                    return None

                data = response.json()

                # Check if response is valid
                if data.get('code') != 1:
                    error_msg = data.get('message', 'Unknown error')

                    # Retry on "too many requests" error
                    if 'too many requests' in error_msg.lower() and attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5
                        logger.warning(f"⏳ GoPlus rate limited, waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                        sleep(wait_time)
                        continue

                    logger.warning(f"GoPlus API returned error: {error_msg}")
                    return None

                # Extract token data
                result = data.get('result', {})
                token_data = result.get(token_address)

                if not token_data:
                    logger.debug(f"No security data found for {token_address} on chain {chain_id}")
                    return None

                # Parse and return relevant fields
                return self._parse_security_data(token_data)

            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"Error fetching GoPlus data, retrying in {wait_time}s: {e}")
                    sleep(wait_time)
                    continue
                else:
                    logger.error(f"Error fetching GoPlus data after {max_retries} attempts: {e}")
                    return None

        return None
    
    def _parse_security_data(self, raw_data: Dict) -> Dict:
        """
        Parse GoPlus API response into clean format

        Args:
            raw_data: Raw API response for single token

        Returns:
            Cleaned dict with relevant fields
        """
        # Extract holder data
        holder_count = raw_data.get('holder_count')
        if holder_count:
            try:
                holder_count = int(holder_count)
            except (ValueError, TypeError):
                holder_count = None

        # Extract LP holder data
        lp_holder_count = raw_data.get('lp_holder_count')
        if lp_holder_count:
            try:
                lp_holder_count = int(lp_holder_count)
            except (ValueError, TypeError):
                lp_holder_count = None

        # Calculate LP locked percentage from lp_holders array
        lp_locked_percent = self._calculate_lp_locked(raw_data.get('lp_holders', []))

        # Extract top holder percentage
        # GoPlus provides multiple holder fields, we want the largest
        creator_percent = float(raw_data.get('creator_percent', 0)) * 100
        owner_percent = float(raw_data.get('owner_percent', 0)) * 100

        # Get top holder from holders list if available
        holders = raw_data.get('holders', [])
        top_holder_percent = max(creator_percent, owner_percent)

        if holders and len(holders) > 0:
            # Find largest non-contract holder (skip DEX pairs)
            for holder in holders[:10]:  # Check top 10
                if not holder.get('is_contract', False):
                    holder_pct = float(holder.get('percent', 0)) * 100
                    top_holder_percent = max(top_holder_percent, holder_pct)
                    break

        # Security flags (convert string "0"/"1" to boolean)
        is_honeypot = raw_data.get('is_honeypot') == '1'
        is_open_source = raw_data.get('is_open_source') == '1'
        is_mintable = raw_data.get('is_mintable') == '1'
        transfer_pausable = raw_data.get('transfer_pausable') == '1'
        can_take_back_ownership = raw_data.get('can_take_back_ownership') == '1'

        # Tax percentages (convert string decimal to percentage)
        try:
            buy_tax = float(raw_data.get('buy_tax', 0)) * 100
        except (ValueError, TypeError):
            buy_tax = 0.0

        try:
            sell_tax = float(raw_data.get('sell_tax', 0)) * 100
        except (ValueError, TypeError):
            sell_tax = 0.0

        # Owner address
        owner_address = raw_data.get('owner_address')

        return {
            # Holder data
            'holder_count': holder_count,
            'top_holder_percent': round(top_holder_percent, 2) if top_holder_percent else None,
            'lp_holder_count': lp_holder_count,
            'lp_locked_percent': lp_locked_percent,

            # Security flags
            'is_honeypot': is_honeypot,
            'buy_tax': round(buy_tax, 2),
            'sell_tax': round(sell_tax, 2),
            'is_open_source': is_open_source,
            'is_mintable': is_mintable,
            'transfer_pausable': transfer_pausable,
            'can_take_back_ownership': can_take_back_ownership,

            # Ownership
            'owner_address': owner_address
        }

    def _calculate_lp_locked(self, lp_holders: list) -> Optional[float]:
        """
        Calculate percentage of LP tokens that are locked or burned

        Args:
            lp_holders: List of LP token holders from GoPlus

        Returns:
            Percentage locked (0-100), or None if data unavailable
        """
        if not lp_holders:
            return None

        # Known lock/burn addresses
        LOCK_ADDRESSES = {
            '0x000000000000000000000000000000000000dead',  # Dead address
            '0x0000000000000000000000000000000000000000',  # Null address
        }

        total_locked = 0.0

        for holder in lp_holders:
            address = holder.get('address', '').lower()
            is_locked = holder.get('is_locked', 0)

            # Count as locked if: marked as locked OR sent to burn address
            if is_locked == 1 or address in LOCK_ADDRESSES:
                percent = float(holder.get('percent', 0)) * 100
                total_locked += percent

        return round(total_locked, 2)


# Test function
if __name__ == "__main__":
    print("Testing GoPlus API client...")

    client = GoPlus()

    # Test with USDT on BSC
    print("\n" + "="*70)
    print("Test 1: USDT on BSC (should be safe)")
    print("="*70)
    usdt_bsc = "0x55d398326f99059fF775485246999027B3197955"
    data = client.fetch_token_security(usdt_bsc, 'bsc')

    if data:
        print(f"✅ Holder Count: {data.get('holder_count')}")
        print(f"✅ Top Holder: {data.get('top_holder_percent')}%")
        print(f"✅ LP Locked: {data.get('lp_locked_percent')}%")
        print(f"✅ Is Honeypot: {data.get('is_honeypot')}")
        print(f"✅ Buy Tax: {data.get('buy_tax')}%")
        print(f"✅ Sell Tax: {data.get('sell_tax')}%")
        print(f"✅ Open Source: {data.get('is_open_source')}")
        print(f"✅ Transfer Pausable: {data.get('transfer_pausable')}")
    else:
        print("❌ Failed to fetch data")

    # Test with meme token (the Chinese one from earlier)
    print("\n" + "="*70)
    print("Test 2: Meme token on BSC")
    print("="*70)
    meme_token = "0x88E3a20b8FC4d30bd733477d775992bE62654444"
    data = client.fetch_token_security(meme_token, 'bsc')

    if data:
        print(f"📊 Holder Count: {data.get('holder_count')}")
        print(f"📊 Top Holder: {data.get('top_holder_percent')}%")
        print(f"📊 LP Locked: {data.get('lp_locked_percent')}%")
        print(f"📊 Is Honeypot: {data.get('is_honeypot')}")
        print(f"📊 Buy Tax: {data.get('buy_tax')}%")
        print(f"📊 Sell Tax: {data.get('sell_tax')}%")
        print(f"📊 Transfer Pausable: {data.get('transfer_pausable')}")
        print(f"📊 Owner: {data.get('owner_address')}")
    else:
        print("❌ Failed to fetch data")