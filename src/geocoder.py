import re
import time
import requests
from db import get_connection

NOMINATIM_URL  = "https://nominatim.openstreetmap.org/search"
POSTCODES_URL  = "https://api.postcodes.io/postcodes/{}"
HEADERS        = {"User-Agent": "PlanningScraper/1.0 (planning-leads-tool)"}
RATE_LIMIT     = 1.1   # seconds — Nominatim ToS: max 1 req/sec
BATCH_SIZE     = 500

_POSTCODE_RE   = re.compile(r'[A-Z]{1,2}[0-9][0-9A-Z]?\s?[0-9][A-Z]{2}', re.IGNORECASE)


# ── Stage 1: Nominatim full address ──────────────────────────────────────────

def _nominatim(address: str):
    """
    Returns (lat, lon) on success, (None, None) on failure.
    Raises on network/HTTP errors so the caller can log the reason.
    """
    resp = requests.get(
        NOMINATIM_URL,
        params={
            "q":            address,
            "format":       "json",
            "limit":        1,
            "countrycodes": "gb",
        },
        headers=HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None, None


# ── Stage 2: postcodes.io postcode centroid ───────────────────────────────────

def _extract_postcode(address: str):
    m = _POSTCODE_RE.search(address)
    return m.group(0).replace(" ", "").upper() if m else None


def _postcodes_io(postcode: str):
    """
    Returns (lat, lon) on success, (None, None) if postcode not found.
    Raises on network errors.
    """
    resp = requests.get(POSTCODES_URL.format(postcode), timeout=10)
    if resp.status_code == 404:
        return None, None
    resp.raise_for_status()
    result = resp.json().get("result", {})
    if result:
        return float(result["latitude"]), float(result["longitude"])
    return None, None


# ── Two-stage pipeline ────────────────────────────────────────────────────────

def _geocode(address: str):
    """
    Returns (lat, lon, source, error).
    source: 'nominatim' | 'postcode' | None
    error:  None on success, reason string on failure
    """
    # Stage 1 — full address via Nominatim
    try:
        lat, lon = _nominatim(address)
        if lat is not None:
            return lat, lon, "nominatim", None
        stage1_error = "[Stage 1 FAILED] Nominatim returned no results for full address"
    except requests.exceptions.Timeout:
        stage1_error = "[Stage 1 FAILED] Nominatim request timed out"
    except requests.exceptions.HTTPError as e:
        stage1_error = f"[Stage 1 FAILED] Nominatim HTTP error {e.response.status_code}"
    except Exception as e:
        stage1_error = f"[Stage 1 FAILED] Nominatim unexpected error: {e}"

    time.sleep(RATE_LIMIT)  # respect rate limit before fallback

    # Stage 2 — postcode centroid via postcodes.io
    postcode = _extract_postcode(address)
    if not postcode:
        return None, None, None, f"{stage1_error} | [Stage 2 FAILED] No valid UK postcode found in address"

    try:
        lat, lon = _postcodes_io(postcode)
        if lat is not None:
            return lat, lon, "postcode", None
        return None, None, None, f"{stage1_error} | [Stage 2 FAILED] postcodes.io: postcode {postcode} not recognised"
    except requests.exceptions.Timeout:
        return None, None, None, f"{stage1_error} | [Stage 2 FAILED] postcodes.io request timed out"
    except Exception as e:
        return None, None, None, f"{stage1_error} | [Stage 2 FAILED] postcodes.io unexpected error: {e}"


# ── Batch runner ──────────────────────────────────────────────────────────────

def run_geocoding_batch(batch_size=BATCH_SIZE, progress_callback=None):
    """
    Geocode pending records using two-stage pipeline.
    Returns (succeeded, failed, remaining).
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = (
                "SELECT reference_no, address FROM applications "
                "WHERE geocoded = FALSE AND address IS NOT NULL AND address != ''"
            )
            if batch_size is not None:
                query += " LIMIT %s"
                cur.execute(query, (batch_size,))
            else:
                cur.execute(query)
            rows = cur.fetchall()

    total     = len(rows)
    succeeded = 0
    failed    = 0

    for i, row in enumerate(rows):
        ref     = row["reference_no"]
        address = row["address"]

        lat, lon, source, error = _geocode(address)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE applications
                    SET latitude = %s, longitude = %s,
                        geocoded = TRUE,
                        geocode_source = %s,
                        geocode_error  = %s
                    WHERE reference_no = %s
                    """,
                    (lat, lon, source, error, ref),
                )
            conn.commit()

        if lat is not None:
            succeeded += 1
        else:
            failed += 1

        if progress_callback:
            progress_callback(i + 1, total)

        time.sleep(RATE_LIMIT)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM applications WHERE geocoded = FALSE")
            remaining = cur.fetchone()["n"]

    return succeeded, failed, remaining


# ── Stats ─────────────────────────────────────────────────────────────────────

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
