"""
DexScreener API Integration
Discover new tokens on BSC via DexScreener with advanced liquidity filtering
"""

import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Dexscreener:
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
        # API endpoints
        self.api_token_profiles_latest = "https://api.dexscreener.com/token-profiles/latest/v1"
        self.api_search = "https://api.dexscreener.com/latest/dex/search"
        self.api_token_pairs = "https://api.dexscreener.com/latest/dex/tokens"
        self.etherscan_v2_api = "https://api.etherscan.io/v2/api"  # Etherscan V2 (multi-chain)

        # Load BSCScan API key from config
        try:
            import sys
            import os
            # Add project root to path if not already there
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)

            from config.settings import BSCSCAN_API_KEY
            self.bscscan_api_key = BSCSCAN_API_KEY
        except (ImportError, Exception) as e:
            logger.warning(f"Failed to load BSCSCAN_API_KEY from config: {e}")
            self.bscscan_api_key = None

        # Rate limiting
        self.last_request_time = 0
        self.rate_limit_delay = 0.2  # 200ms between requests
        self.bscscan_rate_limit = 0.25  # 250ms between BSCScan calls (5/sec limit)

        # Cache latest profiles and token creation dates
        self.token_profiles_data = None
        self.token_creation_cache = {}  # Cache token creation dates

    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def get_latest_token_profiles(self) -> List[Dict]:
        """
        Get latest tokens with profiles from DexScreener

        This endpoint returns tokens that have been "boosted" or have profiles.
        Useful for finding trending/promoted tokens.

        Returns:
            List of token profile data
        """
        self._rate_limit()

        try:
            response = requests.get(
                self.api_token_profiles_latest,
                headers={"Accept": "*/*"},
                timeout=30
            )

            if response.status_code == 200:
                self.token_profiles_data = response.json()
                return self.token_profiles_data
            else:
                print(f"❌ Error getting profiles: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def search_pairs(self, query: str) -> List[Dict]:
        """
        Search for trading pairs

        Args:
            query: Search term (token symbol, name, or address)

        Returns:
            List of pair data dictionaries
        """
        self._rate_limit()

        try:
            response = requests.get(
                self.api_search,
                params={"q": query},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print(f"Found: {len(data.get('pairs'))} pairs")
                return data.get('pairs', [])
            else:
                print(f"❌ Search error: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def get_token_pairs(self, token_address: str) -> List[Dict]:
        """
        Get all pairs for a specific token address

        Args:
            token_address: Token contract address

        Returns:
            List of pair data
        """
        self._rate_limit()

        try:
            url = f"{self.api_token_pairs}/{token_address}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data.get('pairs', [])
            else:
                print(f"❌ Token pairs error: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def get_token_creation_date(self, token_address: str) -> Optional[datetime]:
        """
        Get token contract creation date from Etherscan V2 API (BSC)

        Args:
            token_address: Token contract address

        Returns:
            datetime object of token creation, or None if not found
        """
        # Check cache first
        if token_address in self.token_creation_cache:
            return self.token_creation_cache[token_address]

        if not self.bscscan_api_key:
            return None

        time.sleep(self.bscscan_rate_limit)

        try:
            # Get contract creation transaction hash
            response = requests.get(self.etherscan_v2_api, params={
                'chainid': '56',
                'module': 'contract',
                'action': 'getcontractcreation',
                'contractaddresses': token_address,
                'apikey': self.bscscan_api_key
            }, timeout=10)

            if response.status_code != 200 or response.json().get('status') != '1':
                return None

            tx_hash = response.json()['result'][0]['txHash']

            # Get transaction to find block number
            time.sleep(self.bscscan_rate_limit)
            tx_response = requests.get(self.etherscan_v2_api, params={
                'chainid': '56',
                'module': 'proxy',
                'action': 'eth_getTransactionByHash',
                'txhash': tx_hash,
                'apikey': self.bscscan_api_key
            }, timeout=10)

            if tx_response.status_code != 200:
                return None

            block_num = tx_response.json()['result']['blockNumber']

            # Get block to find timestamp
            time.sleep(self.bscscan_rate_limit)
            block_response = requests.get(self.etherscan_v2_api, params={
                'chainid': '56',
                'module': 'proxy',
                'action': 'eth_getBlockByNumber',
                'tag': block_num,
                'boolean': 'false',
                'apikey': self.bscscan_api_key
            }, timeout=10)

            if block_response.status_code != 200:
                return None

            timestamp_hex = block_response.json()['result']['timestamp']
            creation_date = datetime.fromtimestamp(int(timestamp_hex, 16))

            # Cache and return
            self.token_creation_cache[token_address] = creation_date
            return creation_date

        except Exception as e:
            logger.debug(f"Error getting token creation date for {token_address}: {e}")
            return None

    def discover_latest_bsc_tokens(
        self,
        min_liquidity_usd: float = 10000,
        min_volume_24h_usd: float = 5000,  # Minimum 24h volume
        max_market_cap_usd: float = 5000000,  # Maximum market cap ($5M from config)
        min_token_age_days: int = 7,  # Minimum token age
        max_token_age_days: int = 30,  # Maximum token age
        limit: int = 50
    ) -> List[Dict]:
        """
        Discover recent BSC tokens using search with comprehensive filters

        Strategy:
        1. Search for common pairs (BNB, USDT, BUSD)
        2. Filter by BSC chain and exclude base tokens
        3. Verify token age via BSCScan (not just pair age)
        4. Filter by liquidity, volume, and market cap
        5. Deduplicate by token address (keep highest liquidity pair)
        6. Return newest tokens

        Args:
            min_liquidity_usd: Minimum liquidity in USD (default: $50K)
            min_volume_24h_usd: Minimum 24h volume (default: $10K)
            max_market_cap_usd: Maximum market cap (default: $10M)
            min_token_age_days: Minimum token age in days (default: 7)
            max_token_age_days: Maximum token age in days (default: 30)
            limit: Maximum results to return (default: 50)

        Returns:
            List of token pair data
        """
        print("🔍 Discovering BSC tokens...")

        # Expanded search terms - BSC-native and popular tokens
        SEARCH_TERMS = {
            # Stablecoins & Wrapped Assets (BSC versions)
            "WBNB": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",   # Wrapped BNB
            "USDT": "0x55d398326f99059fF775485246999027B3197955",   # Tether (BSC)
            "USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",   # USD Coin (BSC)
            "BUSD": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",   # Binance USD
            "FDUSD": "0xc5f0f7b66764F6ec8C8Dff7BA683102295E16409",  # First Digital USD

            # DEX Tokens (BSC-native)
            "CAKE": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",   # PancakeSwap
            "BABY": "0x53E562b9B7E5E94b81f10e96Ee70Ad06df3D2657",   # BabySwap
            "BANANA": "0x603c7f932ED1fc6575303D8Fb018fDCBb0f39a95", # ApeSwap
            "BISWAP": "0x965F527D9159dCe6288a2219DB51fc6Eef120dD1", # Biswap

            # Popular BSC-Native Meme/Community Tokens
            "SAFEMOON": "0x8076C74C5e3F5852037F31Ff0093Eeb8c8ADd8D3", # SafeMoon V2
            "BABYDOGE": "0xc748673057861a797275CD8A068AbB95A902e8de", # Baby Doge Coin
            "FLOKI": "0xfb5B838b6cfEEdC2873aB27866079AC55363D37E",  # Floki Inu (BSC)
            "SHIB": "0x2859e4544C4bB03966803b044A93563Bd2D0DD4D",   # SHIB (BSC bridged)

            # Gaming & Metaverse (BSC)
            "GALA": "0x7dDEE176F665cD201F93eEDE625770E2fD911990",   # Gala Games (BSC)
            "SAND": "0x67b725d7e342d7B611fa85e859Df9697D9378B2e",   # The Sandbox (BSC)
            "MBOX": "0x3203c9E46cA618C8C1cE5dC67e7e9D75f5da2377",   # Mobox

            # DeFi Tokens (BSC)
            "XVS": "0xcF6BB5389c92Bdda8a3747Ddb454cB7a64626C63",    # Venus
            "ALPACA": "0x8F0528cE5eF7B51152A59745bEfDD91D97091d2F", # Alpaca Finance
            "BELT": "0xE0e514c71282b6f4e823703a39374Cf58dc3eA4f",  # Belt Finance

            # Bridged Major Assets
            "WETH": "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",   # Wrapped ETH
            "BTCB": "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",   # Bitcoin BEP20
            "DOT": "0x7083609fCE4d1d8Dc0C979AAb8c869Ea2C873402",    # Polkadot (BSC)
            "ADA": "0x3EE2200Efb3400fAbB9AacF31297cBdD1d435D47",    # Cardano (BSC)
        }

        all_pairs = []

        # Step 1: Try to get latest token profiles (boosted/promoted tokens)
        print("   Fetching latest token profiles...")
        try:
            profiles = self.get_latest_token_profiles()
            if profiles:
                # Extract BSC pairs from profiles
                for profile in profiles:
                    if profile.get('chainId') == 'bsc':
                        all_pairs.append(profile)
                print(f"   Found {len([p for p in profiles if p.get('chainId') == 'bsc'])} BSC tokens from profiles")
        except Exception as e:
            logger.warning(f"Could not fetch token profiles: {e}")

        # Step 2: Search via popular tokens
        for term, address in SEARCH_TERMS.items():
            print(f"   Searching: {term}...")
            pairs = self.search_pairs(address)

            # Filter for BSC only and exclude base token matches
            bsc_pairs = [p for p in pairs if p.get('chainId') == 'bsc' and p.get('baseToken', {}).get('address', '').lower() != address.lower()]
            print(f"   Found {len(bsc_pairs)} BSC pairs")
            all_pairs.extend(bsc_pairs)

            # Small delay between searches
            time.sleep(0.5)

        # Deduplicate by token address (keep highest liquidity pair per token)
        unique_tokens = {}
        for pair in all_pairs:
            token_addr = pair.get('baseToken', {}).get('address', '').lower()
            if not token_addr:
                continue

            # Keep pair with highest liquidity for each token
            pair_liquidity = pair.get('liquidity', {}).get('usd', 0)
            if token_addr not in unique_tokens or pair_liquidity > unique_tokens[token_addr].get('liquidity', {}).get('usd', 0):
                unique_tokens[token_addr] = pair

        # Filter by criteria
        filtered_pairs = []
        token_age_cutoff_min = datetime.now() - timedelta(days=max_token_age_days)
        token_age_cutoff_max = datetime.now() - timedelta(days=min_token_age_days)

        for token_addr, pair in unique_tokens.items():
            # Check liquidity
            liquidity = pair.get('liquidity', {}).get('usd', 0)
            if liquidity < min_liquidity_usd:
                continue

            # Check 24h volume
            volume_24h = pair.get('volume', {}).get('h24', 0)
            if volume_24h < min_volume_24h_usd:
                continue

            # Check market cap
            market_cap = pair.get('marketCap', 0)
            if market_cap > max_market_cap_usd:
                continue

            # # Check token creation date via BSCScan
            # token_creation_date = self.get_token_creation_date(token_addr)
            # if token_creation_date:
            #     if token_creation_date < token_age_cutoff_min:
            #         logger.info(f"   Skipping {pair.get('baseToken', {}).get('symbol')} - too old ({(datetime.now() - token_creation_date).days} days)")
            #         continue
            #     if token_creation_date > token_age_cutoff_max:
            #         logger.info(f"   Skipping {pair.get('baseToken', {}).get('symbol')} - too young ({(datetime.now() - token_creation_date).days} days)")
            #         continue
            # else:
            #     # If we can't verify token age, skip it to be safe
            #     logger.warning(f"   Skipping {pair.get('baseToken', {}).get('symbol')} - couldn't verify token age")
            #     continue

            filtered_pairs.append(pair)

        # Sort by market cap (smallest first - more upside potential)
        filtered_pairs.sort(key=lambda x: x.get('marketCap', 0))

        print(f"✅ Found {len(filtered_pairs)} tokens matching criteria")

        return filtered_pairs[:limit]

    def discover_latest_bsc_tokens_enhanced(
        self,
        min_liquidity_usd: float = 10000, # Minimum liquidity required in the main trading pair compared to $50 trades. 10000 for testing. perhaps 50000 for prod.
        max_age_days: int = 50, # Age of trading pair - more likely to be legitimate (but also good value).
        limit: int = 50, # 100 would take a long time, 20 would be fewer options at the end but faster.
        min_liquidity_score: int = 80, # Points tally (higher means more legitimate). 80 is a conservative approach.
        trade_size_usd: float = 50 # Large trades on smaller pools would cause slippage and eat into profit.
    ) -> List[Dict]:
        """
        Enhanced token discovery with comprehensive liquidity analysis

        This function combines token discovery with advanced liquidity filtering
        to identify high-quality, low-risk tokens. Only tokens that pass strict
        liquidity quality checks are returned.

        Args:
            min_liquidity_usd: Minimum liquidity in USD (default: $10K)
            max_age_days: Maximum age in days (default: 30)
            limit: Maximum results to return (default: 50)
            min_liquidity_score: Minimum liquidity quality score 0-100 (default: 80)
            trade_size_usd: Expected trade size for slippage calculation (default: $50)

        Returns:
            List of token pair data with liquidity analysis results
            Each token includes 'liquidity_analysis' field with comprehensive data
        """
        # Import here to avoid circular dependency
        try:
            from src.analysis.liquidity import LiquidityAnalyzer
        except ImportError:
            logger.error("Failed to import LiquidityAnalyzer. Install required dependencies.")
            return []

        logger.info("🔍 Starting enhanced token discovery with liquidity filtering")
        logger.info(f"   Max age: {max_age_days} days")
        logger.info(f"   Min liquidity: ${min_liquidity_usd:,.0f}")
        logger.info(f"   Min liquidity score: {min_liquidity_score}")

        # Step 1: Get candidate tokens using standard discovery
        candidate_tokens = self.discover_latest_bsc_tokens(
            min_liquidity_usd=min_liquidity_usd,
            max_token_age_days=max_age_days,
            limit=limit * 3  # Get more candidates to filter
        )

        if not candidate_tokens:
            logger.warning("No candidate tokens found")
            return []

        logger.info(f"   Found {len(candidate_tokens)} candidate tokens")

        # Step 2: Analyze liquidity quality for each token
        analyzer = LiquidityAnalyzer()
        analyzed_tokens = []

        for i, pair in enumerate(candidate_tokens, 1):
            print(f"Token number: {i}, {pair['baseToken']['name']}")
            token_address = pair.get('baseToken', {}).get('address')

            if not token_address:
                continue

            logger.info(f"   [{i}/{len(candidate_tokens)}] Analyzing {token_address[:10]}...")

            try:
                # Run comprehensive liquidity analysis
                analysis = analyzer.comprehensive_liquidity_analysis(
                    token_address=token_address,
                    trade_size_usd=trade_size_usd
                )

                # Add analysis results to pair data
                pair['liquidity_analysis'] = analysis

                # Filter by score and recommendation
                score = analysis['total_score']
                recommendation = analysis['recommendation']

                if score >= min_liquidity_score:
                    analyzed_tokens.append(pair)
                    logger.info(f"      ✅ PASS - Score: {score}, Recommendation: {recommendation}")
                elif score >= 60:
                    # Include CAUTION tokens for manual review
                    analyzed_tokens.append(pair)
                    logger.info(f"      ⚠️  CAUTION - Score: {score}, Flags: {len(analysis['flags'])}")
                else:
                    logger.info(f"      ❌ REJECT - Score: {score}")

            except Exception as e:
                logger.error(f"      Error analyzing token: {e}")
                continue

            # Rate limiting between analyses
            time.sleep(0.3)

        # Step 3: Sort by liquidity score (highest first)
        analyzed_tokens.sort(
            key=lambda x: x.get('liquidity_analysis', {}).get('total_score', 0),
            reverse=True
        )

        logger.info(f"✅ Found {len(analyzed_tokens)} tokens passing liquidity filters")

        return analyzed_tokens[:limit]

    @staticmethod
    def extract_token_info(pair: Dict) -> Dict:
        """
        Extract relevant token information from pair data

        Args:
            pair: Pair data from DexScreener

        Returns:
            Dictionary with cleaned token data
        """
        base_token = pair.get('baseToken', {})
        created_at = pair.get('pairCreatedAt', 0)

        # Calculate age
        if created_at:
            created_date = datetime.fromtimestamp(created_at / 1000)
            age_days = (datetime.now() - created_date).days
            age_hours = (datetime.now() - created_date).total_seconds() / 3600
        else:
            age_days = None
            age_hours = None

        return {
            'address': base_token.get('address'),
            'name': base_token.get('name'),
            'symbol': base_token.get('symbol'),
            'chain': pair.get('chainId'),
            'dex': pair.get('dexId'),
            'pair_address': pair.get('pairAddress'),
            'price_usd': float(pair.get('priceUsd', 0)),
            'liquidity_usd': pair.get('liquidity', {}).get('usd', 0),
            'market_cap': pair.get('marketCap', 0),
            'fdv': pair.get('fdv', 0),
            'volume_24h': pair.get('volume', {}).get('h24', 0),
            'price_change_24h': pair.get('priceChange', {}).get('h24', 0),
            'txns_24h_buys': pair.get('txns', {}).get('h24', {}).get('buys', 0),
            'txns_24h_sells': pair.get('txns', {}).get('h24', {}).get('sells', 0),
            'created_at': created_at,
            'age_days': age_days,
            'age_hours': age_hours,
            'url': pair.get('url'),
            'liquidity_analysis': pair.get('liquidity_analysis'),
        }


# Example usage
if __name__ == "__main__":
    api = Dexscreener()
    # Test: Discover latest BSC tokens
    print("Test: Discover Latest BSC Tokens")
    print("-" * 70)
    tokens = api.discover_latest_bsc_tokens()
    print(f"Top {len(tokens)} Recent BSC Tokens:")
    print("=" * 70)
    for i, pair in enumerate(tokens, 1):
        token_info = api.extract_token_info(pair)
        if token_info:
            print(f"\n#{i} - {token_info['name']} (${token_info['symbol']})")
            print(f"   Address: {token_info['address']}")
            if token_info['age_days'] is not None:
                print(f"   Age: {token_info['age_days']} days ({token_info['age_hours']:.1f} hours)")
            else:
                print("   Age: Unknown")
            print(f"   Liquidity: ${token_info['liquidity_usd']:,.2f}")
            print(f"   Market Cap: ${token_info['market_cap']:,.2f}")
            print(f"   24h Volume: ${token_info['volume_24h']:,.2f}")
            print(f"   24h Change: {token_info['price_change_24h']:.2f}%")
            print(f"   DEX: {token_info['dex']}")
            print(f"   URL: {token_info['url']}")

    print("\n" + "=" * 70)
    print("✅ All tests complete!")
