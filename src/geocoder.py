import time
import requests
from db import get_connection

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "PlanningScraper/1.0 (planning-leads-tool)"}
RATE_LIMIT = 1.1  # seconds between requests (Nominatim ToS: max 1/sec)
BATCH_SIZE = 500  # records per geocoding run


def _geocode_address(address: str):
    """
    Call Nominatim for a single address string.
    Returns (lat, lon) on success, (None, None) on failure.
    """
    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": address + ", UK", "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None, None


def run_geocoding_batch(batch_size: int = BATCH_SIZE, progress_callback=None):
    """
    Geocode up to batch_size unprocessed records.
    progress_callback(current, total) is called after each record if provided.
    Returns (succeeded, failed, remaining) counts.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT reference_no, address FROM applications
                WHERE geocoded = FALSE AND address IS NOT NULL AND address != ''
                LIMIT %s
                """,
                (batch_size,),
            )
            rows = cur.fetchall()

    total = len(rows)
    succeeded = 0
    failed = 0

    for i, row in enumerate(rows):
        ref = row["reference_no"]
        address = row["address"]

        lat, lon = _geocode_address(address)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE applications
                    SET latitude = %s, longitude = %s, geocoded = TRUE
                    WHERE reference_no = %s
                    """,
                    (lat, lon, ref),
                )
            conn.commit()

        if lat is not None:
            succeeded += 1
        else:
            failed += 1

        if progress_callback:
            progress_callback(i + 1, total)

        time.sleep(RATE_LIMIT)

    # Count remaining
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM applications WHERE geocoded = FALSE")
            remaining = cur.fetchone()["n"]

    return succeeded, failed, remaining


def get_geocoding_stats() -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE geocoded = TRUE AND latitude IS NOT NULL)  AS geocoded_ok,
                    COUNT(*) FILTER (WHERE geocoded = TRUE AND latitude IS NULL)      AS geocoded_failed,
                    COUNT(*) FILTER (WHERE geocoded = FALSE)                          AS pending
                FROM applications
            """)
            return dict(cur.fetchone())
