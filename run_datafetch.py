import logging
from src.database.supabase import Supabase
from src.database.supabase_rest import SupabaseREST
from src.discovery.dexscraper import Dexscraper
from src.utils.telegram_alerts import TelegramAlert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_datafetch():
    """
    Main function to pull data points for all supabase tokens and store in Supabase
    """
    try:
        logger.info("🚀 Starting data fetch for all tokens...")

        # Pull entire supabase
        # supabase = Supabase()
        supabase = SupabaseREST()
        all_tokens = supabase.get_all_tokens()
        logger.info(f"✅ Retrieved {len(all_tokens)} tokens.")

        # Fetch data from Dexscanner
        scraper = Dexscraper()
        all_fetched_data = []
        for token in all_tokens:
            token_address = token['token_address']
            if token_address:
                fetched_data = scraper.fetch_token_metrics(token_address)
                all_fetched_data.append(fetched_data)
                
                # Store in Supabase database
                supabase.store_time_series_data(
                    metrics_data=fetched_data,
                    token_address=token['token_address'],
                    chain_id=token['chain_id']
                )
            else:
                logger.info(f"❌ No token_address found for token: {token}")
        logger.info(f"📊 Fetched data for {len(all_fetched_data)} tokens and stored in Supabase")

        # Send update into telegram
        tele = TelegramAlert()
        tele.send_message(f"✌️ Datafetcher successfully run!! {len(all_fetched_data)} token data rows logged into supabase!!")

    except Exception as e:
        logger.error(f"❌ Fatal error in run_dexscraper: {e}")
        raise


if __name__ == "__main__":
    run_datafetch()