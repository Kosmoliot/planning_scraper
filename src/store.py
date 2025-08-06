from db import get_connection
from psycopg2.extras import execute_values
from datetime import datetime

def store_results(results):
    if not results:
        return

    conn = get_connection()
    cursor = conn.cursor()

    now = datetime.utcnow()

    values = [
        (
            app['Reference No'],
            app['Validated Date'],
            app['Status'],
            app['Address'],
            app['Summary'],
            app['Website'],
            app['Search Word'],
            app['Link'],
            now  # scraped_at value
        )
        for app in results
    ]

    query = """
    INSERT INTO applications (
        reference_no,
        validated_date,
        status,
        address,
        summary,
        website,
        search_word,
        full_link,
        scraped_at
        
    )
    VALUES %s
    ON CONFLICT (reference_no) DO NOTHING;
    """

    execute_values(cursor, query, values)
    conn.commit()
    cursor.close()
    conn.close()

def store_keyword(keyword: str):
    keyword = keyword.lower()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO searched_keywords (keyword)
                SELECT %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM searched_keywords WHERE keyword = %s
                )
            """, (keyword, keyword))  # <- keyword used twice
        conn.commit()

def store_url(url: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO searched_urls (url)
                SELECT %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM searched_urls WHERE url = %s
                )
            """, (url, url))  # <- url used twice
        conn.commit()

def get_all_keywords():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT keyword FROM searched_keywords")
            rows = cur.fetchall()
    return [row["keyword"] for row in rows]

def get_all_urls():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT url FROM searched_urls")
            rows = cur.fetchall()
    return [row["url"] for row in rows]