# Data Dictionary

## Overview

This document defines the key fields across all data layers. Fields are organized by layer (raw, staging, intermediate, marts) and will be updated as models are implemented.

## Seed Data

### candidate_apartments.csv

| Column | Type | Description |
|--------|------|-------------|
| `apartment_id` | string | Unique identifier for each candidate (e.g., APT001) |
| `apartment_name` | string | Display name of the apartment or building |
| `address` | string | Street address |
| `city` | string | City name |
| `state` | string | State abbreviation |
| `zip_code` | string | 5-digit ZIP code |
| `neighborhood` | string | Neighborhood name |
| `listed_rent` | numeric | Representative monthly rent in USD |
| `listed_rent_min` | numeric | Lowest relevant rent for target unit type (optional) |
| `listed_rent_max` | numeric | Highest relevant rent for target unit type (optional) |
| `rent_basis` | string | How rent was obtained: `specific_unit`, `floorplan_range`, `leasing_quote`, `estimated_from_listing`, `unknown` |
| `rent_notes` | string | Context about the rent figure |
| `unit_type` | string | Unit layout (e.g., `1B1B`) |
| `square_feet` | integer | Unit square footage |
| `year_built` | integer | Year the building was constructed |
| `parking_available` | string | Parking type: `garage`, `surface lot`, `underground`, `none`, or empty |
| `parking_fee` | numeric | Monthly parking cost in USD |
| `pet_policy` | string | Pet policy summary |
| `online_availability_status` | string | Availability shown on the listing website |
| `actual_availability_status` | string | Availability confirmed by leasing office |
| `tour_date` | date | Date toured (YYYY-MM-DD) |
| `management_notes` | string | Professional observations about management |
| `personal_notes` | string | Private notes (local file only, never committed) |
| `latitude` | float | Latitude coordinate |
| `longitude` | float | Longitude coordinate |
| `location_source` | string | How coordinates were obtained: `manual`, `public_record`, `unknown` |
| `location_confidence` | string | Coordinate accuracy: `high`, `medium`, `low`, `unknown` |
| `data_privacy_level` | string | `public_demo`, `portfolio_safe`, or `private_local` |
| `notes_public_safe` | string | Notes safe to include in portfolio/screenshots |
| `consideration_status` | string | `eligible`, `rejected`, or `benchmark` |
| `exclusion_reason` | string | Why excluded: `none`, `outside_budget`, etc. |
| `include_in_final_comparison` | boolean | Whether to include in final comparison |

## Staging Layer

### stg_building_permits

Extracted from `raw.raw_building_permits` JSONB records.

| Column | Type | Source Field | Description |
|--------|------|-------------|-------------|
| `row_id` | integer | `id` | Surrogate key from raw table |
| `permit_number` | text | `permitnum` | Seattle permit number |
| `permit_type` | text | `permittypedesc` | Permit type description |
| `permit_class` | text | `permitclass` | Permit class (e.g., Multifamily, Commercial) |
| `permit_class_mapped` | text | `permitclassmapped` | Mapped permit class (e.g., Residential) |
| `status` | text | `statuscurrent` | Current permit status |
| `description` | text | `description` | Permit description |
| `address` | text | `originaladdress1` | Property street address |
| `city` | text | `originalcity` | City |
| `state` | text | `originalstate` | State |
| `zip_code` | text | `originalzip` | ZIP code |
| `contractor` | text | `contractorcompanyname` | Contractor company |
| `applied_date` | timestamp | `applieddate` | Date permit was applied for |
| `issued_date` | timestamp | `issueddate` | Date permit was issued |
| `expires_date` | timestamp | `expiresdate` | Date permit expires |
| `completed_date` | timestamp | `completeddate` | Date work was completed |
| `est_project_cost` | numeric | `estprojectcost` | Estimated project cost |
| `latitude` | double precision | `latitude` | Latitude coordinate |
| `longitude` | double precision | `longitude` | Longitude coordinate |
| `ingested_at` | timestamp | `ingested_at` | When the record was loaded into raw |

### stg_rental_registration

Extracted from `raw.raw_rental_registration` JSONB records.

| Column | Type | Source Field | Description |
|--------|------|-------------|-------------|
| `row_id` | integer | `id` | Surrogate key from raw table |
| `registration_id` | text | `permitnum` | Registration permit number |
| `property_name` | text | `propertyname` | Name of the registered property |
| `registration_type` | text | `permittypedesc` | Registration type description |
| `status` | text | `statuscurrent` | Current registration status |
| `rental_units` | integer | `rentalhousingunits` | Number of rental units |
| `address` | text | `originaladdress1` | Property street address |
| `city` | text | `originalcity` | City |
| `state` | text | `originalstate` | State |
| `zip_code` | text | `originalzip` | ZIP code |
| `registered_date` | date | `registereddate` | Date property was registered |
| `expires_date` | date | `expiresdate` | Registration expiration date |
| `latitude` | double precision | `latitude` | Latitude coordinate |
| `longitude` | double precision | `longitude` | Longitude coordinate |
| `ingested_at` | timestamp | `ingested_at` | When the record was loaded into raw |

### stg_code_violations

Extracted from `raw.raw_code_violations` JSONB records.

| Column | Type | Source Field | Description |
|--------|------|-------------|-------------|
| `row_id` | integer | `id` | Surrogate key from raw table |
| `record_number` | text | `recordnum` | Case/record number |
| `record_type` | text | `recordtype` | Type of record |
| `record_type_desc` | text | `recordtypedesc` | Record type description |
| `status` | text | `statuscurrent` | Current case status |
| `description` | text | `description` | Violation description |
| `address` | text | `originaladdress1` | Property street address (may be null) |
| `city` | text | `originalcity` | City |
| `state` | text | `originalstate` | State |
| `zip_code` | text | `originalzip` | ZIP code |
| `open_date` | timestamp | `opendate` | Date the case was opened |
| `last_inspection_date` | timestamp | `lastinspdate` | Date of last inspection |
| `last_inspection_result` | text | `lastinspresult` | Result of last inspection |
| `latitude` | double precision | `latitude` | Latitude coordinate |
| `longitude` | double precision | `longitude` | Longitude coordinate |
| `ingested_at` | timestamp | `ingested_at` | When the record was loaded into raw |

### stg_candidate_apartments

Cleaned from `raw.raw_candidate_apartments` structured table.

| Column | Type | Description |
|--------|------|-------------|
| `apartment_id` | text | Unique candidate identifier (e.g., APT001) |
| `apartment_name` | text | Display name |
| `normalized_address` | text | Upper-cased, trimmed street address for matching |
| `original_address` | text | Original address as entered |
| `city` | text | City |
| `state` | text | State |
| `zip_code` | text | ZIP code |
| `neighborhood` | text | Neighborhood name |
| `listed_rent` | numeric | Representative monthly rent in USD |
| `listed_rent_min` | numeric | Low end of rent range (optional) |
| `listed_rent_max` | numeric | High end of rent range (optional) |
| `rent_basis` | text | How rent was obtained |
| `rent_notes` | text | Context about the rent figure |
| `unit_type` | text | Unit layout (e.g., `1B1B`) |
| `square_feet` | integer | Unit square footage |
| `year_built` | integer | Year building was constructed |
| `parking_available` | text | Parking type or `none` |
| `parking_fee` | numeric | Monthly parking cost |
| `pet_policy` | text | Pet policy summary |
| `online_availability_status` | text | Availability shown on listing website |
| `actual_availability_status` | text | Availability confirmed by leasing office |
| `tour_date` | date | Date toured |
| `management_notes` | text | Professional management observations |
| `personal_notes` | text | Private notes (local file only) |
| `latitude` | double precision | Latitude |
| `longitude` | double precision | Longitude |
| `location_source` | text | How coordinates were obtained |
| `location_confidence` | text | Coordinate accuracy level |
| `data_privacy_level` | text | `public_demo`, `portfolio_safe`, or `private_local` |
| `notes_public_safe` | text | Portfolio-safe notes |
| `consideration_status` | text | `eligible`, `rejected`, or `benchmark` |
| `exclusion_reason` | text | Why excluded from final comparison |
| `include_in_final_comparison` | boolean | Whether to include in comparison |
| `loaded_at` | timestamp | When the record was loaded into raw |

## Intermediate Layer

### int_candidate_apartment_base

| Column | Type | Description |
|--------|------|-------------|
| `apartment_id` | text | Primary key |
| `apartment_name` | text | Display name |
| `normalized_address` | text | Upper-cased, trimmed address for matching |
| `city` | text | City |
| `state` | text | State |
| `zip_code` | text | ZIP code |
| `neighborhood` | text | Neighborhood name |
| `listed_rent` | numeric | Monthly rent |
| `latitude` | double precision | Latitude |
| `longitude` | double precision | Longitude |
| `has_coordinates` | boolean | Whether both lat/lng are present |
| `coordinate_quality_note` | text | Explains whether proximity matching is enabled |
| `jurisdiction` | text | `seattle`, `shoreline`, `other_king_county`, or `unknown` |
| `public_data_coverage_level` | text | e.g., `seattle_city_open_data_available`, `shoreline_partial_manual_review` |
| `public_data_coverage_note` | text | Explanation of data coverage for this jurisdiction |
| `data_coverage_status` | text | `inside_seattle`, `outside_seattle`, or `unknown` (backward-compatible) |
| `consideration_status` | text | `eligible`, `rejected`, or `benchmark` |
| `meets_budget_requirement` | boolean | `true` if listed_rent <= 2500 |
| `meets_unit_type_requirement` | boolean | `true` if unit_type = '1B1B' |
| `meets_hard_filters` | boolean | `true` if both budget and unit type pass |
| `include_in_final_comparison` | boolean | Whether to include in final comparison |

### int_rental_registration_matches

| Column | Type | Description |
|--------|------|-------------|
| `apartment_id` | text | Primary key |
| `rental_registration_match` | boolean | Whether matched to registration data |
| `matched_registration_id` | text | Registration permit number if matched |
| `matched_property_name` | text | Registered property name if matched |
| `match_method` | text | `address_exact` or `no_match` |
| `match_confidence` | text | `high`, `low`, or `not_applicable` |

### int_code_violations_near_candidates

| Column | Type | Description |
|--------|------|-------------|
| `apartment_id` | text | Primary key |
| `complaints_nearby_count` | integer | Total code complaints within 500m |
| `recent_complaints_nearby_count` | integer | Complaints within 500m opened in last 365 days |
| `open_violations_nearby_count` | integer | Complaints within 500m that are not Completed/Closed |
| `latest_complaint_date` | timestamp | Most recent complaint date within 500m |

### int_building_permits_near_candidates

| Column | Type | Description |
|--------|------|-------------|
| `apartment_id` | text | Primary key |
| `permits_nearby_count` | integer | Total building permits within 500m |
| `recent_permits_nearby_count` | integer | Permits within 500m issued in last 365 days |
| `active_permits_nearby_count` | integer | Permits within 500m with active status |
| `latest_permit_date` | timestamp | Most recent permit issued date within 500m |

## Mart Layer

### mart_apartment_due_diligence

| Column | Type | Description |
|--------|------|-------------|
| `apartment_id` | text | Primary key |
| `apartment_name` | text | Display name |
| `normalized_address` | text | Standardized address |
| `city` | text | City |
| `neighborhood` | text | Neighborhood |
| `listed_rent` | numeric | Monthly rent |
| `jurisdiction` | text | `seattle`, `shoreline`, `other_king_county`, or `unknown` |
| `public_data_coverage_level` | text | Data coverage for this jurisdiction |
| `public_data_coverage_note` | text | Coverage explanation |
| `data_coverage_status` | text | `inside_seattle`, `outside_seattle`, or `unknown` |
| `consideration_status` | text | `eligible`, `rejected`, or `benchmark` |
| `include_in_final_comparison` | boolean | Whether to include in final comparison |
| `meets_hard_filters` | boolean | Whether budget and unit type requirements are met |
| `has_coordinates` | boolean | Whether lat/lng are present |
| `coordinate_quality_note` | text | Proximity matching availability explanation |
| `rental_registration_match` | boolean | Whether matched to registration data |
| `matched_registration_id` | text | Registration ID if matched |
| `registration_match_note` | text | Jurisdiction-aware explanation of match result |
| `match_method` | text | How the match was made |
| `match_confidence` | text | Confidence level of the match |
| `complaints_nearby_count` | integer | Code complaints within 500m |
| `recent_complaints_nearby_count` | integer | Recent complaints within 500m |
| `open_violations_nearby_count` | integer | Open violations within 500m |
| `permits_nearby_count` | integer | Building permits within 500m |
| `recent_permits_nearby_count` | integer | Recent permits within 500m |
| `active_permits_nearby_count` | integer | Active permits within 500m |
| `flag_registration_not_found` | boolean | Inside Seattle and no registration match |
| `flag_recent_complaints_nearby` | boolean | Recent complaints found within 500m |
| `flag_active_construction_nearby` | boolean | Active permits found within 500m |
| `flag_partial_public_data_coverage` | boolean | Apartment is outside Seattle city limits (coverage limitation, not risk) |
| `flag_availability_mismatch` | boolean | Online and actual availability status disagree |
| `flag_availability_unclear` | boolean | One or both availability statuses are unclear |
| `flag_parking_unclear` | boolean | Parking information is missing or unspecified |
| `flag_parking_unavailable` | boolean | Parking is explicitly unavailable |
| `flag_outside_budget` | boolean | Listed rent exceeds $2,500 (tracked separately from due-diligence totals) |
| `total_public_record_flags` | integer | Sum of registration, complaint, and permit flags |
| `total_coverage_limitation_flags` | integer | Sum of coverage limitation flags |
| `total_renter_fit_flags` | integer | Sum of availability and parking flags |
| `total_due_diligence_flags` | integer | Sum of public record + renter fit flags (excludes budget and coverage) |
