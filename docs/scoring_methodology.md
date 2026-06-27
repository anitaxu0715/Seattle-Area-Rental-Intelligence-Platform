# Scoring Methodology

## Overview

The Seattle Rental Intelligence Platform uses **transparent, rule-based scoring** to evaluate candidate apartments. This is a deliberate design choice: renters should be able to understand exactly why an apartment received a particular score or risk flag.

There is no machine learning in the scoring layer. Every flag and score is traceable to a specific data condition.

## Risk Flags

Risk flags are binary due-diligence signals generated from public data. Each flag indicates a condition that a renter should investigate further — **not a legal conclusion**.

### Implemented Flags

| Flag | Condition | Data Source | Status |
|------|-----------|-------------|--------|
| `flag_registration_not_found` | Apartment is inside Seattle and address not matched in rental registration data | Rental Property Registration | **Implemented** |
| `flag_recent_complaints_nearby` | Code violations opened within last 12 months found within 500m | Code Violations | **Implemented** |
| `flag_active_construction_nearby` | Active building permit found within 500m of apartment | Building Permits | **Implemented** |
| `flag_parking_unclear` | Parking information is missing or unspecified | Candidate apartments CSV | **Implemented** |
| `flag_parking_unavailable` | Parking is explicitly unavailable (`parking_available = 'no'`) | Candidate apartments CSV | **Implemented** |
| `flag_partial_public_data_coverage` | Apartment is outside Seattle city limits; city datasets may not cover it (coverage limitation, not risk) | Candidate apartments CSV | **Implemented** |
| `flag_availability_mismatch` | Online and actual availability status disagree | Candidate apartments CSV | **Implemented** |
| `flag_availability_unclear` | One or both availability statuses are unclear | Candidate apartments CSV | **Implemented** |
| `flag_outside_budget` | Listed rent exceeds $2,500 (tracked separately from due-diligence totals) | Candidate apartments CSV | **Implemented** |

### Planned Flags (Not Yet Implemented)

| Flag | Condition | Data Source |
|------|-----------|-------------|
| `high_code_complaint_density` | Above-average complaint count within radius | Code Violations |
| `high_permit_activity_nearby` | Above-average permit count within radius | Building Permits |
| `high_pet_policy_friction` | Pet policy is restrictive or unclear | Candidate apartments CSV |
| `management_communication_concern` | Flagged based on manual notes about responsiveness | Manual observation (CSV) |
| `new_building_limited_history` | Building built within last 2 years, limited public record history | Candidate apartments CSV |
| `address_verification_issue` | Address normalization produced low-confidence match | Address matching layer |

### Flag Language

Flags are worded as **observations, not judgments**:
- "Not found in current rental registration data" (not "unregistered" or "illegal")
- "Above-average complaint density nearby" (not "dangerous area")
- "Active construction permit within 500m" (not "noisy location")

## Design Principles

1. **Transparency over sophistication**: A renter can trace any score back to specific data points
2. **Signals over verdicts**: The platform surfaces information for human judgment, not automated decisions
3. **Configurable weights**: Different renters can adjust preferences to reflect their own priorities
4. **Conservative defaults**: When data is missing, the system does not assume the best case

## Data Coverage

Seattle Open Data primarily covers the City of Seattle. Apartments outside city limits (e.g., Shoreline, Bellevue, Renton) may not appear in Seattle datasets.

The platform tracks this with `jurisdiction` and `public_data_coverage_level` fields:
- `jurisdiction`: `seattle`, `shoreline`, `other_king_county`, or `unknown`
- `public_data_coverage_level`: e.g., `seattle_city_open_data_available`, `shoreline_partial_manual_review`

The `flag_registration_not_found` flag is **only raised for apartments in the `seattle` jurisdiction**. Apartments outside Seattle are not penalized for missing Seattle-specific records. The `flag_partial_public_data_coverage` flag is an informational coverage limitation signal, not a risk indicator.

## Proximity Matching

The current implementation uses approximate distance calculations at Seattle's latitude (~47.6°N):
- 1° latitude ≈ 111,000 meters
- 1° longitude ≈ 75,000 meters (111,000 × cos(47.6°))

Search radius: **500 meters**. A bounding-box pre-filter improves performance before exact distance calculation.

This is an approximation suitable for the project scope. A future version could use PostGIS for precise geodesic distance.

## Future Considerations

Potential scoring enhancements documented in `docs/future_improvements.md`:
- Weighted rental fit score based on personal preferences (budget, parking, quietness, etc.)
- Distance-weighted spatial scoring (using PostGIS calculations)
- Temporal weighting (recent complaints weighted more than older ones)
- Comparison scoring (rank relative to other candidates, not just absolute)

These enhancements would still be rule-based and transparent, not ML-driven.
