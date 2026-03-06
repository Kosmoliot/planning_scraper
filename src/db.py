import os
import re
import psycopg2
import psycopg2.pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

if os.getenv("RAILWAY_ENVIRONMENT") is None:
    from dotenv import load_dotenv
    load_dotenv()

_pool = None

def _get_pool():
    global _pool
    if _pool is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL environment variable is not set")
        _pool = psycopg2.pool.ThreadedConnectionPool(1, 10, db_url, cursor_factory=RealDictCursor)
    return _pool

@contextmanager
def get_connection():
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

def fetch_results(start_date, end_date, websites=None, search_words=None,
                  summary_keywords=None, statuses=None, geocoded_only=False, match_all=False):
    """
    Fetch planning applications with optional filters:
      - websites: filter by website column
      - search_words: filter by search_word column (exact match)
      - summary_keywords: list of terms to search within summary (ILIKE)
      - statuses: list of normalised status values to include
      - geocoded_only: only return rows with valid lat/lng
      - match_all: True = AND between summary terms, False = OR
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT reference_no, validated_date, status, address, summary,
                       website, search_word, scraped_at, full_link, latitude, longitude
                FROM applications
                WHERE validated_date BETWEEN %s AND %s
            """
            params = [start_date, end_date]

            if websites:
                query += " AND website = ANY(%s)"
                params.append(websites)

            if search_words:
                query += " AND search_word = ANY(%s)"
                params.append(search_words)

            if statuses:
                query += " AND status = ANY(%s)"
                params.append(statuses)

            if geocoded_only:
                query += " AND geocoded = TRUE AND latitude IS NOT NULL"

            if summary_keywords:
                op = " AND " if match_all else " OR "
                like_clauses = op.join(["summary ILIKE %s"] * len(summary_keywords))
                query += f" AND ({like_clauses})"
                params.extend([f"%{t}%" for t in summary_keywords])

            query += " ORDER BY validated_date DESC;"
            cur.execute(query, tuple(params))
            return cur.fetchall()

def fetch_failed_urls():
    """Return failed URLs from the most recent scrape session (by date)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                WITH last_run AS (
                    SELECT DATE(MAX(timestamp)) AS run_date
                    FROM scraper_logs
                )
                SELECT DISTINCT url, message, timestamp
                FROM scraper_logs, last_run
                WHERE level = 'ERROR'
                  AND url IS NOT NULL
                  AND DATE(timestamp) = last_run.run_date
                ORDER BY timestamp DESC
            """)
            return cur.fetchall()
