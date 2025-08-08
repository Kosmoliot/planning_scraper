import logging
from db import get_connection

_logger = None  # ← global cache

class PostgresHandler(logging.Handler):
    def emit(self, record):
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO scraper_logs (level, keyword, url, message)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        record.levelname,
                        getattr(record, "keyword", None),
                        getattr(record, "url", None),
                        self.format(record),
                    )
                )
                conn.commit()
        except Exception as e:
            print(f"Failed to log to PostgreSQL: {e}")
        finally:
            if conn:
                conn.close()

def get_logger():
    logger = logging.getLogger("scraper")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    db_handler = PostgresHandler()
    db_handler.setFormatter(formatter)
    logger.addHandler(db_handler)

    return logger
