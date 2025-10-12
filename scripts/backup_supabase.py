#!/usr/bin/env python3
"""
Supabase Database Backup Script
Exports all tables to JSON files for GitHub backup
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.supabase_rest import SupabaseREST

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def backup_supabase_to_json():
    """
    Export all Supabase tables to timestamped JSON files

    Creates:
    - backups/discovered_tokens_YYYYMMDD_HHMMSS.json
    - backups/time_series_latest_YYYYMMDD_HHMMSS.json
    - backups/backup_info_YYYYMMDD_HHMMSS.json (metadata)
    """
    try:
        logger.info("🚀 Starting Supabase backup...")

        # Initialize Supabase client
        supabase = SupabaseREST()

        # Create backups directory
        backup_dir = Path(__file__).parent.parent / "backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # =====================================================================
        # Backup 1: discovered_tokens (all tokens)
        # =====================================================================
        logger.info("📦 Backing up discovered_tokens table...")
        tokens = supabase.get_all_tokens()

        tokens_file = backup_dir / f"discovered_tokens_{timestamp}.json"
        with open(tokens_file, 'w') as f:
            json.dump(tokens, f, indent=2, default=str)

        logger.info(f"✅ Backed up {len(tokens)} tokens to {tokens_file.name}")

        # =====================================================================
        # Backup 2: time_series_data (latest snapshot per token)
        # Note: Full time_series would be huge, so we only backup latest
        # =====================================================================
        logger.info("📦 Backing up time_series_data (latest snapshots)...")

        # Get latest snapshot for each token using Supabase REST API
        # We'll make individual queries per token (inefficient but works)
        latest_snapshots = []

        for token in tokens:
            token_address = token.get('token_address')
            chain_id = token.get('chain_id')

            if not token_address:
                continue

            # Query latest snapshot for this token
            url = f"{supabase.base_url}/time_series_data"
            params = {
                'select': '*',
                'token_address': f'eq.{token_address}',
                'chain_id': f'eq.{chain_id}',
                'order': 'snapshot_at.desc',
                'limit': 1
            }

            try:
                response = supabase._make_get_request(url, params)
                if response and len(response) > 0:
                    latest_snapshots.append(response[0])
            except Exception as e:
                logger.warning(f"Failed to fetch time_series for {token_address}: {e}")
                continue

        timeseries_file = backup_dir / f"time_series_latest_{timestamp}.json"
        with open(timeseries_file, 'w') as f:
            json.dump(latest_snapshots, f, indent=2, default=str)

        logger.info(f"✅ Backed up {len(latest_snapshots)} time-series snapshots to {timeseries_file.name}")

        # =====================================================================
        # Backup metadata
        # =====================================================================
        metadata = {
            'backup_timestamp': timestamp,
            'backup_date': datetime.now().isoformat(),
            'discovered_tokens_count': len(tokens),
            'time_series_snapshots_count': len(latest_snapshots),
            'files': {
                'discovered_tokens': tokens_file.name,
                'time_series_latest': timeseries_file.name
            }
        }

        metadata_file = backup_dir / f"backup_info_{timestamp}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"✅ Backup metadata saved to {metadata_file.name}")

        # =====================================================================
        # Summary
        # =====================================================================
        logger.info("="*70)
        logger.info("✅ Backup complete!")
        logger.info(f"   📁 Directory: {backup_dir}")
        logger.info(f"   📊 Tokens: {len(tokens)}")
        logger.info(f"   📈 Time-series snapshots: {len(latest_snapshots)}")
        logger.info(f"   📝 Files created:")
        logger.info(f"      - {tokens_file.name}")
        logger.info(f"      - {timeseries_file.name}")
        logger.info(f"      - {metadata_file.name}")
        logger.info("="*70)

        return True

    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        raise


def _make_get_request_helper():
    """Helper to add GET request method to SupabaseREST if not exists"""
    import requests

    def _make_get_request(self, url, params):
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None

    # Monkey patch the method
    SupabaseREST._make_get_request = _make_get_request


if __name__ == "__main__":
    # Add helper method
    _make_get_request_helper()

    # Run backup
    try:
        backup_supabase_to_json()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
