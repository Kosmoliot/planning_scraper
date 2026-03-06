"""
Standalone geocoding worker — runs as a separate process.
Continuously processes pending records, sleeps when caught up.
Add to Procfile as:
    worker: python src/geocode_worker.py
"""
import os
import sys
import time
import logging

sys.path.insert(0, os.path.dirname(__file__))

if os.getenv("RAILWAY_ENVIRONMENT") is None:
    from dotenv import load_dotenv
    load_dotenv()

from geocoder import run_geocoding_batch, get_geocoding_stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] geocode_worker: %(message)s",
    handlers=[logging.StreamHandler()]
)

BATCH_SIZE   = 500   # records per iteration (keeps memory low)
POLL_SECONDS = 60    # wait time when no pending records


def main():
    logging.info("Worker started.")
    while True:
        stats = get_geocoding_stats()

        if stats["pending"] == 0:
            logging.info(f"All records geocoded. Sleeping {POLL_SECONDS}s...")
            time.sleep(POLL_SECONDS)
            continue

        logging.info(f"{stats['pending']:,} records pending — processing batch of {BATCH_SIZE}...")
        ok, fail, remaining = run_geocoding_batch(batch_size=BATCH_SIZE)
        logging.info(f"Batch done: {ok} geocoded, {fail} failed, {remaining:,} remaining.")

        # No sleep between batches — keep going until caught up


if __name__ == "__main__":
    main()
