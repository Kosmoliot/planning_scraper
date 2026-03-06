import logging
from db import get_connection

class PostgresHandler(logging.Handler):
    def emit(self, record):
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO scraper_logs (level, keyword, url, message) VALUES (%s, %s, %s, %s)",
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

def get_logger():
    logger = logging.getLogger("scraper")
    if logger.hasHandlers():
        return logger  # already configured, avoid rebuilding handlers on every call

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    db_handler = PostgresHandler()
    db_handler.setFormatter(formatter)
    logger.addHandler(db_handler)

    return logger
