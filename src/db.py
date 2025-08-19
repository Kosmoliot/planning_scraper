import os
import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor

# Load .env locally (Railway injects DATABASE_URL automatically)
if os.getenv("RAILWAY_ENVIRONMENT") is None:
    from dotenv import load_dotenv
    load_dotenv()

def get_connection():
    return psycopg2.connect(
        os.getenv("DATABASE_URL"),
        cursor_factory=RealDictCursor
    )

def fetch_filtered_results(start_date, end_date, websites, keywords, summary_search=None, match_all=False):
    """
    Filters:
      - validated_date BETWEEN start_date AND end_date (always)
      - website IN websites (if provided)
      - search_word IN keywords (if provided)
      - summary contains words from summary_search (if provided)
        * match_all=False -> OR between words
        * match_all=True  -> AND between words
    """
    conn = get_connection()
    results = []
    try:
        with conn.cursor() as cur:
            query = """
                SELECT reference_no, validated_date, status, address, summary, website, search_word, scraped_at, full_link
                FROM applications
                WHERE validated_date BETWEEN %s AND %s
            """
            params = [start_date, end_date]

            if websites:
                query += " AND website = ANY(%s)"
                params.append(websites)

            if keywords:
                query += " AND search_word = ANY(%s)"
                params.append(keywords)

            # --- NEW: summary search ---
            terms = []
            if summary_search:
                # split on whitespace/commas; keep non-empty terms
                import re
                terms = [t for t in re.split(r"[,\s]+", summary_search.strip()) if t]

            if terms:
                # Build "(summary ILIKE %s [AND/OR] summary ILIKE %s ...)"
                op = " AND " if match_all else " OR "
                like_clauses = op.join(["summary ILIKE %s"] * len(terms))
                query += f" AND ({like_clauses})"
                params.extend([f"%{t}%" for t in terms])

            query += " ORDER BY validated_date DESC;"
            cur.execute(query, tuple(params))
            results = cur.fetchall()
    finally:
        conn.close()

    return results

def fetch_results_by_summary(start_date, end_date, websites, keywords):
    """
    Fetch results from the database filtered by:
    - validated_date BETWEEN start_date AND end_date
    - website IN (websites list)
    - summary contains ANY of the keywords
    """
    conn = get_connection()
    with conn.cursor() as cur:
        query = """
            SELECT reference_no, validated_date, status, address, summary, website, search_word, scraped_at, full_link
            FROM applications
            WHERE validated_date BETWEEN %s AND %s
              AND website = ANY(%s)
        """
        params = [start_date, end_date, websites]

        if keywords:
            keyword_clauses = " OR ".join(["summary ILIKE %s"] * len(keywords))
            query += f" AND ({keyword_clauses})"
            params.extend([f"%{kw}%" for kw in keywords])

        query += " ORDER BY validated_date DESC;"
        cur.execute(query, tuple(params))
        results = cur.fetchall()

    conn.close()
    return results

def fetch_failed_urls():
    """
    Debug version: Returns a pandas DataFrame with all distinct URLs
    that failed today. Also prints sample output for debugging.
    """
    conn = get_connection()
    with conn.cursor() as cur:
        query = """
            SELECT DISTINCT url
            FROM scraper_logs
            WHERE level = 'ERROR' 
            AND URL IS NOT NULL
            AND DATE(timestamp) = CURRENT_DATE
        """

        
        cur.execute(query)
        results = cur.fetchall()

    conn.close()
    return results
