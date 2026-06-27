# Dashboard

Read-only Streamlit dashboard for the Seattle-Area Rental Intelligence Platform.

## What it shows

- **Executive Summary** — candidate counts, jurisdiction breakdown, total nearby complaints/permits
- **Apartment Comparison** — side-by-side table with filters for jurisdiction, status, and coverage
- **Apartment Detail** — full due-diligence profile for a single apartment with all flags explained
- **Public Record Evidence** — source complaint and permit records backing the proximity counts
- **Methodology & Limitations** — pipeline description, proximity matching, coverage caveats

## Prerequisites

1. PostgreSQL running with candidate data and public datasets loaded
2. dbt models built (including evidence marts)

```bash
make validate-candidates
make load-candidates
make ingest
make dbt-run
make dbt-test
```

## Run

```bash
make dashboard
```

Opens at http://localhost:8501

## Notes

- The dashboard reads from PostgreSQL mart tables only — no business logic is reimplemented
- Local/private candidate data (`candidate_apartments.local.csv`) is gitignored and never committed
- Shoreline coverage is partial; the dashboard explains this per apartment
- Use the "Refresh data" button in the sidebar to reload after re-running dbt
