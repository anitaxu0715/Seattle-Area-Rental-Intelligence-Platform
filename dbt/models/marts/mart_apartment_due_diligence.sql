with base as (
    select * from {{ ref('int_candidate_apartment_base') }}
),

registration as (
    select * from {{ ref('int_rental_registration_matches') }}
),

violations as (
    select * from {{ ref('int_code_violations_near_candidates') }}
),

permits as (
    select * from {{ ref('int_building_permits_near_candidates') }}
)

select
    b.apartment_id,
    b.apartment_name,
    b.normalized_address,
    b.city,
    b.state,
    b.zip_code,
    b.neighborhood,
    b.listed_rent,
    b.listed_rent_min,
    b.listed_rent_max,
    b.rent_basis,
    b.rent_notes,
    b.unit_type,
    b.square_feet,
    b.year_built,
    b.parking_available,
    b.parking_fee,
    b.pet_policy,
    b.online_availability_status,
    b.actual_availability_status,
    b.tour_date,
    b.latitude,
    b.longitude,
    b.has_coordinates,
    b.coordinate_quality_note,

    -- jurisdiction and coverage
    b.jurisdiction,
    b.public_data_coverage_level,
    b.public_data_coverage_note,
    b.data_coverage_status,
    b.data_privacy_level,
    b.notes_public_safe,

    -- candidate status and hard filters
    b.consideration_status,
    b.exclusion_reason,
    b.include_in_final_comparison,
    b.meets_budget_requirement,
    b.meets_unit_type_requirement,
    b.meets_hard_filters,

    -- rental registration
    coalesce(r.rental_registration_match, false)        as rental_registration_match,
    r.matched_registration_id,
    r.matched_property_name,
    r.registration_status,
    r.match_method,
    r.match_confidence,

    case
        when coalesce(r.rental_registration_match, false) = true
            then 'Matched to Seattle rental registration data using normalized address'
        when b.jurisdiction = 'shoreline'
            then 'Seattle rental registration data is not applicable because this candidate is in Shoreline. Use Shoreline or King County records for future review'
        when b.jurisdiction != 'seattle'
            then 'Seattle rental registration data is not applicable for ' || trim(b.city) || '. Jurisdiction-specific records may be needed'
        else 'Not matched in current Seattle rental registration sample using normalized-address matching. This is a due-diligence signal, not a legal conclusion'
    end as registration_match_note,

    -- code violations nearby
    coalesce(v.complaints_nearby_count, 0)              as complaints_nearby_count,
    coalesce(v.recent_complaints_nearby_count, 0)       as recent_complaints_nearby_count,
    coalesce(v.open_violations_nearby_count, 0)         as open_violations_nearby_count,
    v.latest_complaint_date,

    -- building permits nearby
    coalesce(p.permits_nearby_count, 0)                 as permits_nearby_count,
    coalesce(p.recent_permits_nearby_count, 0)          as recent_permits_nearby_count,
    coalesce(p.active_permits_nearby_count, 0)          as active_permits_nearby_count,
    p.latest_permit_date,

    -- === PUBLIC RECORD flags (only where Seattle data applies) ===
    case
        when b.jurisdiction = 'seattle'
            and coalesce(r.rental_registration_match, false) = false
        then true else false
    end as flag_registration_not_found,

    case
        when coalesce(v.recent_complaints_nearby_count, 0) > 0
        then true else false
    end as flag_recent_complaints_nearby,

    case
        when coalesce(p.active_permits_nearby_count, 0) > 0
        then true else false
    end as flag_active_construction_nearby,

    -- === COVERAGE LIMITATION flags (not property risk) ===
    case
        when b.jurisdiction != 'seattle'
        then true else false
    end as flag_partial_public_data_coverage,

    -- === RENTER-FIT / information-gap flags ===
    case
        when b.online_availability_status is not null
            and b.actual_availability_status is not null
            and lower(b.online_availability_status) != lower(b.actual_availability_status)
        then true else false
    end as flag_availability_mismatch,

    case
        when lower(coalesce(b.online_availability_status, '')) = 'unclear'
            or lower(coalesce(b.actual_availability_status, '')) = 'unclear'
        then true else false
    end as flag_availability_unclear,

    case
        when b.parking_available is null
            or lower(trim(b.parking_available)) = ''
        then true else false
    end as flag_parking_unclear,

    case
        when lower(trim(coalesce(b.parking_available, ''))) = 'no'
        then true else false
    end as flag_parking_unavailable,

    case
        when b.listed_rent > 2500
        then true else false
    end as flag_outside_budget,

    -- === Grouped flag counts ===

    -- Public record signals (registration, complaints, permits — only where data applies)
    (
        case when b.jurisdiction = 'seattle'
            and coalesce(r.rental_registration_match, false) = false
            then 1 else 0 end
        + case when coalesce(v.recent_complaints_nearby_count, 0) > 0
            then 1 else 0 end
        + case when coalesce(p.active_permits_nearby_count, 0) > 0
            then 1 else 0 end
    ) as total_public_record_flags,

    -- Coverage limitations (not property risk — just data availability)
    (
        case when b.jurisdiction != 'seattle' then 1 else 0 end
    ) as total_coverage_limitation_flags,

    -- Renter-fit / information-gap signals (excludes budget)
    (
        case when b.online_availability_status is not null
            and b.actual_availability_status is not null
            and lower(b.online_availability_status) != lower(b.actual_availability_status)
            then 1 else 0 end
        + case when lower(coalesce(b.online_availability_status, '')) = 'unclear'
            or lower(coalesce(b.actual_availability_status, '')) = 'unclear'
            then 1 else 0 end
        + case when b.parking_available is null
            or lower(trim(b.parking_available)) = ''
            then 1 else 0 end
        + case when lower(trim(coalesce(b.parking_available, ''))) = 'no'
            then 1 else 0 end
    ) as total_renter_fit_flags,

    -- Combined due-diligence (public record + renter fit; excludes budget and coverage)
    (
        case when b.jurisdiction = 'seattle'
            and coalesce(r.rental_registration_match, false) = false
            then 1 else 0 end
        + case when coalesce(v.recent_complaints_nearby_count, 0) > 0
            then 1 else 0 end
        + case when coalesce(p.active_permits_nearby_count, 0) > 0
            then 1 else 0 end
        + case when b.online_availability_status is not null
            and b.actual_availability_status is not null
            and lower(b.online_availability_status) != lower(b.actual_availability_status)
            then 1 else 0 end
        + case when lower(coalesce(b.online_availability_status, '')) = 'unclear'
            or lower(coalesce(b.actual_availability_status, '')) = 'unclear'
            then 1 else 0 end
        + case when b.parking_available is null
            or lower(trim(b.parking_available)) = ''
            then 1 else 0 end
        + case when lower(trim(coalesce(b.parking_available, ''))) = 'no'
            then 1 else 0 end
    ) as total_due_diligence_flags

from base b
left join registration r on b.apartment_id = r.apartment_id
left join violations v on b.apartment_id = v.apartment_id
left join permits p on b.apartment_id = p.apartment_id
