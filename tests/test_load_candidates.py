"""Tests for candidate apartment CSV loading and validation."""

import csv
import os
import tempfile
from pathlib import Path

from src.ingestion.validate_candidates import (
    REQUIRED_COLUMNS,
    VALID_CONSIDERATION_STATUSES,
    VALID_RENT_BASES,
    resolve_candidate_file,
    validate_candidates,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_CSV = PROJECT_ROOT / "data" / "seed" / "candidate_apartments.example.csv"

# Helper to write a quick CSV with only the required columns plus extras
_BASE_HEADER = ",".join(sorted(REQUIRED_COLUMNS))


def _write_csv(rows_text: str, extra_header: str = "") -> Path:
    """Write a temp CSV and return its path."""
    header = "apartment_id,apartment_name,address,city,state,zip_code,neighborhood,listed_rent"
    if extra_header:
        header += "," + extra_header
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    )
    f.write(header + "\n")
    f.write(rows_text)
    f.close()
    return Path(f.name)


# --- File resolution ---

def test_resolve_defaults_to_known_file():
    old = os.environ.pop("CANDIDATE_APARTMENTS_FILE", None)
    try:
        path = resolve_candidate_file()
        assert path.name in (
            "candidate_apartments.example.csv",
            "candidate_apartments.local.csv",
        )
    finally:
        if old:
            os.environ["CANDIDATE_APARTMENTS_FILE"] = old


def test_resolve_uses_env_var():
    os.environ["CANDIDATE_APARTMENTS_FILE"] = "/tmp/custom.csv"
    try:
        path = resolve_candidate_file()
        assert path == Path("/tmp/custom.csv")
    finally:
        del os.environ["CANDIDATE_APARTMENTS_FILE"]


# --- Example CSV structure ---

def test_example_csv_exists():
    assert EXAMPLE_CSV.exists()


def test_example_csv_has_required_columns():
    with open(EXAMPLE_CSV, "r", encoding="utf-8") as f:
        columns = set(csv.DictReader(f).fieldnames or [])
    assert not (REQUIRED_COLUMNS - columns)


def test_example_csv_has_rows():
    with open(EXAMPLE_CSV, "r", encoding="utf-8") as f:
        assert len(list(csv.DictReader(f))) >= 3


def test_example_csv_apartment_ids_unique():
    with open(EXAMPLE_CSV, "r", encoding="utf-8") as f:
        ids = [r["apartment_id"] for r in csv.DictReader(f)]
    assert len(ids) == len(set(ids))


def test_example_csv_has_new_schema_columns():
    with open(EXAMPLE_CSV, "r", encoding="utf-8") as f:
        columns = set(csv.DictReader(f).fieldnames or [])
    expected = {
        "listed_rent_min", "listed_rent_max", "rent_basis", "rent_notes",
        "consideration_status", "exclusion_reason", "include_in_final_comparison",
        "data_privacy_level", "notes_public_safe",
    }
    assert not (expected - columns), f"Missing: {expected - columns}"


def test_validation_passes_on_example():
    assert validate_candidates(EXAMPLE_CSV) == []


# --- Validation: basic errors ---

def test_validation_catches_missing_file():
    errs = validate_candidates(Path("/nonexistent/file.csv"))
    assert any("not found" in e.lower() for e in errs)


def test_validation_catches_missing_columns():
    p = _write_csv("")
    # overwrite with minimal header missing required cols
    with open(p, "w", encoding="utf-8") as f:
        f.write("apartment_id,apartment_name\nAPT001,Test\n")
    try:
        assert any("Missing required" in e for e in validate_candidates(p))
    finally:
        p.unlink()


def test_validation_catches_empty_name():
    p = _write_csv("APT001,,123 Main,Seattle,WA,98101,DT,1500\n")
    try:
        assert any("apartment_name" in e for e in validate_candidates(p))
    finally:
        p.unlink()


def test_validation_catches_bad_rent():
    p = _write_csv("APT001,Test,123 Main,Seattle,WA,98101,DT,abc\n")
    try:
        assert any(
            "listed_rent" in e and "not numeric" in e
            for e in validate_candidates(p)
        )
    finally:
        p.unlink()


# --- Rent range validation ---

def test_validation_catches_min_gt_max():
    p = _write_csv(
        "APT001,Test,123 Main,Seattle,WA,98101,DT,1500,2000,1000,,\n",
        extra_header="listed_rent_min,listed_rent_max,rent_basis,rent_notes",
    )
    try:
        assert any(
            "listed_rent_min" in e and ">" in e
            for e in validate_candidates(p)
        )
    finally:
        p.unlink()


def test_validation_accepts_valid_range():
    p = _write_csv(
        "APT001,Test,123 Main,Seattle,WA,98101,DT,1500,1400,1600,floorplan_range,\n",
        extra_header="listed_rent_min,listed_rent_max,rent_basis,rent_notes",
    )
    try:
        assert validate_candidates(p) == []
    finally:
        p.unlink()


def test_validation_catches_bad_rent_basis():
    p = _write_csv(
        "APT001,Test,123 Main,Seattle,WA,98101,DT,1500,,,invalid_basis,\n",
        extra_header="listed_rent_min,listed_rent_max,rent_basis,rent_notes",
    )
    try:
        assert any("rent_basis" in e for e in validate_candidates(p))
    finally:
        p.unlink()


def test_validation_accepts_all_rent_bases():
    for basis in VALID_RENT_BASES:
        p = _write_csv(
            f"APT001,Test,123 Main,Seattle,WA,98101,DT,1500,,,{basis},\n",
            extra_header="listed_rent_min,listed_rent_max,rent_basis,rent_notes",
        )
        try:
            assert not any("rent_basis" in e for e in validate_candidates(p))
        finally:
            p.unlink()


# --- Consideration status validation ---

def test_validation_catches_bad_consideration_status():
    p = _write_csv(
        "APT001,Test,123 Main,Seattle,WA,98101,DT,1500,bad_status,none,true\n",
        extra_header="consideration_status,exclusion_reason,include_in_final_comparison",
    )
    try:
        assert any("consideration_status" in e for e in validate_candidates(p))
    finally:
        p.unlink()


def test_validation_accepts_all_consideration_statuses():
    for status in VALID_CONSIDERATION_STATUSES:
        p = _write_csv(
            f"APT001,Test,123 Main,Seattle,WA,98101,DT,1500,{status},none,true\n",
            extra_header="consideration_status,exclusion_reason,include_in_final_comparison",
        )
        try:
            assert not any("consideration_status" in e for e in validate_candidates(p))
        finally:
            p.unlink()


def test_validation_catches_bad_exclusion_reason():
    p = _write_csv(
        "APT001,Test,123 Main,Seattle,WA,98101,DT,1500,rejected,bad_reason,false\n",
        extra_header="consideration_status,exclusion_reason,include_in_final_comparison",
    )
    try:
        assert any("exclusion_reason" in e for e in validate_candidates(p))
    finally:
        p.unlink()


def test_validation_catches_bad_include_flag():
    p = _write_csv(
        "APT001,Test,123 Main,Seattle,WA,98101,DT,1500,eligible,none,maybe\n",
        extra_header="consideration_status,exclusion_reason,include_in_final_comparison",
    )
    try:
        assert any("include_in_final_comparison" in e for e in validate_candidates(p))
    finally:
        p.unlink()


# --- Coordinates ---

def test_validation_catches_bad_coordinates():
    p = _write_csv(
        "APT001,Test,123 Main,Seattle,WA,98101,DT,1500,0.0,0.0\n",
        extra_header="latitude,longitude",
    )
    try:
        assert any("latitude" in e and "outside" in e for e in validate_candidates(p))
    finally:
        p.unlink()


# --- Local CSV is headers-only ---

def test_local_csv_validates_if_present():
    local = PROJECT_ROOT / "data" / "seed" / "candidate_apartments.local.csv"
    if not local.exists():
        return
    with open(local, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) == 0:
        return
    errors = validate_candidates(local)
    assert errors == [], f"Local CSV has validation errors: {errors}"
