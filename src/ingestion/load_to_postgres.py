"""Load extracted raw data into PostgreSQL."""

from datetime import datetime, timezone

from psycopg2.extras import Json

from src.utils.database import ensure_schemas, get_connection
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def load_records_to_raw(conn, records: list[dict], dataset_name: str, raw_table: str) -> int:
    """Insert raw records as JSONB rows into the specified raw table."""
    if not records:
        logger.warning("No records to load for %s", dataset_name)
        return 0

    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM raw.{raw_table};")
        logger.info("Cleared existing rows from raw.%s", raw_table)

        insert_sql = f"""
            INSERT INTO raw.{raw_table} (source_dataset, ingested_at, raw_record)
            VALUES (%s, %s, %s)
        """
        now = datetime.now(timezone.utc)
        for record in records:
            cur.execute(insert_sql, (dataset_name, now, Json(record)))

    conn.commit()
    logger.info("Loaded %d records into raw.%s", len(records), raw_table)
    return len(records)


def start_audit(conn, dataset_name: str) -> int:
    """Insert a pipeline_audit row with status='running'. Returns the audit id."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw.pipeline_audit (dataset_name, started_at, status)
            VALUES (%s, %s, 'running')
            RETURNING id
            """,
            (dataset_name, datetime.now(timezone.utc)),
        )
        audit_id = cur.fetchone()[0]
    conn.commit()
    return audit_id


def complete_audit(
    conn,
    audit_id: int,
    status: str,
    rows_extracted: int,
    rows_loaded: int,
    raw_file_path: str | None,
    error_message: str | None = None,
):
    """Update the pipeline_audit row on completion."""
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE raw.pipeline_audit
            SET completed_at  = %s,
                status        = %s,
                rows_extracted = %s,
                rows_loaded   = %s,
                raw_file_path = %s,
                error_message = %s
            WHERE id = %s
            """,
            (
                datetime.now(timezone.utc),
                status,
                rows_extracted,
                rows_loaded,
                raw_file_path,
                error_message,
                audit_id,
            ),
        )
    conn.commit()
    logger.info("Audit id=%d updated: status=%s rows_loaded=%d",
                audit_id, status, rows_loaded)


def run_load(extraction_results: dict, datasets_config: dict):
    """Load all extracted datasets into PostgreSQL with audit logging."""
    conn = get_connection()

    raw_tables = [
        ds["raw_table"]
        for ds in datasets_config["datasets"].values()
        if ds.get("enabled", False) and ds.get("raw_table")
    ]
    ensure_schemas(conn, raw_tables=raw_tables)

    try:
        for key, result in extraction_results.items():
            ds_config = datasets_config["datasets"][key]
            raw_table = ds_config["raw_table"]

            audit_id = start_audit(conn, key)

            if result["status"] != "success":
                complete_audit(
                    conn, audit_id,
                    status="failed",
                    rows_extracted=0,
                    rows_loaded=0,
                    raw_file_path=result.get("raw_file_path"),
                    error_message=result.get("error", "extraction failed"),
                )
                continue

            try:
                rows_loaded = load_records_to_raw(
                    conn, result["records"], key, raw_table
                )
                complete_audit(
                    conn, audit_id,
                    status="success",
                    rows_extracted=result["rows_extracted"],
                    rows_loaded=rows_loaded,
                    raw_file_path=result["raw_file_path"],
                )
            except Exception as exc:
                conn.rollback()
                logger.error("Failed to load %s: %s", key, exc)
                complete_audit(
                    conn, audit_id,
                    status="failed",
                    rows_extracted=result["rows_extracted"],
                    rows_loaded=0,
                    raw_file_path=result["raw_file_path"],
                    error_message=str(exc),
                )
    finally:
        conn.close()
        logger.info("Database connection closed")
