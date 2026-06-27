"""Tests for dataset configuration loading."""

from pathlib import Path

import yaml

DATASETS_PATH = Path(__file__).resolve().parent.parent / "src" / "ingestion" / "datasets.yml"

EXPECTED_ENABLED = {
    "building_permits",
    "rental_property_registration",
    "code_complaints_violations",
}


def _load():
    with open(DATASETS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_datasets_yml_loads():
    config = _load()
    assert "datasets" in config
    assert len(config["datasets"]) > 0


def test_all_datasets_have_required_fields():
    config = _load()
    required_fields = {"name", "domain", "dataset_id", "raw_table", "enabled"}

    for key, ds in config["datasets"].items():
        missing = required_fields - set(ds.keys())
        assert not missing, f"Dataset '{key}' missing fields: {missing}"


def test_expected_datasets_are_enabled():
    config = _load()
    enabled = {k for k, ds in config["datasets"].items() if ds.get("enabled")}
    assert EXPECTED_ENABLED == enabled


def test_building_permits_config():
    bp = _load()["datasets"]["building_permits"]
    assert bp["dataset_id"] == "76t5-zqzr"
    assert bp["domain"] == "data.seattle.gov"
    assert bp["raw_table"] == "raw_building_permits"
    assert bp["natural_key"] == "permitnum"
    assert bp["enabled"] is True
    assert bp["default_limit"] > 0


def test_rental_registration_config():
    rr = _load()["datasets"]["rental_property_registration"]
    assert rr["dataset_id"] == "j2xh-c7vt"
    assert rr["domain"] == "data.seattle.gov"
    assert rr["raw_table"] == "raw_rental_registration"
    assert rr["natural_key"] == "permitnum"
    assert rr["enabled"] is True


def test_code_violations_config():
    cv = _load()["datasets"]["code_complaints_violations"]
    assert cv["dataset_id"] == "ez4a-iug7"
    assert cv["domain"] == "data.seattle.gov"
    assert cv["raw_table"] == "raw_code_violations"
    assert cv["natural_key"] == "recordnum"
    assert cv["enabled"] is True


def test_raw_table_names_are_valid():
    """Table names must be lowercase alphanumeric with underscores."""
    import re
    pattern = re.compile(r"^[a-z][a-z0-9_]*$")
    config = _load()
    for key, ds in config["datasets"].items():
        table = ds["raw_table"]
        assert pattern.match(table), f"Invalid raw_table for '{key}': {table}"


def test_disabled_datasets_still_have_raw_table():
    config = _load()
    for key, ds in config["datasets"].items():
        assert ds.get("raw_table"), f"Dataset '{key}' missing raw_table"
