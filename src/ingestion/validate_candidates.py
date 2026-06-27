"""Validate candidate apartment CSV data before loading."""

import csv
import os
import sys
from pathlib import Path

from src.utils.logging_config import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

REQUIRED_COLUMNS = {
    "apartment_id", "apartment_name", "address", "city", "state",
    "zip_code", "neighborhood", "listed_rent",
}

REQUIRED_NOT_NULL = {"apartment_id", "apartment_name", "address", "city", "state"}

VALID_DATA_PRIVACY_LEVELS = {"public_demo", "portfolio_safe", "private_local"}
VALID_LOCATION_SOURCES = {"manual", "public_record", "unknown"}
VALID_LOCATION_CONFIDENCES = {"high", "medium", "low", "unknown"}
VALID_RENT_BASES = {
    "specific_unit", "floorplan_range", "leasing_quote",
    "estimated_from_listing", "unknown",
}
VALID_CONSIDERATION_STATUSES = {"eligible", "rejected", "benchmark"}
VALID_EXCLUSION_REASONS = {
    "none", "outside_budget", "wrong_unit_type",
    "availability_mismatch", "parking_issue", "location_issue", "other",
}

MAX_LISTED_RENT = 2500

LAT_MIN, LAT_MAX = 47.3, 47.9
LNG_MIN, LNG_MAX = -122.6, -122.0

PLACEHOLDER_PATTERNS = [
    "123 fake", "example apartment", "test apartment",
    "placeholder", "xxx", "tbd address",
]


def resolve_candidate_file() -> Path:
    """Determine which candidate CSV to load."""
    env_path = os.getenv("CANDIDATE_APARTMENTS_FILE")
    if env_path:
        return Path(env_path)

    local_path = PROJECT_ROOT / "data" / "seed" / "candidate_apartments.local.csv"
    if local_path.exists():
        return local_path

    return PROJECT_ROOT / "data" / "seed" / "candidate_apartments.example.csv"


def _check_accepted(row_label, field_name, value, accepted, errors):
    if value and value not in accepted:
        errors.append(
            f"{row_label}: {field_name} '{value}' not in {accepted}"
        )


def _parse_optional_float(val: str) -> float | None:
    v = (val or "").strip()
    if not v:
        return None
    return float(v)


def validate_candidates(file_path: Path | None = None) -> list[str]:
    """Validate a candidate apartments CSV. Returns list of error messages."""
    if file_path is None:
        file_path = resolve_candidate_file()

    errors: list[str] = []
    warnings: list[str] = []

    if not file_path.exists():
        errors.append(f"File not found: {file_path}")
        return errors

    is_example = "example" in file_path.name

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = set(reader.fieldnames or [])
        rows = list(reader)

    missing_cols = REQUIRED_COLUMNS - columns
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
        return errors

    if not rows:
        errors.append("CSV has no data rows")
        return errors

    seen_ids = set()
    for i, row in enumerate(rows, start=2):
        row_label = f"Row {i} ({row.get('apartment_id', '?')})"

        # --- Required not-null ---
        for field in REQUIRED_NOT_NULL:
            if not (row.get(field) or "").strip():
                errors.append(f"{row_label}: {field} is empty")

        # --- Unique apartment_id ---
        aid = row.get("apartment_id", "").strip()
        if aid in seen_ids:
            errors.append(f"{row_label}: duplicate apartment_id '{aid}'")
        seen_ids.add(aid)

        # --- listed_rent ---
        rent_str = (row.get("listed_rent") or "").strip()
        rent = None
        if rent_str:
            try:
                rent = float(rent_str)
                if rent <= 0:
                    errors.append(f"{row_label}: listed_rent must be positive")
                elif rent > MAX_LISTED_RENT:
                    warnings.append(
                        f"{row_label}: listed_rent {rent} exceeds "
                        f"hard filter max ({MAX_LISTED_RENT})"
                    )
            except ValueError:
                errors.append(
                    f"{row_label}: listed_rent is not numeric: '{rent_str}'"
                )

        # --- Rent range ---
        rent_min = rent_max = None
        try:
            rent_min = _parse_optional_float(row.get("listed_rent_min", ""))
        except ValueError:
            errors.append(f"{row_label}: listed_rent_min is not numeric")
        try:
            rent_max = _parse_optional_float(row.get("listed_rent_max", ""))
        except ValueError:
            errors.append(f"{row_label}: listed_rent_max is not numeric")

        if rent_min is not None and rent_max is not None and rent_min > rent_max:
            errors.append(
                f"{row_label}: listed_rent_min ({rent_min}) > "
                f"listed_rent_max ({rent_max})"
            )

        if (rent is not None and rent_min is not None and rent_max is not None
                and (rent < rent_min or rent > rent_max)):
            warnings.append(
                f"{row_label}: listed_rent ({rent}) outside range "
                f"[{rent_min}, {rent_max}]"
            )

        # --- unit_type ---
        unit = (row.get("unit_type") or "").strip()
        if unit and unit != "1B1B":
            warnings.append(
                f"{row_label}: unit_type '{unit}' is not 1B1B "
                f"(outside primary search scope)"
            )

        # --- Accepted-value fields ---
        _check_accepted(row_label, "rent_basis",
                        (row.get("rent_basis") or "").strip(),
                        VALID_RENT_BASES, errors)
        _check_accepted(row_label, "data_privacy_level",
                        (row.get("data_privacy_level") or "").strip(),
                        VALID_DATA_PRIVACY_LEVELS, errors)
        _check_accepted(row_label, "location_source",
                        (row.get("location_source") or "").strip(),
                        VALID_LOCATION_SOURCES, errors)
        _check_accepted(row_label, "location_confidence",
                        (row.get("location_confidence") or "").strip(),
                        VALID_LOCATION_CONFIDENCES, errors)
        _check_accepted(row_label, "consideration_status",
                        (row.get("consideration_status") or "").strip(),
                        VALID_CONSIDERATION_STATUSES, errors)
        _check_accepted(row_label, "exclusion_reason",
                        (row.get("exclusion_reason") or "").strip(),
                        VALID_EXCLUSION_REASONS, errors)

        # --- include_in_final_comparison ---
        incl_raw = (row.get("include_in_final_comparison") or "").strip().lower()
        if incl_raw and incl_raw not in ("true", "false"):
            errors.append(
                f"{row_label}: include_in_final_comparison must be "
                f"true or false, got '{incl_raw}'"
            )

        # --- Cross-field consistency warnings ---
        status = (row.get("consideration_status") or "").strip()
        incl = incl_raw == "true"

        if status in ("rejected", "benchmark") and incl:
            warnings.append(
                f"{row_label}: include_in_final_comparison is true but "
                f"consideration_status is '{status}'"
            )

        is_budget_ok = rent is not None and rent <= MAX_LISTED_RENT
        is_unit_ok = unit == "1B1B"
        meets_filters = is_budget_ok and is_unit_ok

        if status == "eligible" and not meets_filters and rent is not None:
            reasons = []
            if not is_budget_ok:
                reasons.append(f"rent {rent} > {MAX_LISTED_RENT}")
            if not is_unit_ok:
                reasons.append(f"unit_type '{unit}' is not 1B1B")
            warnings.append(
                f"{row_label}: consideration_status is 'eligible' but "
                f"does not meet hard filters ({', '.join(reasons)})"
            )

        # --- Coordinates ---
        lat_str = (row.get("latitude") or "").strip()
        lng_str = (row.get("longitude") or "").strip()
        apt_name = (row.get("apartment_name") or "").strip()
        if lat_str and lng_str:
            try:
                lat, lng = float(lat_str), float(lng_str)
                if not (LAT_MIN <= lat <= LAT_MAX):
                    errors.append(
                        f"{row_label}: latitude {lat} outside Seattle area "
                        f"[{LAT_MIN}, {LAT_MAX}]"
                    )
                if not (LNG_MIN <= lng <= LNG_MAX):
                    errors.append(
                        f"{row_label}: longitude {lng} outside Seattle area "
                        f"[{LNG_MIN}, {LNG_MAX}]"
                    )
            except ValueError:
                errors.append(f"{row_label}: latitude/longitude not numeric")
        elif not is_example:
            warnings.append(
                f"{row_label} [{apt_name}]: MISSING COORDINATES — "
                f"nearby complaints and permits will show as 0. "
                f"Add latitude/longitude from a public source to enable "
                f"proximity matching."
            )
        else:
            warnings.append(
                f"{row_label}: missing coordinates — proximity matching "
                f"will not work for this apartment"
            )

        # --- Placeholder detection (non-example files only) ---
        if not is_example:
            addr_lower = (row.get("address") or "").lower()
            name_lower = (row.get("apartment_name") or "").lower()
            for pattern in PLACEHOLDER_PATTERNS:
                if pattern in addr_lower or pattern in name_lower:
                    warnings.append(
                        f"{row_label}: possible placeholder data detected "
                        f"('{pattern}' found)"
                    )

    for w in warnings:
        logger.warning("WARN: %s", w)
    for e in errors:
        logger.error("ERROR: %s", e)

    if not errors:
        logger.info(
            "Validation passed: %d rows in %s (%d warnings)",
            len(rows), file_path.name, len(warnings),
        )
    else:
        logger.error("Validation failed with %d errors", len(errors))

    return errors


if __name__ == "__main__":
    path = resolve_candidate_file()
    logger.info("Validating: %s", path)
    errs = validate_candidates(path)
    if errs:
        sys.exit(1)
