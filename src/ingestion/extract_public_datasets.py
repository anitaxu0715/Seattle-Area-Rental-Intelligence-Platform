"""Extract datasets from Seattle Open Data using the Socrata client."""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from src.ingestion.socrata_client import SocrataClient
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATASETS_PATH = Path(__file__).resolve().parent / "datasets.yml"
RAW_DIR = PROJECT_ROOT / "data" / "raw"


def load_dataset_config() -> dict:
    """Load dataset configuration from datasets.yml."""
    with open(DATASETS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_where_clause(config: dict) -> str | None:
    """Build a SoQL WHERE clause from dataset config."""
    date_field = config.get("date_filter_field")
    lookback_days = config.get("lookback_days")

    if date_field and lookback_days:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).strftime(
            "%Y-%m-%dT00:00:00"
        )
        return f"{date_field} >= '{cutoff}'"
    return None


def extract_dataset(dataset_key: str, config: dict) -> tuple[list[dict], str]:
    """Extract one dataset and save the raw JSON file.

    Returns (records, raw_file_path).
    """
    app_token = os.getenv("SOCRATA_APP_TOKEN") or None
    client = SocrataClient(domain=config["domain"], app_token=app_token)

    where = build_where_clause(config)
    order = config.get("order")
    max_records = config.get("default_limit", 1000)
    page_size = config.get("page_size", 1000)

    logger.info("Extracting %s (dataset_id=%s, max_records=%d)",
                dataset_key, config["dataset_id"], max_records)

    records = client.get_all_records(
        dataset_id=config["dataset_id"],
        max_records=max_records,
        page_size=page_size,
        where=where,
        order=order,
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{dataset_key}_{timestamp}.json"
    raw_file_path = RAW_DIR / filename

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with open(raw_file_path, "w") as f:
        json.dump(records, f, indent=2)

    logger.info("Saved %d records to %s", len(records), raw_file_path)
    return records, str(raw_file_path)


def run_extraction() -> dict:
    """Run extraction for all enabled datasets. Returns results per dataset."""
    config = load_dataset_config()
    results = {}

    for key, ds in config["datasets"].items():
        if not ds.get("enabled", False):
            logger.info("Skipping disabled dataset: %s", key)
            continue

        # Only Socrata datasets for now
        if ds.get("format") == "geojson":
            logger.info("Skipping non-Socrata dataset: %s", key)
            continue

        try:
            records, raw_path = extract_dataset(key, ds)
            results[key] = {
                "status": "success",
                "rows_extracted": len(records),
                "raw_file_path": raw_path,
                "records": records,
            }
        except Exception as exc:
            logger.error("Failed to extract %s: %s", key, exc)
            results[key] = {
                "status": "failed",
                "rows_extracted": 0,
                "raw_file_path": None,
                "records": [],
                "error": str(exc),
            }

    return results


if __name__ == "__main__":
    run_extraction()
