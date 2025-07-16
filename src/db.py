import os
import psycopg2
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

def fetch_filtered_results(start_date, end_date, websites, keywords):
    """
    Fetch results from the database filtered by:
    - validated_date BETWEEN start_date AND end_date
    - website IN (websites list)
    - search_word IN (keywords list)
    """
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT reference_no, validated_date, status, address, summary, website, search_word, scraped_at, full_link
            FROM applications
            WHERE validated_date BETWEEN %s AND %s
              AND website = ANY(%s)
              AND search_word = ANY(%s)
            ORDER BY validated_date DESC;
        """, (start_date, end_date, websites, keywords))
        results = cur.fetchall()
    conn.close()
    return results
