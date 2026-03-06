import logging
from datetime import datetime
from scraper import scrape_all_sites
from store import get_all_urls, get_all_keywords
from geocoder import run_geocoding_batch


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scheduled_scrape.log"),
        logging.StreamHandler()
    ]
)

def run_scheduled_scrape():
    urls = get_all_urls()
    keywords = get_all_keywords()

    if not urls or not keywords:
        logging.warning("No URLs or keywords found in DB.")
        return

    logging.info(f"Running scheduled scrape for {len(urls)} URLs and {len(keywords)} keywords.")

    successes, failures = scrape_all_sites(urls, keywords)

    logging.info(f"Scraping complete. Successes: {len(successes)}, Failures: {len(failures)}")

    if failures:
        for item, error in failures:
            logging.warning(f"Failed: {item} → {error}")

    logging.info("Scheduled scraping run finished at %s", datetime.utcnow())

    # Geocode any new records added by this scrape
    logging.info("Starting geocoding batch for new records...")
    ok, fail, remaining = run_geocoding_batch()
    logging.info(f"Geocoding complete. Succeeded: {ok}, Failed: {fail}, Remaining: {remaining}")

if __name__ == "__main__":
    run_scheduled_scrape()