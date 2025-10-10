import psycopg2
from dotenv import load_dotenv
import os
import logging
from typing import List, Dict
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
            connection = psycopg2.connect(
                user=self.user,
                password=self.password,
                host=self.host,
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
