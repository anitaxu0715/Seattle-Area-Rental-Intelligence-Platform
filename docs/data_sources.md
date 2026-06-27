# Data Sources

## Overview

This project combines manually curated apartment data with official public open data sources. No data is scraped from commercial listing platforms.

## Source 1: Candidate Apartments

| Field | Value |
|-------|-------|
| Type | Manual CSV |
| File | `data/seed/candidate_apartments.csv` |
| Refresh | Manual updates by project owner |
| Purpose | Core list of apartment candidates being evaluated |

The candidate list is curated from the project owner's own apartment search notes. It includes apartment names, addresses, rent, amenities, and personal observations. This data represents the "question" the platform is designed to answer: which of these apartments is the best fit?

## Source 2: Rental Property Registration

| Field | Value |
|-------|-------|
| Provider | City of Seattle |
| Portal | [data.seattle.gov](https://data.seattle.gov/) |
| Dataset ID | `j2xh-c7vt` |
| API | Socrata (SODA) |
| Format | JSON |
| Purpose | Verify whether candidate apartments are registered as rental properties |

Seattle requires most rental properties to be registered. Matching a candidate apartment to this dataset provides a basic verification signal. A non-match is flagged as "not found in current data" — not as a violation.

## Source 3: Building Permits

| Field | Value |
|-------|-------|
| Provider | City of Seattle |
| Portal | [data.seattle.gov](https://data.seattle.gov/) |
| Dataset ID | `76t5-zqzr` |
| API | Socrata (SODA) |
| Format | JSON |
| Purpose | Identify nearby construction or development activity |

Active building permits near a candidate apartment can indicate construction noise, neighborhood disruption, or upcoming development. The platform uses geocoordinates to identify permits within a configurable radius.

## Source 4: Code Violations

| Field | Value |
|-------|-------|
| Provider | City of Seattle |
| Portal | [data.seattle.gov](https://data.seattle.gov/) |
| Dataset ID | `ez4a-iug7` |
| API | Socrata (SODA) |
| Format | JSON |
| Purpose | Identify complaint or violation history near candidate apartments |

Code violations include complaints about building conditions, noise, and other issues. The platform aggregates these by proximity to candidate apartments to generate risk flags like `high_code_complaint_density` and `recent_violation_nearby`.

## Source 5: Neighborhood Boundaries

| Field | Value |
|-------|-------|
| Provider | City of Seattle GIS |
| Portal | [Seattle GeoData](https://data-seattlecitygis.opendata.arcgis.com/) |
| Dataset | Neighborhood Map Atlas Neighborhoods |
| Format | GeoJSON |
| Purpose | Support neighborhood-level aggregation and spatial joins |

Neighborhood boundary polygons enable grouping complaints, permits, and apartments by neighborhood for comparative analysis.

## API Details

### Socrata (SODA) API

Most Seattle Open Data datasets are accessed via the Socrata Open Data API (SODA):

- Base pattern: `https://data.seattle.gov/resource/{dataset_id}.json`
- Pagination: `$limit` and `$offset` parameters
- Filtering: `$where` clause with SoQL syntax
- App token: Optional but recommended to avoid rate limiting
- Rate limits: 1,000 requests/hour without token; higher with token

### Data Refresh Strategy

| Dataset | Refresh Frequency | Lookback Window |
|---------|-------------------|-----------------|
| Candidate apartments | Manual | N/A |
| Rental registration | Weekly | Full dataset |
| Building permits | Weekly | Last 365 days |
| Code violations | Weekly | Last 730 days |
| Neighborhood boundaries | Monthly | Full dataset |

## Implementation Status

| Dataset | Ingestion Implemented | Raw Table | Audit Logging |
|---------|----------------------|-----------|---------------|
| Candidate Apartments | Not yet | — | — |
| **Rental Property Registration** | **Yes** | `raw.raw_rental_registration` | **Yes** |
| **Building Permits** | **Yes** | `raw.raw_building_permits` | **Yes** |
| **Code Violations** | **Yes** | `raw.raw_code_violations` | **Yes** |
| Neighborhood Boundaries | Not yet | — | — |

All three Socrata datasets are ingested via a reusable pipeline: API extraction with pagination and retry, timestamped raw JSON file storage, PostgreSQL JSONB loading, and per-dataset audit logging. Field names are verified against the live Socrata API metadata.

## Legal and Ethical Notes

- All public data is sourced from official government open data portals
- Data is used for personal due-diligence analysis, not commercial purposes
- No personally identifiable information beyond publicly available addresses
- Risk flags are informational signals, not legal determinations
