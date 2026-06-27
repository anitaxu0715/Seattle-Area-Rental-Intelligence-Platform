# Resume Bullets

Pick the ones most relevant to the role. Adapt as needed.

---

- Built a Python + PostgreSQL + dbt + Streamlit pipeline that ingests Seattle public records and compares them against apartment candidates to surface nearby code complaints, building permits, and registration status.

- Wrote a reusable Socrata API client with pagination, retry, and timeout handling to pull building permits, code violations, and rental registration from Seattle's Open Data portal.

- Stored raw API responses as JSONB in PostgreSQL so downstream dbt models could extract fields without losing the original data.

- Created 11 dbt models (staging, intermediate, mart) with 70 data quality tests covering nulls, uniqueness, accepted values, and cross-model consistency.

- Implemented 500m proximity matching using coordinate-based distance calculations, then built evidence marts so every complaint/permit count can be traced to individual source records.

- Handled a real jurisdiction edge case: Seattle and Shoreline have different public data availability, so the pipeline tracks jurisdiction per apartment and doesn't penalize Shoreline candidates for missing Seattle records.

- Designed a local/private candidate workflow where real apartment search notes stay in a gitignored CSV while a demo file is committed for reproducibility.

- Built a Streamlit dashboard with five pages (summary, comparison, detail, evidence, methodology) that reads from dbt marts without reimplementing any business logic.

- Validated all proximity results against source data — every complaint and permit count is backed by individual records with verified distances under 500m.
