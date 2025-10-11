import psycopg2
from dotenv import load_dotenv
import os
import socket
import logging
from typing import List, Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Supabase:
    def __init__(self):
        # Load environment variables from .env
        load_dotenv()

        # Fetch variables
        self.password = os.getenv("SUPABASE_PASSWORD")
        self.user = os.getenv("SUPABASE_USERNAME")
        self.host = os.getenv("SUPABASE_HOST")
        self.port = os.getenv("SUPABASE_PORT")
        self.dbname = os.getenv("SUPABASE_DBNAME")

        self.connection = None
        if not self.connection:
            self.connection = self.get_connection()

    def get_connection(self):
        """
        Create and return a Supabase PostgreSQL connection

        Returns:
            psycopg2 connection object
        """
        try:
            # Force IPv4 resolution for GitHub Actions compatibility
            # psycopg2 sometimes tries IPv6 first, which fails on GitHub runners

            # Resolve hostname to IPv4 address only
            logger.info(f"Attempting to connect to Supabase: {self.host}:{self.port}")
            try:
                ipv4_host = socket.getaddrinfo(
                    self.host,
                    self.port,
                    socket.AF_INET,  # Force IPv4
                    socket.SOCK_STREAM
                )[0][4][0]
                logger.info(f"✅ Resolved {self.host} to IPv4: {ipv4_host}")
                host_to_use = ipv4_host
            except socket.gaierror as dns_error:
                # If IPv4 resolution fails, fall back to original hostname
                logger.warning(f"⚠️ Could not resolve {self.host} to IPv4: {dns_error}")
                logger.warning(f"Falling back to hostname: {self.host}")
                host_to_use = self.host

            connection = psycopg2.connect(
                user=self.user,
                password=self.password,
                host=host_to_use,  # Use resolved IPv4 address
                port=self.port,
                dbname=self.dbname
            )
            return connection
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise

    def create_table_if_not_exists(self):
        """
        Create the discovered_tokens table if it doesn't exist
        Run this once to set up your database
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS discovered_tokens (
            id BIGSERIAL PRIMARY KEY,
            chain_id TEXT NOT NULL,
            token_address TEXT NOT NULL,
            dexscreener_url TEXT,
            discovered_at TIMESTAMP WITH TIME ZONE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

            CONSTRAINT unique_token_per_chain UNIQUE (chain_id, token_address)
        );

        CREATE INDEX IF NOT EXISTS idx_discovered_tokens_chain ON discovered_tokens(chain_id);
        CREATE INDEX IF NOT EXISTS idx_discovered_tokens_discovered_at ON discovered_tokens(discovered_at);
        CREATE INDEX IF NOT EXISTS idx_discovered_tokens_chain_date ON discovered_tokens(chain_id, discovered_at);
        """

        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
            logger.info("✅ Table 'discovered_tokens' ready")
            cursor.close()
        except Exception as e:
            logger.error(f"❌ Failed to create table: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def store_discovered_tokens(self, tokens_list: List[Dict]) -> Dict:
        """
        Store discovered tokens with automatic duplicate prevention.

        Uses PostgreSQL's ON CONFLICT to skip duplicates - NO need to query first!
        This is fast and prevents duplicate entries automatically.

        Args:
            tokens_list: List of token dicts with keys:
                        - chain_id (str)
                        - address (str)
                        - dexscreener_url (str)
                        - discovered_at (float, unix timestamp)

        Returns:
            Dict: {
                'total': int,           # Total tokens attempted
                'inserted': int,        # New tokens added
                'skipped': int,         # Duplicates skipped
                'errors': []            # Any errors
            }
        """
        if not tokens_list:
            logger.warning("No tokens to store")
            return {'total': 0, 'inserted': 0, 'skipped': 0, 'errors': []}

        conn = None
        stats = {
            'total': len(tokens_list),
            'inserted': 0,
            'skipped': 0,
            'errors': []
        }

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # ON CONFLICT = automatic duplicate prevention
            # If (chain_id, token_address) already exists, skip it
            # If new, insert it and return the id
            insert_sql = """
            INSERT INTO discovered_tokens (chain_id, token_address, dexscreener_url, discovered_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (chain_id, token_address) DO NOTHING
            RETURNING id;
            """

            for token in tokens_list:
                try:
                    # Convert Unix timestamp to PostgreSQL timestamp
                    discovered_timestamp = datetime.fromtimestamp(token.get('discovered_at', 0))

                    cursor.execute(insert_sql, (
                        token.get('chain_id'),
                        token.get('address'),
                        token.get('dexscreener_url'),
                        discovered_timestamp
                    ))

                    # If a row is returned, token was inserted (new)
                    # If no row returned, it was a duplicate (skipped)
                    result = cursor.fetchone()
                    if result:
                        stats['inserted'] += 1
                        logger.debug(f"✅ Inserted: {token.get('chain_id')} {token.get('address')}")
                    else:
                        stats['skipped'] += 1
                        logger.debug(f"⏭️  Skipped (duplicate): {token.get('chain_id')} {token.get('address')}")

                except Exception as e:
                    error_msg = f"Error storing {token.get('address', 'unknown')}: {e}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)

            conn.commit()
            cursor.close()

            logger.info(f"📊 Storage: {stats['inserted']} new, {stats['skipped']} duplicates, {len(stats['errors'])} errors")

        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            stats['errors'].append(str(e))
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

        return stats

    def get_tokens_by_age(self, min_age_days: int = 7, max_age_days: int = 30, chain_id: str = 'bsc') -> List[Dict]:
        """
        Get tokens within a specific age range for analysis.

        This is the PRIMARY method for fetching tokens ready for liquidity analysis.
        Tokens must have survived min_age_days (default 7) to pass scam filter.

        Args:
            min_age_days: Minimum token age in days (default: 7)
            max_age_days: Maximum token age in days (default: 30)
            chain_id: Blockchain filter (default: 'bsc')

        Returns:
            List of token dicts with keys:
                - id (int)
                - chain_id (str)
                - token_address (str)
                - dexscreener_url (str)
                - discovered_at (datetime)
                - created_at (datetime)
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT id, chain_id, token_address, dexscreener_url, discovered_at, created_at
            FROM discovered_tokens
            WHERE chain_id = %s
              AND discovered_at >= NOW() - INTERVAL '%s days'
              AND discovered_at <= NOW() - INTERVAL '%s days'
            ORDER BY discovered_at DESC;
            """

            cursor.execute(query, (chain_id, max_age_days, min_age_days))
            rows = cursor.fetchall()

            tokens = []
            for row in rows:
                tokens.append({
                    'id': row[0],
                    'chain_id': row[1],
                    'token_address': row[2],
                    'dexscreener_url': row[3],
                    'discovered_at': row[4],
                    'created_at': row[5]
                })

            logger.info(f"📊 Found {len(tokens)} tokens aged {min_age_days}-{max_age_days} days on {chain_id}")
            cursor.close()
            return tokens

        except Exception as e:
            logger.error(f"❌ Query error in get_tokens_by_age: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_all_tokens(self, chain_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        Get all discovered tokens with optional filters.

        Args:
            chain_id: Filter by blockchain (optional)
            limit: Maximum number of tokens to return (optional)

        Returns:
            List of token dicts
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = "SELECT id, chain_id, token_address, dexscreener_url, discovered_at, created_at FROM discovered_tokens"
            params = []

            if chain_id:
                query += " WHERE chain_id = %s"
                params.append(chain_id)

            query += " ORDER BY discovered_at DESC"

            if limit:
                query += " LIMIT %s"
                params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            tokens = []
            for row in rows:
                tokens.append({
                    'id': row[0],
                    'chain_id': row[1],
                    'token_address': row[2],
                    'dexscreener_url': row[3],
                    'discovered_at': row[4],
                    'created_at': row[5]
                })

            logger.info(f"📊 Retrieved {len(tokens)} tokens" + (f" on {chain_id}" if chain_id else ""))
            cursor.close()
            return tokens

        except Exception as e:
            logger.error(f"❌ Query error in get_all_tokens: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_token_by_address(self, token_address: str, chain_id: str = 'bsc') -> Optional[Dict]:
        """
        Get a specific token by its address.

        Args:
            token_address: Token contract address
            chain_id: Blockchain (default: 'bsc')

        Returns:
            Token dict or None if not found
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT id, chain_id, token_address, dexscreener_url, discovered_at, created_at
            FROM discovered_tokens
            WHERE token_address = %s AND chain_id = %s
            LIMIT 1;
            """

            cursor.execute(query, (token_address, chain_id))
            row = cursor.fetchone()

            if row:
                token = {
                    'id': row[0],
                    'chain_id': row[1],
                    'token_address': row[2],
                    'dexscreener_url': row[3],
                    'discovered_at': row[4],
                    'created_at': row[5]
                }
                logger.debug(f"Found token: {token_address}")
                cursor.close()
                return token
            else:
                logger.warning(f"Token not found: {token_address} on {chain_id}")
                cursor.close()
                return None

        except Exception as e:
            logger.error(f"❌ Query error in get_token_by_address: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_recent_tokens(self, hours: int = 24, chain_id: Optional[str] = None) -> List[Dict]:
        """
        Get tokens discovered in the last N hours.

        Useful for monitoring scraper activity and recent discoveries.

        Args:
            hours: Number of hours to look back (default: 24)
            chain_id: Filter by blockchain (optional)

        Returns:
            List of recently discovered token dicts
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if chain_id:
                query = """
                SELECT id, chain_id, token_address, dexscreener_url, discovered_at, created_at
                FROM discovered_tokens
                WHERE discovered_at >= NOW() - INTERVAL '%s hours'
                  AND chain_id = %s
                ORDER BY discovered_at DESC;
                """
                params = (hours, chain_id)
            else:
                query = """
                SELECT id, chain_id, token_address, dexscreener_url, discovered_at, created_at
                FROM discovered_tokens
                WHERE discovered_at >= NOW() - INTERVAL '%s hours'
                ORDER BY discovered_at DESC;
                """
                params = (hours,)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            tokens = []
            for row in rows:
                tokens.append({
                    'id': row[0],
                    'chain_id': row[1],
                    'token_address': row[2],
                    'dexscreener_url': row[3],
                    'discovered_at': row[4],
                    'created_at': row[5]
                })

            logger.info(f"📊 Found {len(tokens)} tokens in last {hours}h" + (f" on {chain_id}" if chain_id else ""))
            cursor.close()
            return tokens

        except Exception as e:
            logger.error(f"❌ Query error in get_recent_tokens: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_database_stats(self) -> Dict:
        """
        Get comprehensive statistics about discovered tokens.

        Returns:
            Dict with statistics:
                - total_tokens: Total count across all chains
                - by_chain: Per-chain breakdown
                - by_age: Age bucket breakdown (0-7d, 7-30d, 30d+)
                - oldest_token: Oldest discovery timestamp
                - newest_token: Newest discovery timestamp
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Total and per-chain stats
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    chain_id,
                    MIN(discovered_at) as oldest,
                    MAX(discovered_at) as newest
                FROM discovered_tokens
                GROUP BY chain_id
                ORDER BY total DESC;
            """)
            chain_rows = cursor.fetchall()

            # Age bucket stats
            cursor.execute("""
                SELECT
                    COUNT(CASE WHEN discovered_at >= NOW() - INTERVAL '7 days' THEN 1 END) as last_7_days,
                    COUNT(CASE WHEN discovered_at >= NOW() - INTERVAL '30 days'
                               AND discovered_at < NOW() - INTERVAL '7 days' THEN 1 END) as days_7_to_30,
                    COUNT(CASE WHEN discovered_at < NOW() - INTERVAL '30 days' THEN 1 END) as over_30_days
                FROM discovered_tokens;
            """)
            age_row = cursor.fetchone()

            # Build stats dict
            stats = {
                'total_tokens': sum(row[0] for row in chain_rows),
                'by_chain': {},
                'by_age': {
                    'last_7_days': age_row[0] if age_row else 0,
                    'days_7_to_30': age_row[1] if age_row else 0,
                    'over_30_days': age_row[2] if age_row else 0
                },
                'oldest_token': None,
                'newest_token': None
            }

            for row in chain_rows:
                chain = row[1]
                stats['by_chain'][chain] = {
                    'count': row[0],
                    'oldest': row[2],
                    'newest': row[3]
                }

                # Track overall oldest/newest
                if stats['oldest_token'] is None or row[2] < stats['oldest_token']:
                    stats['oldest_token'] = row[2]
                if stats['newest_token'] is None or row[3] > stats['newest_token']:
                    stats['newest_token'] = row[3]

            cursor.close()
            logger.info(f"📊 Database stats: {stats['total_tokens']} total tokens")
            return stats

        except Exception as e:
            logger.error(f"❌ Query error in get_database_stats: {e}")
            return {
                'total_tokens': 0,
                'by_chain': {},
                'by_age': {},
                'oldest_token': None,
                'newest_token': None
            }
        finally:
            if conn:
                conn.close()

    def create_time_series_table(self):
        """
        Create the time_series_data table if it doesn't exist.
        Stores historical snapshots of token metrics for trend analysis.
        """
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS time_series_data (
            id BIGSERIAL PRIMARY KEY,

            -- Token identifiers
            token_address TEXT NOT NULL,
            chain_id TEXT NOT NULL,

            -- Snapshot timestamp
            snapshot_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

            -- DexScreener Metrics
            price_usd NUMERIC(20, 10),
            liquidity_usd NUMERIC(20, 2),
            volume_24h NUMERIC(20, 2),
            price_change_24h NUMERIC(10, 2),
            buys_24h INTEGER,
            sells_24h INTEGER,
            main_dex TEXT,
            pair_address TEXT,
            pair_count INTEGER,

            -- Holder Data (from GoPlus API)
            holder_count INTEGER,
            top_holder_percent NUMERIC(5, 2),
            lp_holder_count INTEGER,

            -- Security Flags (from GoPlus API)
            is_honeypot BOOLEAN,
            buy_tax NUMERIC(5, 2),
            sell_tax NUMERIC(5, 2),
            is_open_source BOOLEAN,

            -- Liquidity Analysis
            concentration_ratio NUMERIC(5, 4),
            concentration_score NUMERIC(5, 2),

            -- Metadata
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        -- Unique index to prevent duplicate snapshots
        CREATE UNIQUE INDEX IF NOT EXISTS idx_time_series_unique_snapshot
            ON time_series_data(token_address, chain_id, snapshot_at);

        -- Index for querying specific token over time
        CREATE INDEX IF NOT EXISTS idx_time_series_token_time
            ON time_series_data(token_address, chain_id, snapshot_at DESC);

        -- Index for recent snapshots
        CREATE INDEX IF NOT EXISTS idx_time_series_recent
            ON time_series_data(snapshot_at DESC);

        -- Index for liquidity filtering
        CREATE INDEX IF NOT EXISTS idx_time_series_liquidity
            ON time_series_data(liquidity_usd)
            WHERE liquidity_usd IS NOT NULL;

        -- Index for chain filtering
        CREATE INDEX IF NOT EXISTS idx_time_series_chain_time
            ON time_series_data(chain_id, snapshot_at DESC);
        """

        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
            logger.info("✅ Table 'time_series_data' ready")
            cursor.close()
        except Exception as e:
            logger.error(f"❌ Failed to create time_series_data table: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def store_time_series_data(self, metrics_data: Dict, token_address: str, chain_id: str) -> bool:
        """
        Store a single time-series snapshot of token metrics.

        Args:
            metrics_data: Dict from fetch_token_metrics() containing:
                - price_usd, liquidity_usd, volume_24h, price_change_24h
                - buys_24h, sells_24h, main_dex, pair_address, pair_count
                Optional: holder_count, top_holder_percent, concentration_score, etc.
            token_address: Token contract address
            chain_id: Blockchain identifier (bsc, base, arbitrum, optimism)

        Returns:
            bool: True if inserted, False if duplicate or error
        """
        if not metrics_data:
            logger.warning(f"No metrics data provided for {token_address}")
            return False

        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            insert_sql = """
            INSERT INTO time_series_data (
                token_address, chain_id, snapshot_at,
                price_usd, liquidity_usd, volume_24h, price_change_24h,
                buys_24h, sells_24h, main_dex, pair_address, pair_count,
                holder_count, top_holder_percent, lp_holder_count,
                is_honeypot, buy_tax, sell_tax, is_open_source,
                concentration_ratio, concentration_score
            )
            VALUES (
                %s, %s, NOW(),
                %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s
            )
            ON CONFLICT (token_address, chain_id, snapshot_at) DO NOTHING
            RETURNING id;
            """

            cursor.execute(insert_sql, (
                token_address,
                chain_id,
                # DexScreener metrics
                metrics_data.get('price_usd'),
                metrics_data.get('liquidity_usd'),
                metrics_data.get('volume_24h'),
                metrics_data.get('price_change_24h'),
                metrics_data.get('buys_24h'),
                metrics_data.get('sells_24h'),
                metrics_data.get('main_dex'),
                metrics_data.get('pair_address'),
                metrics_data.get('pair_count'),
                # GoPlus metrics (optional, may be None)
                metrics_data.get('holder_count'),
                metrics_data.get('top_holder_percent'),
                metrics_data.get('lp_holder_count'),
                # Security flags (optional)
                metrics_data.get('is_honeypot'),
                metrics_data.get('buy_tax'),
                metrics_data.get('sell_tax'),
                metrics_data.get('is_open_source'),
                # Analysis metrics (optional)
                metrics_data.get('concentration_ratio'),
                metrics_data.get('concentration_score')
            ))

            result = cursor.fetchone()
            conn.commit()
            cursor.close()

            if result:
                logger.debug(f"✅ Stored time-series data for {token_address} on {chain_id}")
                return True
            else:
                logger.debug(f"⏭️  Skipped duplicate snapshot for {token_address} on {chain_id}")
                return False

        except Exception as e:
            logger.error(f"❌ Error storing time-series data for {token_address}: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def get_time_series_data(self, token_address: str, chain_id: str = 'bsc', limit: int = 100) -> List[Dict]:
        """
        Get historical time-series data for a specific token.

        Args:
            token_address: Token contract address
            chain_id: Blockchain (default: 'bsc')
            limit: Maximum number of snapshots to return (default: 100)

        Returns:
            List of snapshot dicts ordered by time (oldest to newest)
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT
                id, snapshot_at, price_usd, liquidity_usd, volume_24h, price_change_24h,
                buys_24h, sells_24h, main_dex, pair_address, pair_count,
                holder_count, top_holder_percent, concentration_score
            FROM time_series_data
            WHERE token_address = %s AND chain_id = %s
            ORDER BY snapshot_at ASC
            LIMIT %s;
            """

            cursor.execute(query, (token_address, chain_id, limit))
            rows = cursor.fetchall()

            snapshots = []
            for row in rows:
                snapshots.append({
                    'id': row[0],
                    'snapshot_at': row[1],
                    'price_usd': float(row[2]) if row[2] else None,
                    'liquidity_usd': float(row[3]) if row[3] else None,
                'volume_24h': float(row[4]) if row[4] else None,
                    'price_change_24h': float(row[5]) if row[5] else None,
                    'buys_24h': row[6],
                    'sells_24h': row[7],
                    'main_dex': row[8],
                    'pair_address': row[9],
                    'pair_count': row[10],
                    'holder_count': row[11],
                    'top_holder_percent': float(row[12]) if row[12] else None,
                    'concentration_score': float(row[13]) if row[13] else None
                })

            logger.info(f"📊 Retrieved {len(snapshots)} snapshots for {token_address} on {chain_id}")
            cursor.close()
            return snapshots

        except Exception as e:
            logger.error(f"❌ Query error in get_time_series_data: {e}")
            return []
        finally:
            if conn:
                conn.close()
