import logging
from src.database.supabase_rest import SupabaseREST
from src.discovery.dexscraper import Dexscraper
from src.discovery.goplus import GoPlus
from src.utils.telegram_alerts import TelegramAlert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_datafetch():
    """
    Main function to pull data points for all supabase tokens and store in Supabase.

    Fetches:
    - DexScreener metrics (price, volume, liquidity, transactions)
    - GoPlus security data (holder count, taxes, honeypot flags, ownership)
    """
    try:
        logger.info("🚀 Starting data fetch for all tokens...")

        # Initialize clients
        supabase = SupabaseREST()
        scraper = Dexscraper()
        goplus = GoPlus()

        # Get all tokens from database
        all_tokens = supabase.get_all_tokens()
        logger.info(f"✅ Retrieved {len(all_tokens)} tokens from database")

        # Fetch data for each token
        successful_fetches = 0
        failed_fetches = 0

        for idx, token in enumerate(all_tokens, 1):
            token_address = token.get('token_address')
            chain_id = token.get('chain_id', 'bsc')

            if not token_address:
                logger.warning(f"❌ No token_address found for token: {token}")
                failed_fetches += 1
                continue

            logger.info(f"📊 Processing token {idx}/{len(all_tokens)}: {token_address} ({chain_id})")

            try:
                # Fetch DexScreener metrics
                dex_data = scraper.fetch_token_metrics(token_address)

                if not dex_data:
                    logger.warning(f"⚠️  No DexScreener data for {token_address}")
                    failed_fetches += 1
                    continue

                # Fetch GoPlus security data
                security_data = goplus.fetch_token_security(
                    token_address=token_address,
                    chain_id=chain_id
                )

                # Merge DexScreener + GoPlus data
                if security_data:
                    merged_data = {**dex_data, **security_data}
                    logger.info(f"✅ Merged DexScreener + GoPlus data for {token_address}")
                else:
                    logger.warning(f"⚠️  No GoPlus data for {token_address}, using DexScreener only")
                    merged_data = dex_data

                # Store in Supabase
                success = supabase.store_time_series_data(
                    metrics_data=merged_data,
                    token_address=token_address,
                    chain_id=chain_id
                )

                if success:
                    successful_fetches += 1
                else:
                    failed_fetches += 1

            except Exception as e:
                logger.error(f"❌ Error processing {token_address}: {e}")
                failed_fetches += 1
                continue

        # Summary
        logger.info("="*70)
        logger.info("✅ Datafetch complete!")
        logger.info(f"   Successful: {successful_fetches}/{len(all_tokens)}")
        logger.info(f"   Failed: {failed_fetches}/{len(all_tokens)}")
        logger.info("="*70)

        # Send Telegram notification
        tele = TelegramAlert()
        tele.send_message(
            f"✌️ Datafetch complete!\n"
            f"✅ Success: {successful_fetches}\n"
            f"❌ Failed: {failed_fetches}\n"
            f"📊 Total: {len(all_tokens)} tokens"
        )

    except Exception as e:
        logger.error(f"❌ Fatal error in run_datafetch: {e}")
        raise


if __name__ == "__main__":
    run_datafetch()