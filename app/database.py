import os
from pathlib import Path
import psycopg


def connect():
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "db"),
        dbname=os.environ.get("DB_NAME", "notes"),
        user=os.environ.get("DB_USER", "lab"),
        password=Path(os.environ["DB_PASSWORD_FILE"]).read_text().strip(),
        connect_timeout=3,
        options="-c statement_timeout=5000",
    )
