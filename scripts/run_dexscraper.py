from src.discovery.dexscraper import Dexscraper
from src.database.supabase import Supabase

def run_dexscraper():
    scraper = Dexscraper()
    new_tokens = scraper.scraped
    supabase = Supabase()
    supabase.store_discovered_tokens(new_tokens)

if __name__ == "__main__":
    run_dexscraper()