"""Seattle-Area Rental Intelligence Platform — Streamlit Dashboard."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from dashboard.db import (
    load_due_diligence_mart,
    load_complaint_evidence,
    load_permit_evidence,
)
from dashboard.formatting import (
    coverage_label,
    flag_label,
    jurisdiction_label,
    rent_display,
    status_label,
)

st.set_page_config(
    page_title="Seattle-Area Rental Intelligence",
    page_icon="🏠",
    layout="wide",
)

# ---------- sidebar navigation ----------

section = st.sidebar.radio(
    "Navigate",
    [
        "Executive Summary",
        "Apartment Comparison",
        "Apartment Detail",
        "Public Record Evidence",
        "Methodology & Limitations",
    ],
)

if st.sidebar.button("Refresh data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data from Seattle Open Data (Socrata API). "
    "Candidate apartments are manually curated."
)

# ---------- load data ----------

df = load_due_diligence_mart()
complaints = load_complaint_evidence()
permits = load_permit_evidence()


# ================================================================
# EXECUTIVE SUMMARY
# ================================================================
if section == "Executive Summary":
    st.title("Seattle-Area Rental Intelligence Platform")
    st.markdown(
        "Comparing apartment candidates across Seattle and Shoreline "
        "using public records from Seattle's Open Data portal. "
        "Coverage varies by jurisdiction."
    )

    st.markdown("---")

    total = len(df)
    eligible = int((df["include_in_final_comparison"] == True).sum())  # noqa: E712
    seattle_n = int((df["jurisdiction"] == "seattle").sum())
    shoreline_n = int((df["jurisdiction"] == "shoreline").sum())
    total_complaints = int(df["complaints_nearby_count"].sum())
    total_permits = int(df["permits_nearby_count"].sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Candidates", total)
    c2.metric("Eligible for Comparison", eligible)
    c3.metric("Benchmark / Excluded", total - eligible)

    c4, c5, c6 = st.columns(3)
    c4.metric("Seattle Candidates", seattle_n)
    c5.metric("Shoreline Candidates", shoreline_n)
    c6.metric("Other Jurisdictions", total - seattle_n - shoreline_n)

    c7, c8 = st.columns(2)
    c7.metric("Complaints within 500m (total)", total_complaints)
    c8.metric("Permits within 500m (total)", total_permits)

    st.info(
        "Public-record coverage differs by jurisdiction. "
        "Seattle city open datasets cover permits, code complaints, and rental registration. "
        "Shoreline candidates may show partial results from Seattle boundary data only. "
        "Shoreline-specific public records require separate integration or manual review."
    )


# ================================================================
# APARTMENT COMPARISON
# ================================================================
elif section == "Apartment Comparison":
    st.title("Apartment Comparison")

    # --- filters ---
    with st.expander("Filters", expanded=False):
        fc1, fc2 = st.columns(2)
        jur_opts = sorted(df["jurisdiction"].unique())
        sel_jur = fc1.multiselect("Jurisdiction", jur_opts, default=jur_opts)
        stat_opts = sorted(df["consideration_status"].unique())
        sel_stat = fc2.multiselect("Status", stat_opts, default=stat_opts)

    filtered = df[
        df["jurisdiction"].isin(sel_jur) & df["consideration_status"].isin(sel_stat)
    ]

    cols = [
        "apartment_name", "city", "jurisdiction", "listed_rent",
        "consideration_status", "include_in_final_comparison",
        "public_data_coverage_level",
        "complaints_nearby_count", "permits_nearby_count",
        "total_public_record_flags", "total_coverage_limitation_flags",
        "total_renter_fit_flags", "total_due_diligence_flags",
        "flag_outside_budget",
    ]

    display = filtered[cols].copy()
    display["jurisdiction"] = display["jurisdiction"].apply(jurisdiction_label)
    display["consideration_status"] = display["consideration_status"].apply(status_label)
    display["public_data_coverage_level"] = display["public_data_coverage_level"].apply(coverage_label)
    display["listed_rent"] = display["listed_rent"].apply(lambda v: f"${v:,.0f}")
    display["include_in_final_comparison"] = display["include_in_final_comparison"].apply(flag_label)
    display["flag_outside_budget"] = display["flag_outside_budget"].apply(flag_label)

    display.columns = [
        "Apartment", "City", "Jurisdiction", "Rent",
        "Status", "In Final Comparison",
        "Data Coverage",
        "Complaints (500m)", "Permits (500m)",
        "Public Record Flags", "Coverage Flags",
        "Renter Fit Flags", "Due Diligence Flags",
        "Over Budget",
    ]

    st.dataframe(display, use_container_width=True, hide_index=True)

    st.caption(
        "Public record flags: registration, complaints, permits (Seattle data only). "
        "Coverage flags: non-Seattle jurisdiction. "
        "Renter fit flags: availability, parking. "
        "Budget is tracked separately via hard filters."
    )


# ================================================================
# APARTMENT DETAIL
# ================================================================
elif section == "Apartment Detail":
    st.title("Apartment Detail")

    names = df["apartment_name"].tolist()
    selected = st.selectbox("Select apartment", names)
    row = df[df["apartment_name"] == selected].iloc[0]

    st.subheader(row["apartment_name"])

    d1, d2, d3 = st.columns(3)
    d1.markdown(f"**City:** {row['city']}")
    d2.markdown(f"**Jurisdiction:** {jurisdiction_label(row['jurisdiction'])}")
    d3.markdown(f"**Neighborhood:** {row['neighborhood']}")

    d4, d5, d6 = st.columns(3)
    d4.markdown(f"**Rent:** {rent_display(row)}")
    d5.markdown(f"**Status:** {status_label(row['consideration_status'])}")
    d6.markdown(f"**In Final Comparison:** {flag_label(row['include_in_final_comparison'])}")

    st.markdown("---")

    st.subheader("Data Coverage")
    st.markdown(f"**Coverage level:** {coverage_label(row['public_data_coverage_level'])}")
    if pd.notna(row.get("public_data_coverage_note")):
        st.markdown(f"> {row['public_data_coverage_note']}")
    st.markdown(f"**Coordinates:** {row['coordinate_quality_note']}")

    st.markdown("---")

    st.subheader("Rental Registration")
    st.markdown(f"**Matched:** {flag_label(row['rental_registration_match'])}")
    st.markdown(f"> {row['registration_match_note']}")

    st.markdown("---")

    st.subheader("Nearby Public Records (500m)")
    p1, p2, p3 = st.columns(3)
    p1.metric("Complaints", int(row["complaints_nearby_count"]))
    p2.metric("Permits", int(row["permits_nearby_count"]))
    p3.metric("Active Permits", int(row["active_permits_nearby_count"]))

    st.markdown("---")

    st.subheader("Due-Diligence Signals")

    flags = [
        ("Registration not matched (Seattle only)", row.get("flag_registration_not_found", False),
         "Current Seattle data/matching logic did not find a match. Not a legal conclusion."),
        ("Recent complaints nearby", row.get("flag_recent_complaints_nearby", False),
         "Code violation records opened in the last year exist within 500m."),
        ("Active construction nearby", row.get("flag_active_construction_nearby", False),
         "Active building permits exist within 500m."),
        ("Partial public data coverage", row.get("flag_partial_public_data_coverage", False),
         "This candidate is outside full Seattle city data coverage."),
        ("Availability mismatch", row.get("flag_availability_mismatch", False),
         "Online and actual availability status disagree."),
        ("Availability unclear", row.get("flag_availability_unclear", False),
         "One or both availability statuses were not verified."),
        ("Parking unclear", row.get("flag_parking_unclear", False),
         "Parking information is missing or unspecified."),
        ("Parking unavailable", row.get("flag_parking_unavailable", False),
         "Parking is explicitly unavailable at this property."),
        ("Outside budget", row.get("flag_outside_budget", False),
         "Outside budget — handled separately as a hard filter, not included in due-diligence flag totals."),
    ]

    for label, val, desc in flags:
        if val:
            st.markdown(f"- **{label}** — {desc}")

    if not any(v for _, v, _ in flags):
        st.markdown("No due-diligence flags raised for this apartment.")

    st.markdown("---")
    fc1, fc2, fc3, fc4 = st.columns(4)
    fc1.metric("Public Record", int(row["total_public_record_flags"]))
    fc2.metric("Coverage", int(row["total_coverage_limitation_flags"]))
    fc3.metric("Renter Fit", int(row["total_renter_fit_flags"]))
    fc4.metric("Total Due Diligence", int(row["total_due_diligence_flags"]))


# ================================================================
# PUBLIC RECORD EVIDENCE
# ================================================================
elif section == "Public Record Evidence":
    st.title("Public Record Evidence")

    names = df["apartment_name"].tolist()
    selected = st.selectbox("Select apartment", names, key="evidence_select")
    row = df[df["apartment_name"] == selected].iloc[0]
    apt_id = row["apartment_id"]
    jur = row["jurisdiction"]

    if jur == "shoreline":
        st.warning(
            f"{selected} is in Shoreline. Any nearby records shown are from "
            f"Seattle-side data near the city boundary and represent partial "
            f"boundary context, not complete Shoreline coverage."
        )

    # --- complaints ---
    st.subheader(f"Complaints within 500m ({int(row['complaints_nearby_count'])} total)")
    apt_complaints = complaints[complaints["apartment_id"] == apt_id]

    if len(apt_complaints) > 0:
        display_c = apt_complaints[[
            "record_number", "complaint_address", "complaint_open_date",
            "complaint_status", "complaint_type", "complaint_description",
            "estimated_distance_meters",
        ]].copy()
        display_c.columns = [
            "Record #", "Address", "Open Date", "Status",
            "Type", "Description", "Distance (m)",
        ]
        display_c["Open Date"] = pd.to_datetime(display_c["Open Date"]).dt.date
        st.dataframe(display_c, use_container_width=True, hide_index=True)
    else:
        if jur == "shoreline":
            st.markdown(
                "No Seattle complaint records found within 500m. "
                "This does not imply no Shoreline records exist; "
                "Shoreline requires separate public data integration or manual review."
            )
        else:
            st.markdown(
                "No complaint records found within 500m in the current dataset sample."
            )

    st.markdown("---")

    # --- permits ---
    st.subheader(f"Permits within 500m ({int(row['permits_nearby_count'])} total)")
    apt_permits = permits[permits["apartment_id"] == apt_id]

    if len(apt_permits) > 0:
        display_p = apt_permits[[
            "permit_number", "permit_address", "issued_date",
            "permit_status", "permit_type", "permit_description",
            "estimated_distance_meters",
        ]].copy()
        display_p.columns = [
            "Permit #", "Address", "Issued Date", "Status",
            "Type", "Description", "Distance (m)",
        ]
        display_p["Issued Date"] = pd.to_datetime(display_p["Issued Date"]).dt.date
        st.dataframe(display_p, use_container_width=True, hide_index=True)
    else:
        if jur == "shoreline":
            st.markdown(
                "No Seattle permit records found within 500m. "
                "This does not imply no Shoreline records exist; "
                "Shoreline requires separate public data integration or manual review."
            )
        else:
            st.markdown(
                "No permit records found within 500m in the current dataset sample."
            )


# ================================================================
# METHODOLOGY & LIMITATIONS
# ================================================================
elif section == "Methodology & Limitations":
    st.title("Methodology & Limitations")

    st.subheader("Data Pipeline")
    st.markdown("""
How the data gets from the API to this dashboard:

1. **Ingestion** — A reusable Python client fetches public data from the
   Seattle Open Data portal (Socrata API) for building permits, code complaints,
   and rental property registration. Raw JSON responses are stored locally.

2. **Loading** — Raw records are loaded into PostgreSQL as JSONB rows,
   preserving the original API response for auditability.

3. **Transformation** — dbt Core models transform raw data through three layers:
   - **Staging**: clean, type, and rename source fields
   - **Intermediate**: address matching, proximity calculations, jurisdiction logic
   - **Marts**: apartment-level due-diligence profiles and evidence records

4. **Candidate Data** — Apartment candidates are manually curated in a local CSV
   (not scraped from any website). Coordinates are manually verified from public sources.

5. **Dashboard** — This Streamlit app reads from the mart tables.
   All flags and counts come from dbt, not from code in this app.
""")

    st.subheader("Proximity Matching")
    st.markdown("""
Nearby complaints and permits are identified using approximate distance
at Seattle's latitude (~47.6 N):
- 1 degree latitude = ~111,000 meters
- 1 degree longitude = ~75,000 meters

**Search radius: 500 meters.** A bounding-box pre-filter narrows candidates
before exact distance calculation. This is sufficient for the current scope;
PostGIS would provide geodesic precision.
""")

    st.subheader("Jurisdiction Coverage")
    st.markdown("""
| Jurisdiction | Public Data Available | Notes |
|---|---|---|
| **Seattle** | Permits, code complaints, rental registration | From Seattle Open Data (Socrata) |
| **Shoreline** | Partial (Seattle boundary data only) | Shoreline-specific records need future integration |
| **Other King County** | Not configured | County-level records may be available separately |

Shoreline candidates are valid search candidates. Missing Seattle records for
Shoreline properties should not be interpreted as negative evidence.
""")

    st.subheader("Key Limitations")
    st.markdown("""
- **Sample-limited ingestion**: Each public dataset is currently limited to
  1,000 most recent rows. Counts are lower bounds, not totals.
- **Approximate distance**: Flat-earth approximation, not geodesic.
  Error is negligible at this scale.
- **Address matching**: Registration matching uses exact normalized-address
  comparison. Abbreviation differences may cause misses.
- **Registration non-match is not a legal conclusion**: A non-match means
  the address was not found in the current sample using current matching
  logic — not that the property is unregistered or illegal.
- **Dashboard is read-only**: All data comes from pre-built dbt mart tables.
""")

    st.subheader("Data Sources")
    st.markdown("""
| Source | Provider | Dataset ID |
|---|---|---|
| Building Permits | City of Seattle Open Data | `76t5-zqzr` |
| Code Violations | City of Seattle Open Data | `ez4a-iug7` |
| Rental Registration | City of Seattle Open Data | `j2xh-c7vt` |
| Candidate Apartments | Manually curated (local CSV) | — |
""")
