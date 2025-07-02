#   db.py

import os
import psycopg2

def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")

def insert_new_rows(df):
    conn = get_connection()
    cur = conn.cursor()
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO applications (
                reference_no, website, search_word,
                validated_date, status, address, summary
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (reference_no) DO NOTHING;
        """, (
            row["Reference No"], row["Website"], row["Search Word"],
            row["Validated Date"], row["Status"],
            row["Address"], row["Summary"]
        ))
    conn.commit()
    cur.close()
    conn.close()

