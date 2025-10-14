"""
Datafetch + Filtration Script with Smart Caching

This script combines data fetching with critical filter application:
1. Fetches DexScreener metrics (always hourly)
2. Fetches GoPlus data (hourly for new, daily for graduated tokens)
3. Calculates concentration score from pairs data
4. Applies 7 critical filters to tag tokens as PASS/FAIL
5. Updates graduation status (graduate after 5 passes)
6. Stores time-series snapshots
7. Sends instant Telegram alerts for tokens that PASS
8. Sends end-of-run summary

Runs hourly via GitHub Actions (30 min after discovery).
"""

import logging
from datetime import datetime
from src.database.supabase_rest import SupabaseREST
from src.discovery.dexscraper import Dexscraper
from src.discovery.goplus import GoPlus
from src.filters import (
    apply_critical_filters,
    should_fetch_goplus,
    update_graduation_status,
    get_graduation_summary
)
from src.utils.telegram_alerts import TelegramAlert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def send_pass_alert(tele: TelegramAlert, token_address: str, filter_details: dict, dex_data: dict):
    """
    Send instant Telegram alert when a token passes all filters.

    Args:
        tele: TelegramAlert instance
        token_address: Token contract address
        filter_details: Filter result details
        dex_data: DexScreener data with URL
    """
    try:
        liquidity = filter_details.get('liquidity_usd', 0)
        concentration = filter_details.get('concentration_score', 0)
        lp_locked = filter_details.get('lp_locked_percent', 0)
        buy_tax = filter_details.get('buy_tax', 0)
        sell_tax = filter_details.get('sell_tax', 0)

        # Get DexScreener URL from pairs (use main pair)
        pairs = dex_data.get('pairs', [])
        dexscreener_url = None
        if pairs:
            main_pair = max(pairs, key=lambda p: p.get('liquidity', {}).get('usd', 0))
            dexscreener_url = main_pair.get('url')

        message = (
            f"🎯 NEW TOKEN PASSED FILTERS!\n\n"
            f"Token: {token_address[:10]}...{token_address[-6:]}\n"
            f"Liquidity: ${liquidity:,.0f}\n"
            f"Concentration: {concentration:.0f}/100\n"
            f"LP Locked: {lp_locked:.0f}%\n"
            f"Buy Tax: {buy_tax:.1f}% | Sell Tax: {sell_tax:.1f}%\n"
        )

        if dexscreener_url:
            message += f"\n🔗 {dexscreener_url}"

        tele.send_message(message)
        logger.info(f"📨 Sent PASS alert for {token_address}")

    except Exception as e:
        logger.error(f"❌ Error sending PASS alert: {e}")


def run_datafetch_and_filtration():
    """
    Main function: Fetch metrics + apply filters with smart caching.

    Process:
    1. Get all tokens from discovered_tokens table
    2. For each token:
       a. Fetch DexScreener metrics (always - liquidity changes hourly)
       b. Check if GoPlus refresh needed (hourly for new, daily for graduated)
       c. Apply critical filters
       d. Update graduation status
       e. Store time-series snapshot
       f. Send instant alert if PASS
    3. Send end-of-run summary with graduation stats
    """
    try:
        logger.info("🚀 Starting datafetch + filtration for all tokens...")
        current_hour = datetime.now().hour

        # Initialize clients
        supabase = SupabaseREST()
        scraper = Dexscraper()
        goplus = GoPlus()
        tele = TelegramAlert()

        # Get all tokens from database
        all_tokens = supabase.get_all_tokens()
        logger.info(f"✅ Retrieved {len(all_tokens)} tokens from database")

        # Get graduation summary before processing
        grad_summary_before = get_graduation_summary(all_tokens)
        logger.info(
            f"📊 Graduation status: "
            f"{grad_summary_before['graduated']} graduated, "
            f"{grad_summary_before['in_progress']} in progress, "
            f"{grad_summary_before['new']} new"
        )

        # Counters for summary
        successful_fetches = 0
        failed_fetches = 0
        tokens_passed = 0
        tokens_failed = 0
        goplus_api_calls = 0
        goplus_cached = 0
        graduated_count = 0
        demoted_count = 0
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
                # Always fetch DexScreener (liquidity/volume changes frequently)
                dex_data = scraper.fetch_token_metrics(token_address)

                if not dex_data:
                    logger.warning(f"⚠️  No DexScreener data for {token_address}")
                    failed_fetches += 1
                    continue

                # Extract pairs for concentration calculation
                pairs = dex_data.get('pairs', [])

                # Smart GoPlus caching: check if refresh needed
                needs_goplus_refresh = should_fetch_goplus(token, current_hour)

                if needs_goplus_refresh:
                    # Fetch fresh GoPlus data
                    security_data = goplus.fetch_token_security(
                        token_address=token_address,
                        chain_id=chain_id
                    )
                    goplus_api_calls += 1

                    # Update last check timestamp
                    supabase.update_graduation_status(
                        token_address=token_address,
                        graduated=token.get('graduated', False),
                        consecutive_passes=token.get('consecutive_passes', 0),
                        last_goplus_check=datetime.now()
                    )
                else:
                    # Use cached GoPlus data from last snapshot
                    security_data = supabase.get_cached_goplus_data(token_address)
                    goplus_cached += 1

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

                    # Send instant Telegram alert for PASS tokens -- COMMENTED OUT TOO MUCH NOISE
                    # send_pass_alert(tele, token_address, filter_result['details'], dex_data)
                else:
                    tokens_failed += 1
                    # Track failure reasons for summary
                    for reason in filter_reasons:
                        failure_reasons_count[reason] = failure_reasons_count.get(reason, 0) + 1

                logger.info(f"   Filter result: {filter_status}")
                if filter_reasons:
                    logger.info(f"   Reasons: {', '.join(filter_reasons)}")

                # Update graduation status
                graduated, consecutive_passes, action = update_graduation_status(
                    token_address=token_address,
                    current_status={
                        'graduated': token.get('graduated', False),
                        'consecutive_passes': token.get('consecutive_passes', 0)
                    },
                    filter_status=filter_status
                )

                if action == 'GRADUATED':
                    graduated_count += 1
                elif action == 'DEMOTED':
                    demoted_count += 1

                # Save graduation status to database
                supabase.update_graduation_status(
                    token_address=token_address,
                    graduated=graduated,
                    consecutive_passes=consecutive_passes
                )

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

        # Get updated graduation summary
        all_tokens_updated = supabase.get_all_tokens()
        grad_summary_after = get_graduation_summary(all_tokens_updated)

        # Summary
        logger.info("="*70)
        logger.info("✅ Datafetch + Filtration complete!")
        logger.info(f"   Successful: {successful_fetches}/{len(all_tokens)}")
        logger.info(f"   Failed: {failed_fetches}/{len(all_tokens)}")
        logger.info(f"   Passed filters: {tokens_passed}")
        logger.info(f"   Failed filters: {tokens_failed}")
        logger.info(f"   GoPlus API calls: {goplus_api_calls}")
        logger.info(f"   GoPlus cached: {goplus_cached}")
        logger.info(f"   New graduations: {graduated_count}")
        logger.info(f"   Demotions: {demoted_count}")
        logger.info("="*70)

        # Top 5 failure reasons
        if failure_reasons_count:
            logger.info("Top failure reasons:")
            sorted_reasons = sorted(failure_reasons_count.items(), key=lambda x: x[1], reverse=True)
            for reason, count in sorted_reasons[:5]:
                logger.info(f"   {reason}: {count} tokens")

        # Build failure reasons summary for Telegram
        failure_summary = ""
        if failure_reasons_count:
            sorted_reasons = sorted(failure_reasons_count.items(), key=lambda x: x[1], reverse=True)
            failure_summary = "\n\nTop failure reasons:\n"
            for reason, count in sorted_reasons[:3]:  # Top 3 for brevity
                failure_summary += f"• {reason}: {count}\n"

        # Build graduation summary for Telegram
        graduation_summary = (
            f"\n🎓 Graduation System:\n"
            f"• Graduated: {grad_summary_after['graduated']} "
            f"(+{grad_summary_after['graduated'] - grad_summary_before['graduated']})\n"
            f"• In Progress: {grad_summary_after['in_progress']}\n"
            f"• GoPlus calls: {goplus_api_calls} (saved {goplus_cached})\n"
            f"• Est. daily calls: ~{grad_summary_after['estimated_daily_goplus_calls']}"
        )

        # Send end-of-run Telegram summary
        tele.send_message(
            f"✌️ Datafetch + Filtration complete!\n\n"
            f"📊 Total: {len(all_tokens)} tokens\n"
            f"✅ Successful: {successful_fetches}\n"
            f"❌ Failed: {failed_fetches}\n\n"
            f"🎯 Filter Results:\n"
            f"✅ PASS: {tokens_passed}\n"
            f"❌ FAIL: {tokens_failed}"
            f"{failure_summary}"
            f"{graduation_summary}"
        )

    except Exception as e:
        logger.error(f"❌ Fatal error in run_datafetch_and_filtration: {e}")
        raise


if __name__ == "__main__":
    run_datafetch_and_filtration()
