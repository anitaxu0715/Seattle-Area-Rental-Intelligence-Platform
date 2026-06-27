# Candidate Data Collection Guide

## Overview

Candidate apartment data is the core input to the Seattle-Area Rental Intelligence Platform. It represents the apartments you are personally evaluating during an apartment search across Seattle and nearby cities.

Candidates may be in Seattle, Shoreline, or other King County jurisdictions. The `city` field determines which public data coverage applies — Seattle has the richest open data, while other jurisdictions may require manual review or future data integration. This data is **manually curated** — the project does not scrape Zillow, Apartments.com, Google Maps, or any commercial listing platform.

## File Types

| File | Purpose | Committed to Git |
|------|---------|-----------------|
| `candidate_apartments.example.csv` | Public demo data for running the pipeline | Yes |
| `candidate_apartments.local.csv` | Your real apartment search notes | **No** (gitignored) |

## Search Scope

This project focuses on a real apartment search:
- **Unit type**: 1B1B
- **Max rent**: $2,500/month

These hard filters are defined in `personal_preferences.yml` and evaluated in the dbt intermediate layer. They apply only to candidate apartment records — public enrichment datasets (permits, complaints, registration) are ingested independently.

### Candidate Status

Not every apartment in the dataset needs to be a final recommendation:

| Status | Meaning | In final comparison? |
|--------|---------|---------------------|
| `eligible` | Meets hard filters, should be considered | Yes |
| `rejected` | Was considered but excluded (e.g., over budget) | No |
| `benchmark` | Useful for comparison but not recommended | No |

Rejected and benchmark apartments stay in the dataset for transparency. The mart clearly marks them with `include_in_final_comparison = false` and `meets_hard_filters = false`.

**Example**: An over-budget apartment like Arista Residences can be included as `benchmark` with `exclusion_reason = outside_budget`. It will appear in the mart with `flag_outside_budget = true` but won't be recommended.

### Rent Model

`listed_rent` is the **representative rent** for your decision — not the universal rent for the whole building. It is usually based on a specific unit, a leasing quote, or a floor plan range.

| Field | Purpose |
|-------|---------|
| `listed_rent` | Representative rent used in comparison and hard-filter logic (required) |
| `listed_rent_min` | Lowest relevant rent observed for the target unit type (optional) |
| `listed_rent_max` | Highest relevant rent observed for the target unit type (optional) |
| `rent_basis` | How the rent was obtained: `specific_unit`, `floorplan_range`, `leasing_quote`, `estimated_from_listing`, `unknown` |
| `rent_notes` | Professional context about the rent (e.g., "range for 1B1B units in this building") |

If only a range is known, set `listed_rent` to the most relevant representative number (e.g., the midpoint or the quote you received), and fill `listed_rent_min`/`listed_rent_max` for context.

## How to Add Your Own Data

1. Copy the example file:
   ```
   cp data/seed/candidate_apartments.example.csv data/seed/candidate_apartments.local.csv
   ```

2. Replace the demo rows with your real apartment candidates.

3. Run validation:
   ```
   make validate-candidates
   ```

4. Load into the database:
   ```
   make load-candidates
   ```

The loader automatically prefers `candidate_apartments.local.csv` over the example file. You can also set `CANDIDATE_APARTMENTS_FILE` to point to any file.

## Required Fields

| Field | Required | Description |
|-------|----------|-------------|
| `apartment_id` | Yes | Unique ID you assign (e.g., APT001) |
| `apartment_name` | Yes | Building or community name |
| `address` | Yes | Street address |
| `city` | Yes | City name |
| `state` | Yes | State abbreviation |
| `zip_code` | Yes | ZIP code |
| `neighborhood` | Yes | Neighborhood name |
| `listed_rent` | Yes | Monthly rent in USD |

## Optional Fields

| Field | Description |
|-------|-------------|
| `unit_type` | e.g., "1B1B", "Studio", "2B1B" |
| `square_feet` | Unit square footage |
| `year_built` | Year the building was constructed |
| `parking_available` | e.g., "garage", "surface lot", "underground", "none" |
| `parking_fee` | Monthly parking cost |
| `pet_policy` | e.g., "cats only", "cats and dogs up to 50 lbs", "no pets" |
| `online_availability_status` | What the listing website showed |
| `actual_availability_status` | What the leasing office confirmed |
| `tour_date` | Date you toured (YYYY-MM-DD) |
| `management_notes` | Professional observations about management |
| `personal_notes` | Private notes (only in local file) |
| `latitude` | Latitude coordinate |
| `longitude` | Longitude coordinate |
| `location_source` | How coordinates were obtained: `manual`, `public_record`, `unknown` |
| `location_confidence` | Coordinate accuracy: `high`, `medium`, `low`, `unknown` |
| `data_privacy_level` | `public_demo`, `portfolio_safe`, or `private_local` |
| `notes_public_safe` | Notes safe to include in portfolio/screenshots |

## How to Prepare Local Candidate Data

Before adding rows to `candidate_apartments.local.csv`, follow this checklist:

- [ ] Use public apartment building names and street addresses only
- [ ] Do not include names of leasing agents, staff, or other individuals
- [ ] Do not include private conversations, emails, or phone call transcripts
- [ ] Write `management_notes` and `notes_public_safe` in professional, factual language
- [ ] Keep `personal_notes` for local-only observations — this column is never shown in portfolio output
- [ ] Manually verify `latitude` and `longitude` from a public source (city GIS portal, public property records)
- [ ] Do not scrape coordinates from Google Maps or any commercial service
- [ ] Set `data_privacy_level` to `private_local` for real search data
- [ ] Run `make validate-candidates` after every edit to catch errors early
- [ ] Do **not** commit `candidate_apartments.local.csv` to git — it is gitignored for your protection

### Column-by-column guide

| Column | How to fill | Example |
|--------|------------|---------|
| `apartment_id` | Assign a unique short ID | `APT001` |
| `apartment_name` | Public building or community name | `The Lydian` |
| `address` | Street address from the listing | `401 Terry Ave N` |
| `city` | City name | `Seattle` |
| `state` | Two-letter state code | `WA` |
| `zip_code` | 5-digit ZIP | `98109` |
| `neighborhood` | Neighborhood or area name | `South Lake Union` |
| `listed_rent` | Monthly rent shown on the listing | `2150` |
| `unit_type` | Unit layout | `1B1B` |
| `square_feet` | Leave blank if unknown | `680` |
| `year_built` | Leave blank if unknown | `2019` |
| `parking_available` | `garage`, `surface lot`, `underground`, `street`, or `none` | `underground` |
| `parking_fee` | Monthly cost, blank if included or N/A | `200` |
| `pet_policy` | Summarize concisely | `cats and dogs up to 50 lbs` |
| `online_availability_status` | What the website showed | `available` |
| `actual_availability_status` | What the leasing office confirmed | `available` |
| `tour_date` | Date you visited, YYYY-MM-DD format | `2025-07-20` |
| `management_notes` | Professional observations only | `responsive to email inquiries` |
| `personal_notes` | Private — anything useful for your decision | (keep private) |
| `latitude` | From public source | `47.6235` |
| `longitude` | From public source | `-122.3378` |
| `location_source` | `manual`, `public_record`, or `unknown` | `manual` |
| `location_confidence` | `high`, `medium`, `low`, or `unknown` | `high` |
| `data_privacy_level` | Use `private_local` for real data | `private_local` |
| `notes_public_safe` | Portfolio-safe summary | `Modern building near transit` |

### Workflow after filling

```bash
# Validate your data
make validate-candidates

# Load into PostgreSQL
make load-candidates

# Rebuild dbt models with your real data
make dbt-run

# Run data quality tests
make dbt-test
```

You can also specify the file explicitly:

```bash
CANDIDATE_APARTMENTS_FILE=data/seed/candidate_apartments.local.csv make load-candidates
```

## Why Coordinates Matter

Latitude and longitude are **required for 500m proximity matching** — the feature that finds nearby code complaints and building permits. Without coordinates:

- `complaints_nearby_count` and `permits_nearby_count` will show as **0**, even if public records exist nearby
- `has_coordinates` will be `false` in the mart
- `coordinate_quality_note` will explain that proximity matching is unavailable

The apartment will still appear in the mart with all other fields (registration match, availability flags, parking flags, etc.) — only the proximity-based counts are affected.

### How to check coordinate status

```bash
make coordinate-status
```

This shows which candidates are missing coordinates without modifying any data.

### Adding manually verified coordinates

1. Look up the apartment's street address in a public source:
   - King County Parcel Viewer
   - City GIS portals (Seattle, Shoreline)
   - Public property records

2. Get the decimal latitude and longitude for the building location.

3. Add the values to the `latitude` and `longitude` columns in your CSV.

4. Set the metadata columns:
   - `location_source` = `manual` (you looked it up yourself)
   - `location_confidence` = `high` (coordinate is for the building itself) or `medium` (approximate block-level)

5. Validate and reload:
   ```bash
   make validate-candidates
   make load-candidates
   make dbt-run
   ```

### Coordinate format

- Use **decimal degrees** (e.g., `47.6062`, not `47°36'22"`)
- Seattle-area **latitude** is typically between 47.3 and 47.9
- Seattle-area **longitude** is typically between -122.6 and -122.0 (negative)

### What not to do

- Do **not** scrape coordinates from Google Maps or commercial services
- Do **not** use automated geocoding APIs
- Do **not** guess coordinates — if unsure, leave them blank and set `location_confidence = unknown`

### Jurisdiction note for proximity matching

Even with coordinates, proximity results depend on which public datasets are ingested:

- **Seattle candidates**: Can match against Seattle building permits and code complaints within 500m
- **Shoreline candidates**: May still show 0 for Seattle public records because Shoreline is a different jurisdiction. Equivalent Shoreline/King County data requires future integration or manual review

## Privacy Levels

| Level | Meaning | Use |
|-------|---------|-----|
| `public_demo` | Fictional or obviously generic data | Example file, demos |
| `portfolio_safe` | Real data written in professional language | Portfolio screenshots, presentations |
| `private_local` | Contains personal observations | Local analysis only, never committed |

## Notes Guidelines

For `management_notes` and `notes_public_safe`, use professional, factual language:

**Good examples:**
- "Parking information required follow-up"
- "Online availability differed from leasing response"
- "Pet policy required additional documentation"
- "Management response was timely"
- "New building with limited public history"

**Avoid:**
- Personal opinions or emotional language
- Names of specific staff members
- Private financial details
- Anything you wouldn't want in a professional portfolio
