"""Show which candidate apartments are missing coordinates."""

import csv

from src.ingestion.validate_candidates import resolve_candidate_file
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def show_coordinate_status():
    path = resolve_candidate_file()
    logger.info("Checking coordinates in: %s", path)

    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        logger.warning("No data rows found")
        return

    missing = 0
    print()
    print(f"{'ID':<10} {'Name':<30} {'City':<12} {'Lat':>10} {'Lng':>12} "
          f"{'Source':<15} {'Confidence':<10}")
    print("-" * 105)

    for row in rows:
        aid = row.get("apartment_id", "?")
        name = (row.get("apartment_name") or "")[:28]
        city = (row.get("city") or "")[:10]
        lat = (row.get("latitude") or "").strip()
        lng = (row.get("longitude") or "").strip()
        src = (row.get("location_source") or "").strip() or "-"
        conf = (row.get("location_confidence") or "").strip() or "-"

        lat_display = lat if lat else "MISSING"
        lng_display = lng if lng else "MISSING"

        if not lat or not lng:
            missing += 1

        print(f"{aid:<10} {name:<30} {city:<12} {lat_display:>10} {lng_display:>12} "
              f"{src:<15} {conf:<10}")

    print()
    complete = len(rows) - missing
    print(f"Summary: {complete}/{len(rows)} candidates have coordinates. "
          f"{missing} missing.")

    if missing > 0:
        print()
        print("Candidates with missing coordinates will show 0 for "
              "complaints_nearby_count and permits_nearby_count.")
        print("Add latitude/longitude from a public source, then run:")
        print("  make validate-candidates")
        print("  make load-candidates")
        print("  make dbt-run")
    print()


if __name__ == "__main__":
    show_coordinate_status()
