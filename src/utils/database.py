"""PostgreSQL database connection utilities."""

import os
import re

import psycopg2
from dotenv import load_dotenv

from src.utils.logging_config import get_logger

logger = get_logger(__name__)

load_dotenv()

RAW_TABLE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def get_connection():
    """Return a psycopg2 connection using environment variables."""
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "seattle_rental"),
        user=os.getenv("POSTGRES_USER", "rental_user"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
    )
    logger.info("Connected to PostgreSQL: %s@%s:%s/%s",
                os.getenv("POSTGRES_USER", "rental_user"),
                os.getenv("POSTGRES_HOST", "localhost"),
                os.getenv("POSTGRES_PORT", "5432"),
                os.getenv("POSTGRES_DB", "seattle_rental"))
    return conn


def validate_table_name(name: str) -> str:
    """Validate that a table name is safe for use in SQL."""
    if not RAW_TABLE_PATTERN.match(name):
        raise ValueError(f"Invalid table name: {name!r}")
    return name


def ensure_raw_table(conn, table_name: str):
    """Create a JSONB raw table if it does not exist."""
    safe_name = validate_table_name(table_name)
    with conn.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS raw.{safe_name} (
                id              SERIAL PRIMARY KEY,
                source_dataset  TEXT NOT NULL,
                ingested_at     TIMESTAMP NOT NULL DEFAULT NOW(),
                raw_record      JSONB NOT NULL
            );
        """)
    conn.commit()
    logger.info("Ensured raw.%s exists", safe_name)


def ensure_schemas(conn, raw_tables: list[str] | None = None):
    """Create the raw schema, pipeline_audit, and any raw tables from config."""
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw.pipeline_audit (
                id              SERIAL PRIMARY KEY,
                dataset_name    TEXT NOT NULL,
                started_at      TIMESTAMP NOT NULL,
                completed_at    TIMESTAMP,
                status          TEXT NOT NULL DEFAULT 'running',
                rows_extracted  INTEGER DEFAULT 0,
                rows_loaded     INTEGER DEFAULT 0,
                raw_file_path   TEXT,
                error_message   TEXT
            );
        """)
    conn.commit()
    logger.info("Ensured raw schema and pipeline_audit table exist")

    if raw_tables:
        for table_name in raw_tables:
            ensure_raw_table(conn, table_name)
