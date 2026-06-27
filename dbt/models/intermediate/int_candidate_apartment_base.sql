with candidates as (
    select * from {{ ref('stg_candidate_apartments') }}
)

select
    apartment_id,
    apartment_name,
    normalized_address,
    original_address,
    city,
    state,
    zip_code,
    neighborhood,
    listed_rent,
    listed_rent_min,
    listed_rent_max,
    rent_basis,
    rent_notes,
    unit_type,
    square_feet,
    year_built,
    parking_available,
    parking_fee,
    pet_policy,
    online_availability_status,
    actual_availability_status,
    tour_date,
    management_notes,
    personal_notes,
    latitude,
    longitude,
    location_source,
    location_confidence,
    data_privacy_level,
    notes_public_safe,

    -- candidate status
    coalesce(consideration_status, 'eligible')          as consideration_status,
    coalesce(exclusion_reason, 'none')                  as exclusion_reason,
    coalesce(include_in_final_comparison, true)          as include_in_final_comparison,

    -- hard-filter evaluation
    case when listed_rent <= 2500 then true else false end
        as meets_budget_requirement,
    case when lower(trim(coalesce(unit_type, ''))) = '1b1b' then true else false end
        as meets_unit_type_requirement,
    case
        when listed_rent <= 2500
            and lower(trim(coalesce(unit_type, ''))) = '1b1b'
        then true else false
    end as meets_hard_filters,

    -- coordinate completeness
    case
        when latitude is not null and longitude is not null
        then true else false
    end as has_coordinates,

    case
        when latitude is not null and longitude is not null
            then 'Coordinates available; proximity matching enabled'
        else 'Missing coordinates; proximity-based complaint and permit matching is not available for this candidate'
    end as coordinate_quality_note,

    -- jurisdiction and data coverage
    case
        when upper(trim(city)) = 'SEATTLE' then 'seattle'
        when upper(trim(city)) = 'SHORELINE' then 'shoreline'
        when city is not null then 'other_king_county'
        else 'unknown'
    end as jurisdiction,

    case
        when upper(trim(city)) = 'SEATTLE' then 'seattle_city_open_data_available'
        when upper(trim(city)) = 'SHORELINE' then 'shoreline_partial_manual_review'
        when city is not null then 'king_county_context_possible'
        else 'unknown_or_not_configured'
    end as public_data_coverage_level,

    case
        when upper(trim(city)) = 'SEATTLE'
            then 'Seattle city open datasets are available for permits, code complaints, and rental registration, subject to sample limits and matching limitations'
        when upper(trim(city)) = 'SHORELINE'
            then 'Seattle city datasets do not apply. Shoreline and King County public records may require separate manual review or future data integration'
        when city is not null
            then 'Seattle city datasets do not apply. County or city-specific public records may be needed for ' || trim(city)
        else 'Jurisdiction-specific public data coverage has not been configured'
    end as public_data_coverage_note,

    -- backward-compatible data_coverage_status
    case
        when upper(trim(city)) = 'SEATTLE' then 'inside_seattle'
        when city is not null then 'outside_seattle'
        else 'unknown'
    end as data_coverage_status,

    loaded_at

from candidates
