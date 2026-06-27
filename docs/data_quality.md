# Data Quality

## Overview

Data quality is enforced at multiple layers of the pipeline: during ingestion, within dbt transformations, and through pipeline audit logging. The goal is to catch issues early and make data problems visible rather than silently propagating bad data.

## Ingestion-Level Checks

Performed in the Python ingestion layer before data reaches the warehouse:

| Check | Description |
|-------|-------------|
| API response validation | Verify HTTP status codes and non-empty response bodies |
| Row count validation | Log extracted row counts and flag if zero rows returned |

## dbt Tests

### Generic Tests (Applied Across Models)

| Test | Applied To | Purpose |
|------|------------|---------|
| `not_null` | Primary keys, required fields | Ensure critical fields are populated |
| `unique` | Primary keys, natural keys | Prevent duplicate records |
| `accepted_values` | Status fields, category fields | Validate categorical data |

### Staging Model Tests

| Model | Tests |
|-------|-------|
| `stg_candidate_apartments` | `apartment_id` unique and not null; `apartment_name` not null; `normalized_address` not null; `listed_rent` not null; `neighborhood` not null; `data_privacy_level` accepted values |
| `stg_rental_registration` | `row_id` unique and not null; `registration_id` not null; `address` not null; `status` not null |
| `stg_building_permits` | `row_id` unique and not null; `permit_number` not null; `address` not null; `status` not null |
| `stg_code_violations` | `row_id` unique and not null; `record_number` not null; `address` not null (warn severity); `status` not null |

### Intermediate Model Tests

| Model | Tests |
|-------|-------|
| `int_candidate_apartment_base` | `apartment_id` unique and not null; `jurisdiction` accepted values; `public_data_coverage_level` accepted values; `data_coverage_status` accepted values; `consideration_status` accepted values; `has_coordinates` not null; `meets_hard_filters` not null |
| `int_building_permits_near_candidates` | `apartment_id` unique and not null |
| `int_code_violations_near_candidates` | `apartment_id` unique and not null |
| `int_rental_registration_matches` | `apartment_id` unique and not null; `rental_registration_match` not null; `match_method` accepted values; `match_confidence` accepted values |

### Mart Model Tests

| Model | Tests |
|-------|-------|
| `mart_apartment_due_diligence` | `apartment_id` unique and not null; `jurisdiction` accepted values; `consideration_status` accepted values; not-null checks on all flag totals and key fields |
| `mart_nearby_complaint_evidence` | `apartment_id` not null; `record_number` not null; `estimated_distance_meters` not null |
| `mart_nearby_permit_evidence` | `apartment_id` not null; `permit_number` not null; `estimated_distance_meters` not null |

## Pipeline Audit Log

Each pipeline run records an entry in the audit log with:

| Field | Description |
|-------|-------------|
| `run_id` | Unique identifier for the pipeline run |
| `dataset_name` | Name of the dataset processed |
| `run_timestamp` | When the run started |
| `rows_extracted` | Number of rows pulled from the source |
| `rows_loaded` | Number of rows written to the warehouse |
| `status` | `success`, `partial`, or `failed` |
| `error_message` | Error details if status is not `success` |
| `duration_seconds` | How long the step took |

