with candidates as (
    select * from {{ ref('int_candidate_apartment_base') }}
),

registrations as (
    select
        registration_id,
        upper(trim(address)) as normalized_address,
        property_name,
        status,
        registered_date,
        expires_date
    from {{ ref('stg_rental_registration') }}
    where address is not null
),

matched as (
    select
        c.apartment_id,
        c.apartment_name,
        c.normalized_address,
        c.jurisdiction,
        c.data_coverage_status,
        r.registration_id       as matched_registration_id,
        r.normalized_address    as matched_registration_address,
        r.property_name         as matched_property_name,
        r.status                as registration_status,
        r.registered_date,
        r.expires_date,
        case
            when r.registration_id is not null then true
            else false
        end as rental_registration_match,
        case
            when r.registration_id is not null then 'address_exact'
            else 'no_match'
        end as match_method,
        case
            when r.registration_id is not null then 'high'
            when c.jurisdiction != 'seattle' then 'not_applicable'
            else 'low'
        end as match_confidence
    from candidates c
    left join registrations r
        on c.normalized_address = r.normalized_address
)

select * from matched
