"""
Datafetch + Filtration Script

This script combines data fetching with critical filter application:
1. Fetches DexScreener + GoPlus metrics for all tokens
2. Calculates concentration score from pairs data
3. Applies 7 critical filters to tag tokens as PASS/FAIL
4. Stores time-series snapshots + updates filter status
5. Sends Telegram summary with filter results

Runs hourly via GitHub Actions (30 min after discovery).
"""

import logging
from src.database.supabase_rest import SupabaseREST
from src.discovery.dexscraper import Dexscraper
from src.discovery.goplus import GoPlus
from src.filters.critical_filters import apply_critical_filters
from src.utils.telegram_alerts import TelegramAlert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_datafetch_and_filtration():
    """
    Main function: Fetch metrics + apply filters for all tokens.

    Process:
    1. Get all tokens from discovered_tokens table
    2. For each token:
       a. Fetch DexScreener metrics (includes pairs for concentration)
       b. Fetch GoPlus security data
       c. Apply critical filters
       d. Store time-series snapshot
       e. Update filter_status in discovered_tokens
    3. Send Telegram summary
    """
    try:
        logger.info("🚀 Starting datafetch + filtration for all tokens...")

        # Initialize clients
        supabase = SupabaseREST()
        scraper = Dexscraper()
        goplus = GoPlus()

        # Get all tokens from database
        all_tokens = supabase.get_all_tokens()
        logger.info(f"✅ Retrieved {len(all_tokens)} tokens from database")

        # Counters for summary
        successful_fetches = 0
        failed_fetches = 0
        tokens_passed = 0
        tokens_failed = 0
        failure_reasons_count = {}

        for idx, token in enumerate(all_tokens, 1):
            token_address = token.get('token_address')
            chain_id = token.get('chain_id', 'bsc')

            if not token_address:
                logger.warning(f"❌ No token_address found for token: {token}")
                failed_fetches += 1
                continue

            logger.info(f"📊 Processing token {idx}/{len(all_tokens)}: {token_address} ({chain_id})")

            try:
                # Fetch DexScreener metrics (includes pairs)
                dex_data = scraper.fetch_token_metrics(token_address)

                if not dex_data:
                    logger.warning(f"⚠️  No DexScreener data for {token_address}")
                    failed_fetches += 1
                    continue

                # Extract pairs for concentration calculation
                pairs = dex_data.get('pairs', [])

                # Fetch GoPlus security data
                security_data = goplus.fetch_token_security(
                    token_address=token_address,
                    chain_id=chain_id
                )

                # Apply critical filters
                filter_result = apply_critical_filters(
                    goplus_data=security_data or {},
                    dexscreener_data=dex_data,
                    pairs=pairs
                )

                filter_status = filter_result['status']
                filter_reasons = filter_result['reasons']

                # Update counters
                if filter_status == 'PASS':
                    tokens_passed += 1
                else:
                    tokens_failed += 1
                    # Track failure reasons for summary
                    for reason in filter_reasons:
                        failure_reasons_count[reason] = failure_reasons_count.get(reason, 0) + 1

                logger.info(f"   Filter result: {filter_status}")
                if filter_reasons:
                    logger.info(f"   Reasons: {', '.join(filter_reasons)}")

                # Merge DexScreener + GoPlus data for storage
                if security_data:
                    merged_data = {**dex_data, **security_data}
                    logger.info(f"✅ Merged DexScreener + GoPlus data for {token_address}")
                else:
                    logger.warning(f"⚠️  No GoPlus data for {token_address}, using DexScreener only")
                    merged_data = dex_data

                # Add filter details to merged data for time-series storage
                merged_data['filter_status'] = filter_status
                merged_data['filter_fail_reasons'] = filter_reasons
                merged_data['concentration_score'] = filter_result['details']['concentration_score']

                # Store time-series snapshot in Supabase (includes filter status)
                success = supabase.store_time_series_data(
                    metrics_data=merged_data,
                    token_address=token_address,
                    chain_id=chain_id
                )

                if success:
                    successful_fetches += 1
                else:
                    failed_fetches += 1
                    logger.warning(f"⚠️  Failed to store time-series data for {token_address}")

            except Exception as e:
                logger.error(f"❌ Error processing {token_address}: {e}")
                failed_fetches += 1
                continue

        # Summary
        logger.info("="*70)
        logger.info("✅ Datafetch + Filtration complete!")
        logger.info(f"   Successful: {successful_fetches}/{len(all_tokens)}")
        logger.info(f"   Failed: {failed_fetches}/{len(all_tokens)}")
        logger.info(f"   Passed filters: {tokens_passed}")
        logger.info(f"   Failed filters: {tokens_failed}")
        logger.info("="*70)

        # Top 5 failure reasons
        if failure_reasons_count:
            logger.info("Top failure reasons:")
            sorted_reasons = sorted(failure_reasons_count.items(), key=lambda x: x[1], reverse=True)
            for reason, count in sorted_reasons[:5]:
                logger.info(f"   {reason}: {count} tokens")

        # Send Telegram notification
        tele = TelegramAlert()

        # Build failure reasons summary for Telegram
        failure_summary = ""
        if failure_reasons_count:
            sorted_reasons = sorted(failure_reasons_count.items(), key=lambda x: x[1], reverse=True)
            failure_summary = "\n\nTop failure reasons:\n"
            for reason, count in sorted_reasons[:3]:  # Top 3 for brevity
                failure_summary += f"• {reason}: {count}\n"

        tele.send_message(
            f"✌️ Datafetch + Filtration complete!\n\n"
            f"📊 Total: {len(all_tokens)} tokens\n"
            f"✅ Successful: {successful_fetches}\n"
            f"❌ Failed: {failed_fetches}\n\n"
            f"🎯 Filter Results:\n"
            f"✅ PASS: {tokens_passed}\n"
            f"❌ FAIL: {tokens_failed}"
            f"{failure_summary}"
        )

    except Exception as e:
        logger.error(f"❌ Fatal error in run_datafetch_and_filtration: {e}")
        raise


if __name__ == "__main__":
    run_datafetch_and_filtration()
