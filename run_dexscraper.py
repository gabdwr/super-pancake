import logging
from src.discovery.dexscraper import Dexscraper
from src.database.supabase import Supabase
from src.utils.telegram_alerts import TelegramAlert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_dexscraper():
    """
    Main function to scrape latest tokens from DexScreener and store in Supabase
    """
    try:
        logger.info("=" * 70)
        logger.info("🚀 Starting DexScreener scrape job...")
        logger.info("=" * 70)

        # Scrape tokens from DexScreener
        scraper = Dexscraper()
        new_tokens = scraper.scraped
        logger.info(f"📊 Found {len(new_tokens)} tokens to process")

        if not new_tokens:
            logger.warning("⚠️  No tokens found. Exiting.")
            return

        # Store in Supabase database
        logger.info("💾 Storing tokens in Supabase...")
        supabase = Supabase()
        stats = supabase.store_discovered_tokens(new_tokens)

        # Log results
        logger.info("=" * 70)
        logger.info("✅ Scrape complete!")
        logger.info(f"   Total processed: {stats['total']}")
        logger.info(f"   New tokens inserted: {stats['inserted']}")
        logger.info(f"   Duplicates skipped: {stats['skipped']}")
        if stats['errors']:
            logger.error(f"   Errors encountered: {len(stats['errors'])}")
            for error in stats['errors'][:3]:  # Show first 3 errors
                logger.error(f"      - {error}")
        logger.info("=" * 70)

        tele = TelegramAlert()
        tele.send_message(f"⛏ Dexscraper run successful!! {stats['inserted']} new tokens logged into supabase!!")

    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"❌ Fatal error in run_dexscraper: {e}")
        logger.error("=" * 70)
        raise


if __name__ == "__main__":
    run_dexscraper()