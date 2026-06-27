# Validation Notes

## mart_apartment_due_diligence — Validation Summary

Validated on 2026-06-18 against 6 candidate apartments (5 in Seattle, 1 in Shoreline) with 1,000 rows ingested per public dataset.

### Per-Apartment Results

| Apartment | City | Coverage | Reg Match | Complaints (500m) | Permits (500m) | Flags | Assessment |
|-----------|------|----------|-----------|-------------------|----------------|-------|------------|
| Capitol Hill Apartments | Seattle | inside_seattle | no_match | 14 | 8 | 3 | Reasonable — dense urban neighborhood |
| Ballard Commons | Seattle | inside_seattle | no_match | 9 | 5 | 3 | Reasonable — active neighborhood |
| University Heights Living | Seattle | inside_seattle | no_match | 18 | 2 | 3 | Highest complaint density; near UW campus, plausible |
| Beacon Hill Terrace | Seattle | inside_seattle | no_match | 0 | 2 | 2 | 0 complaints within 500m; 11 exist within 1km — radius cutoff, not data gap |
| Fremont Place | Seattle | inside_seattle | no_match | 6 | 6 | 3 | Reasonable — includes new apartment construction nearby |
| Shoreline Garden Apartments | Shoreline | outside_seattle | no_match | 0 | 0 | 1 | Correct — outside Seattle, only coverage flag raised |

### Consistency Checks Passed

- `complaints_nearby_count >= recent_complaints_nearby_count` for all apartments
- `recent_complaints_nearby_count >= open_violations_nearby_count` for all apartments
- `permits_nearby_count >= recent_permits_nearby_count` for all apartments
- `permits_nearby_count >= active_permits_nearby_count` for all apartments
- `flag_registration_not_found` is only `true` when `jurisdiction = 'seattle'`
- `flag_partial_public_data_coverage` matches `jurisdiction != 'seattle'`

### Risk Flag Language Verification

All flag column names use observational, due-diligence language:
- `flag_registration_not_found` — not "unregistered" or "illegal"
- `flag_recent_complaints_nearby` — not "dangerous area"
- `flag_active_construction_nearby` — not "noisy location"
- `flag_parking_unclear` — not "parking unavailable" (separate `flag_parking_unavailable` for explicit "no")
- `flag_partial_public_data_coverage` — not "uncovered" or "risky"

No flag implies a legal conclusion or safety judgment.

### Outside-Seattle Verification

The Shoreline apartment (APT006) correctly:
- Has `data_coverage_status = 'outside_seattle'`
- Has `public_data_coverage_note` explaining the limitation
- Has `match_confidence = 'not_applicable'` (not `low`)
- Has `flag_registration_not_found = false` (not penalized for missing Seattle records)
- Has `flag_partial_public_data_coverage = true` as an informational signal
- Shows 0 complaints and 0 permits (Seattle datasets don't cover Shoreline)

## Coordinate Completion and Proximity Results (2026-06-24)

Manually verified latitude/longitude coordinates were added for all 5 local candidate apartments. Proximity matching is now active.

### Results after coordinate addition

| Apartment | Jurisdiction | Complaints (500m) | Permits (500m) | Explanation |
|-----------|-------------|:---:|:---:|---|
| Verdant | shoreline | 0 | 2 | 2 Seattle permits found near the Seattle/Shoreline boundary |
| Canopy | shoreline | 0 | 0 | Too far from Seattle boundary for Seattle records to appear |
| Modera Northgate | seattle | 6 | 4 | Active Northgate transit development area |
| Augusta | seattle | 8 | 2 | Dense U-District residential area |
| Arista | seattle | 8 | 3 | University Village / Ravenna residential area |

All proximity counts have been traced to specific source records with verified distances under 500m. See [proximity_validation.md](proximity_validation.md) for full evidence.

### Shoreline boundary behavior

Verdant's 2 permits are Seattle-jurisdiction records that fall within 500m because the apartment is near the Seattle/Shoreline border. Canopy is farther north and shows 0 — both results are correct. Shoreline-specific public data would require future integration with Shoreline or King County sources.

## Known Limitations

### 1,000-Row Sample Ingestion Limit

Each public dataset is currently limited to 1,000 most recent rows via the `default_limit` setting in `datasets.yml`. This means:

- The proximity search may miss older complaints or permits that were not in the ingested sample.
- Apartments in areas with lower recent activity may show 0 nearby records even if historical records exist.
- Increasing `default_limit` (or removing it) would provide more complete coverage but increase ingestion time.

**Impact**: Complaint and permit counts are lower bounds, not totals. The `recent_complaints_nearby_count` is the most reliable since the 1,000-row sample is ordered by date and covers the most recent records.

### Approximate Distance Calculation

The proximity search uses flat-earth approximation at Seattle's latitude (~47.6°N):
- 1° latitude ≈ 111,000 meters
- 1° longitude ≈ 75,000 meters

At the 500m search radius, the error is negligible (under 1 meter). The bounding-box pre-filter uses slightly larger thresholds (0.006° lat, 0.008° lng ≈ ~666m × ~600m) to avoid missing edge cases before exact distance calculation.

**Future improvement**: PostGIS `ST_DWithin` would provide geodesic precision and spatial indexing.

### Address Matching Limitations

Rental registration matching uses exact normalized address comparison (`upper(trim(address))`). This means:

- Addresses with different formatting (e.g., "1234 E Pine St" vs "1234 East Pine Street") will not match.
- Unit/suite numbers are not currently handled.
- Abbreviation differences (ST vs STREET, AVE vs AVENUE, E vs EAST) will cause mismatches.

**Current result**: All candidate apartments show `no_match` because the seed data uses fictional addresses (e.g., "1234 E Pine St" doesn't exist in Seattle's registration data). This is expected for placeholder data.

**Future improvement**: Fuzzy matching, address standardization (e.g., via `usaddress` library), or coordinate-based matching within a small radius.

### Registration Flag Scope

`flag_registration_not_found` is only raised when:
1. The apartment's `data_coverage_status` is `inside_seattle`, AND
2. No exact address match was found in the rental registration dataset.

This design prevents false positives for apartments outside Seattle city limits, where the City of Seattle registration dataset would not be expected to contain records.

A `no_match` result does not mean the property is unregistered — it means the address was not found in the current ingested sample using exact address matching. The property may be registered under a different address format, unit number, or may simply not be in the 1,000-row sample.

### Cross-Join Performance

The proximity models (`int_code_violations_near_candidates` and `int_building_permits_near_candidates`) use `CROSS JOIN` with a bounding-box pre-filter. With 6 candidates and 1,000 rows per dataset, this produces at most 6,000 candidate pairs before filtering — acceptable for development.

At production scale (thousands of candidates × hundreds of thousands of records), this would need spatial indexing via PostGIS.
