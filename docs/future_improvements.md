# Future Improvements

## Beyond MVP

This document tracks potential enhancements beyond the initial MVP scope.

### Jurisdiction-Specific Data Expansion
- Add Shoreline permit/code enforcement data if a stable public data source is available
- Add King County parcel/assessor data for candidates outside Seattle
- Add manual review tables for jurisdictions without bulk APIs
- Support jurisdiction-specific rental registration matching
- Track data freshness per jurisdiction

### Data Sources
- King County parcel and property tax data for ownership history
- Sound Transit GTFS data for precise transit access scoring
- Seattle 911 incident response data for safety signals
- Walk Score or similar open transit/walkability metrics

### Address Matching and Scoring
- Fuzzy address matching in Python (e.g., via `usaddress` library) to improve rental registration match rates
- Python-side risk flag aggregation and rental fit scoring (currently all flag logic is in dbt SQL)
- Geocoding API integration for automated coordinate lookup

### Data Engineering
- Incremental loading for large datasets (building permits, code violations)
- CDC (change data capture) tracking to detect updated/deleted records
- Data versioning to compare snapshots over time
- Partitioned tables for time-series analysis

### Geospatial
- PostGIS spatial indexing for faster proximity queries
- Configurable search radius per dataset
- Walk-time isochrone analysis instead of straight-line distance
- Map visualization layer in the dashboard

### Scoring
- Distance-weighted scoring (closer complaints weighted more heavily)
- Temporal decay (recent events weighted more than old ones)
- Relative scoring (rank candidates against each other, not just absolute)
- Configurable scoring profiles for different renter personas

### Dashboard
- Interactive map view with apartment pins and risk overlays
- Side-by-side apartment comparison
- PDF export of due-diligence reports
- Saved search configurations

### Orchestration
- Current pipeline orchestration is Makefile-based (`make ingest`, `make dbt-run`, etc.)
- A stub Airflow DAG exists in `airflow/dags/` but is not implemented
- Airflow is a planned future upgrade, not required to run the current project
- Install `requirements-airflow.txt` when ready to implement

### Infrastructure
- Automated testing in CI/CD pipeline
- Pre-commit hooks for SQL linting
- dbt documentation site generation
- Terraform or Pulumi for cloud deployment option

### Observability
- Pipeline alerting (email or Slack on failure)
- Data freshness monitoring dashboard
- Row count trend tracking to detect anomalies
- dbt test result history tracking
