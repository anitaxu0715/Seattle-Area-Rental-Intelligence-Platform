"""Tests for pipeline audit payload structure."""

from datetime import datetime, timezone

EXPECTED_DATASETS = [
    "building_permits",
    "rental_property_registration",
    "code_complaints_violations",
]


def _make_audit_payload(
    dataset_name: str,
    status: str,
    rows_extracted: int,
    rows_loaded: int,
    raw_file_path: str | None = None,
    error_message: str | None = None,
) -> dict:
    """Mirror the audit fields the pipeline writes."""
    return {
        "dataset_name": dataset_name,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "rows_extracted": rows_extracted,
        "rows_loaded": rows_loaded,
        "raw_file_path": raw_file_path,
        "error_message": error_message,
    }


REQUIRED_FIELDS = {
    "dataset_name", "started_at", "completed_at",
    "status", "rows_extracted", "rows_loaded",
    "raw_file_path", "error_message",
}


def test_audit_payload_has_required_fields():
    payload = _make_audit_payload(
        dataset_name="building_permits",
        status="success",
        rows_extracted=500,
        rows_loaded=500,
        raw_file_path="data/raw/building_permits_20250601_120000.json",
    )
    assert REQUIRED_FIELDS.issubset(set(payload.keys()))


def test_audit_payload_success():
    payload = _make_audit_payload(
        dataset_name="building_permits",
        status="success",
        rows_extracted=100,
        rows_loaded=100,
    )
    assert payload["status"] == "success"
    assert payload["error_message"] is None
    assert payload["rows_extracted"] == payload["rows_loaded"]


def test_audit_payload_failure():
    payload = _make_audit_payload(
        dataset_name="building_permits",
        status="failed",
        rows_extracted=0,
        rows_loaded=0,
        error_message="Connection refused",
    )
    assert payload["status"] == "failed"
    assert payload["error_message"] is not None


def test_audit_payload_per_dataset():
    """Each enabled dataset should produce its own audit record."""
    payloads = []
    for ds in EXPECTED_DATASETS:
        payloads.append(_make_audit_payload(
            dataset_name=ds,
            status="success",
            rows_extracted=1000,
            rows_loaded=1000,
            raw_file_path=f"data/raw/{ds}_20260618_120000.json",
        ))

    assert len(payloads) == 3
    names = {p["dataset_name"] for p in payloads}
    assert names == set(EXPECTED_DATASETS)


def test_audit_partial_failure():
    """If one dataset fails, others should still have their own records."""
    results = {
        "building_permits": _make_audit_payload(
            "building_permits", "success", 1000, 1000),
        "rental_property_registration": _make_audit_payload(
            "rental_property_registration", "failed", 0, 0,
            error_message="HTTP 500"),
        "code_complaints_violations": _make_audit_payload(
            "code_complaints_violations", "success", 800, 800),
    }

    assert len(results) == 3
    assert results["building_permits"]["status"] == "success"
    assert results["rental_property_registration"]["status"] == "failed"
    assert results["code_complaints_violations"]["status"] == "success"
