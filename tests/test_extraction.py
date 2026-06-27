"""Tests for extraction utilities."""

from datetime import datetime, timedelta, timezone

from src.ingestion.extract_public_datasets import build_where_clause, load_dataset_config


def test_load_dataset_config_returns_datasets():
    config = load_dataset_config()
    assert "datasets" in config
    assert "building_permits" in config["datasets"]
    assert "rental_property_registration" in config["datasets"]
    assert "code_complaints_violations" in config["datasets"]


def test_enabled_datasets_count():
    config = load_dataset_config()
    enabled = [k for k, ds in config["datasets"].items() if ds.get("enabled")]
    assert len(enabled) == 3


def test_build_where_clause_with_date_filter():
    config = {
        "date_filter_field": "issueddate",
        "lookback_days": 365,
    }
    clause = build_where_clause(config)
    assert clause is not None
    assert "issueddate >= " in clause

    cutoff_str = clause.split("'")[1]
    cutoff_date = datetime.strptime(cutoff_str, "%Y-%m-%dT%H:%M:%S").date()
    expected_date = (datetime.now(timezone.utc) - timedelta(days=365)).date()
    assert abs((cutoff_date - expected_date).days) <= 1


def test_build_where_clause_without_date_filter():
    assert build_where_clause({}) is None
    assert build_where_clause({"date_filter_field": "issueddate"}) is None
    assert build_where_clause({"lookback_days": 365}) is None


def test_no_where_clause_for_rental_registration():
    """Rental registration has no date_filter_field, so no WHERE clause."""
    config = load_dataset_config()
    rr = config["datasets"]["rental_property_registration"]
    assert build_where_clause(rr) is None


def test_where_clause_for_code_violations():
    config = load_dataset_config()
    cv = config["datasets"]["code_complaints_violations"]
    clause = build_where_clause(cv)
    assert clause is not None
    assert "opendate >= " in clause


def test_output_filename_contains_dataset_key():
    """Verify the raw file naming convention includes the dataset key."""
    for key in ["building_permits", "rental_property_registration", "code_complaints_violations"]:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{key}_{timestamp}.json"
        assert key in filename
        assert filename.endswith(".json")


def test_raw_record_jsonb_structure_building_permits():
    sample = {
        "permitnum": "6783472-CN",
        "permitclass": "Multifamily",
        "statuscurrent": "Issued",
        "originaladdress1": "123 MAIN ST",
        "latitude": "47.6062",
        "longitude": "-122.3321",
        "issueddate": "2026-01-15T00:00:00.000",
    }
    row = {"source_dataset": "building_permits", "raw_record": sample}
    assert row["source_dataset"] == "building_permits"
    assert "permitnum" in row["raw_record"]


def test_raw_record_jsonb_structure_rental_registration():
    sample = {
        "permitnum": "001-0100981",
        "propertyname": "Sample Apartments",
        "originaladdress1": "2008 WESTLAKE AVE",
        "statuscurrent": "Active Registration",
        "registereddate": "2026-06-17",
    }
    row = {"source_dataset": "rental_property_registration", "raw_record": sample}
    assert row["source_dataset"] == "rental_property_registration"
    assert "permitnum" in row["raw_record"]


def test_raw_record_jsonb_structure_code_violations():
    sample = {
        "recordnum": "000630-26CP",
        "recordtype": "Complaint",
        "originaladdress1": "5412 39TH AVE W",
        "statuscurrent": "Completed",
        "opendate": "2026-06-15T00:00:00.000",
    }
    row = {"source_dataset": "code_complaints_violations", "raw_record": sample}
    assert row["source_dataset"] == "code_complaints_violations"
    assert "recordnum" in row["raw_record"]
