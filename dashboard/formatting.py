"""Small helper functions for labels and text formatting."""

import pandas as pd


def flag_label(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "Unknown"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    s = str(value).strip().lower()
    if s in ("true", "t", "1", "yes"):
        return "Yes"
    if s in ("false", "f", "0", "no"):
        return "No"
    return "Unknown"


def coverage_label(level: str) -> str:
    labels = {
        "seattle_city_open_data_available": "Seattle City Open Data",
        "shoreline_partial_manual_review": "Shoreline (partial / manual review)",
        "king_county_context_possible": "King County (limited context)",
        "unknown_or_not_configured": "Unknown",
    }
    return labels.get(level, level)


def status_label(status: str) -> str:
    labels = {
        "eligible": "Eligible",
        "rejected": "Rejected",
        "benchmark": "Benchmark",
    }
    return labels.get(status, status)


def jurisdiction_label(j: str) -> str:
    labels = {
        "seattle": "Seattle",
        "shoreline": "Shoreline",
        "other_king_county": "Other King County",
        "unknown": "Unknown",
    }
    return labels.get(j, j)


def rent_display(row) -> str:
    rent = f"${row['listed_rent']:,.0f}"
    r_min = row.get("listed_rent_min")
    r_max = row.get("listed_rent_max")
    if pd.notna(r_min) and pd.notna(r_max):
        rent += f" (range: ${r_min:,.0f} - ${r_max:,.0f})"
    return rent
