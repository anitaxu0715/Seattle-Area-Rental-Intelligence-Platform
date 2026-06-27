"""Load candidate apartments from CSV into PostgreSQL."""

import csv
from datetime import datetime, timezone
from pathlib import Path

from src.ingestion.validate_candidates import resolve_candidate_file, validate_candidates
from src.utils.database import get_connection
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

CREATE_TABLE_SQL = """
DROP TABLE IF EXISTS raw.raw_candidate_apartments CASCADE;
CREATE TABLE raw.raw_candidate_apartments (
    apartment_id                TEXT PRIMARY KEY,
    apartment_name              TEXT NOT NULL,
    address                     TEXT NOT NULL,
    city                        TEXT,
    state                       TEXT,
    zip_code                    TEXT,
    neighborhood                TEXT,
    listed_rent                 NUMERIC,
    listed_rent_min             NUMERIC,
    listed_rent_max             NUMERIC,
    rent_basis                  TEXT,
    rent_notes                  TEXT,
    unit_type                   TEXT,
    square_feet                 INTEGER,
    year_built                  INTEGER,
    parking_available           TEXT,
    parking_fee                 NUMERIC,
    pet_policy                  TEXT,
    online_availability_status  TEXT,
    actual_availability_status  TEXT,
    tour_date                   DATE,
    management_notes            TEXT,
    personal_notes              TEXT,
    latitude                    DOUBLE PRECISION,
    longitude                   DOUBLE PRECISION,
    location_source             TEXT,
    location_confidence         TEXT,
    data_privacy_level          TEXT,
    notes_public_safe           TEXT,
    consideration_status        TEXT,
    exclusion_reason            TEXT,
    include_in_final_comparison BOOLEAN,
    loaded_at                   TIMESTAMP NOT NULL DEFAULT NOW()
);
"""

INSERT_SQL = """
INSERT INTO raw.raw_candidate_apartments (
    apartment_id, apartment_name, address, city, state, zip_code,
    neighborhood, listed_rent, listed_rent_min, listed_rent_max,
    rent_basis, rent_notes, unit_type, square_feet, year_built,
    parking_available, parking_fee, pet_policy,
    online_availability_status, actual_availability_status, tour_date,
    management_notes, personal_notes,
    latitude, longitude, location_source, location_confidence,
    data_privacy_level, notes_public_safe,
    consideration_status, exclusion_reason, include_in_final_comparison,
    loaded_at
) VALUES (
    %(apartment_id)s, %(apartment_name)s, %(address)s, %(city)s, %(state)s,
    %(zip_code)s, %(neighborhood)s, %(listed_rent)s, %(listed_rent_min)s,
    %(listed_rent_max)s, %(rent_basis)s, %(rent_notes)s, %(unit_type)s,
    %(square_feet)s, %(year_built)s, %(parking_available)s, %(parking_fee)s,
    %(pet_policy)s, %(online_availability_status)s,
    %(actual_availability_status)s, %(tour_date)s,
    %(management_notes)s, %(personal_notes)s,
    %(latitude)s, %(longitude)s, %(location_source)s,
    %(location_confidence)s, %(data_privacy_level)s,
    %(notes_public_safe)s, %(consideration_status)s,
    %(exclusion_reason)s, %(include_in_final_comparison)s,
    %(loaded_at)s
);
"""


def _parse_int(val: str) -> int | None:
    if not val:
        return None
    return int(val)


def _parse_float(val: str) -> float | None:
    if not val:
        return None
    return float(val)


def _parse_text(val: str) -> str | None:
    if not val or not val.strip():
        return None
    return val.strip()


def _parse_bool(val: str) -> bool | None:
    v = (val or "").strip().lower()
    if not v:
        return None
    return v == "true"


def load_candidates(file_path: Path | None = None) -> int:
    """Validate and load candidate apartments into raw.raw_candidate_apartments."""
    if file_path is None:
        file_path = resolve_candidate_file()

    logger.info("Using candidate file: %s", file_path)

    if "example" in file_path.name:
        logger.warning(
            "Loading public demo data (%s). "
            "For real analysis, create candidate_apartments.local.csv "
            "or set CANDIDATE_APARTMENTS_FILE.",
            file_path.name,
        )

    errors = validate_candidates(file_path)
    if errors:
        logger.error("Validation failed — aborting load")
        raise ValueError(f"Candidate validation failed with {len(errors)} errors")

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")
            cur.execute(CREATE_TABLE_SQL)
        conn.commit()
        logger.info("Prepared raw.raw_candidate_apartments table")

        now = datetime.now(timezone.utc)
        loaded = 0
        with conn.cursor() as cur:
            for row in rows:
                params = {
                    "apartment_id": row["apartment_id"],
                    "apartment_name": row["apartment_name"],
                    "address": row["address"],
                    "city": row["city"],
                    "state": row["state"],
                    "zip_code": row.get("zip_code") or None,
                    "neighborhood": row.get("neighborhood") or None,
                    "listed_rent": _parse_float(row.get("listed_rent", "")),
                    "listed_rent_min": _parse_float(
                        row.get("listed_rent_min", "")),
                    "listed_rent_max": _parse_float(
                        row.get("listed_rent_max", "")),
                    "rent_basis": _parse_text(row.get("rent_basis", "")),
                    "rent_notes": _parse_text(row.get("rent_notes", "")),
                    "unit_type": _parse_text(row.get("unit_type", "")),
                    "square_feet": _parse_int(row.get("square_feet", "")),
                    "year_built": _parse_int(row.get("year_built", "")),
                    "parking_available": _parse_text(
                        row.get("parking_available", "")),
                    "parking_fee": _parse_float(row.get("parking_fee", "")),
                    "pet_policy": _parse_text(row.get("pet_policy", "")),
                    "online_availability_status": _parse_text(
                        row.get("online_availability_status", "")),
                    "actual_availability_status": _parse_text(
                        row.get("actual_availability_status", "")),
                    "tour_date": _parse_text(row.get("tour_date", "")),
                    "management_notes": _parse_text(
                        row.get("management_notes", "")),
                    "personal_notes": _parse_text(
                        row.get("personal_notes", "")),
                    "latitude": _parse_float(row.get("latitude", "")),
                    "longitude": _parse_float(row.get("longitude", "")),
                    "location_source": _parse_text(
                        row.get("location_source", "")),
                    "location_confidence": _parse_text(
                        row.get("location_confidence", "")),
                    "data_privacy_level": _parse_text(
                        row.get("data_privacy_level", "")),
                    "notes_public_safe": _parse_text(
                        row.get("notes_public_safe", "")),
                    "consideration_status": _parse_text(
                        row.get("consideration_status", "")),
                    "exclusion_reason": _parse_text(
                        row.get("exclusion_reason", "")),
                    "include_in_final_comparison": _parse_bool(
                        row.get("include_in_final_comparison", "")),
                    "loaded_at": now,
                }
                cur.execute(INSERT_SQL, params)
                loaded += 1

        conn.commit()
        logger.info("Loaded %d candidate apartments from %s", loaded, file_path.name)
        return loaded

    finally:
        conn.close()


if __name__ == "__main__":
    count = load_candidates()
    logger.info("Done: %d rows loaded", count)
