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
