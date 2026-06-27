# Architecture

## System Overview

The Seattle Rental Intelligence Platform follows a standard ELT (Extract, Load, Transform) architecture with layered data modeling.

```
┌─────────────────────────────────────────────────────────┐
│                     DATA SOURCES                         │
│                                                          │
│  ┌──────────────────┐    ┌────────────────────────────┐  │
│  │ Candidate CSV     │    │ Seattle Open Data (Socrata) │  │
│  │ (manual curation) │    │ - Rental Registration      │  │
│  │                   │    │ - Building Permits          │  │
│  │                   │    │ - Code Violations           │  │
│  └────────┬─────────┘    │ - Neighborhood Boundaries   │  │
│           │               └──────────────┬──────────────┘  │
└───────────┼──────────────────────────────┼──────────────┘
            │                              │
            ▼                              ▼
┌─────────────────────────────────────────────────────────┐
│                  INGESTION LAYER (Python)                 │
│                                                          │
│  ┌──────────────────┐    ┌────────────────────────────┐  │
│  │ CSV Loader        │    │ Socrata API Client         │  │
│  │                   │    │ - Pagination               │  │
│  │                   │    │ - Rate limiting             │  │
│  │                   │    │ - Error handling            │  │
│  └────────┬─────────┘    └──────────────┬──────────────┘  │
│           │                              │                │
│           └──────────┬───────────────────┘                │
│                      ▼                                    │
│           ┌─────────────────────┐                         │
│           │ Load to PostgreSQL   │                         │
│           │ (raw schema)         │                         │
│           └─────────┬───────────┘                         │
└─────────────────────┼───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              WAREHOUSE (PostgreSQL + PostGIS)             │
│                                                          │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  raw     │  │ staging  │  │   int    │  │  marts   │  │
│  │         │──►│          │──►│          │──►│          │  │
│  │ schema  │  │  schema  │  │  schema  │  │  schema  │  │
│  └─────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                          │
│  Managed by dbt Core                                     │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   DATA QUALITY LAYER                     │
│                                                          │
│  ┌─────────────────────┐    ┌─────────────────────────┐  │
│  │ dbt Tests            │    │ Pipeline Audit Log       │  │
│  │ - not_null           │    │ - run timestamp          │  │
│  │ - unique             │    │ - rows extracted/loaded  │  │
│  │ - accepted_values    │    │ - status and errors      │  │
│  │ - relationships      │    │                          │  │
│  │ - freshness          │    │                          │  │
│  └─────────────────────┘    └─────────────────────────┘  │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                      │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Streamlit Dashboard                                  │  │
│  │ - Apartment Comparison                               │  │
│  │ - Due Diligence Profile                              │  │
│  │ - Neighborhood Comparison                            │  │
│  │ - Search Gaps                                        │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              ORCHESTRATION (Makefile / future Airflow)    │
│                                                          │
│  Ingest ──► Load ──► dbt Run ──► dbt Test ──► Audit Log  │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Extract**: Python ingestion layer pulls data from Seattle Open Data APIs (Socrata) and reads the candidate apartments CSV
2. **Load**: Raw data is loaded into PostgreSQL `raw` schema tables with minimal transformation
3. **Transform**: dbt models clean, normalize, join, and aggregate data through three layers:
   - **Staging**: One model per source, cleaned and typed
   - **Intermediate**: Business logic — address matching, proximity calculations, flag generation
   - **Marts**: Final analytical tables — apartment profiles, neighborhood summaries, risk dashboards
4. **Test**: dbt tests validate data quality at each layer
5. **Present**: Streamlit reads from mart tables to render the dashboard

## Schema Design

| Schema | Purpose | Example Tables |
|--------|---------|----------------|
| `raw` | Unmodified source data | `raw_candidate_apartments`, `raw_building_permits` |
| `staging` | Cleaned, typed, renamed | `stg_candidate_apartments`, `stg_building_permits`, `stg_code_violations`, `stg_rental_registration` |
| `int` | Joined and enriched | `int_candidate_apartment_base`, `int_building_permits_near_candidates`, `int_code_violations_near_candidates`, `int_rental_registration_matches` |
| `marts` | Analytics-ready | `mart_apartment_due_diligence`, `mart_nearby_complaint_evidence`, `mart_nearby_permit_evidence` |

## Key Design Decisions

- **PostgreSQL 15 with PostGIS Docker image**: Keeps the project self-contained and runnable locally via Docker. PostGIS is available for future spatial upgrades; current proximity matching uses approximate distance calculations in SQL
- **dbt Core over dbt Cloud**: Free, open-source, and demonstrates SQL modeling skill directly
- **Socrata API over bulk downloads**: Demonstrates API client engineering and supports incremental loads
- **Rule-based scoring over ML**: Transparent, explainable, and appropriate for the problem scope
