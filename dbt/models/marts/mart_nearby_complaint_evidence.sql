with candidates as (
    select
        apartment_id,
        apartment_name,
        jurisdiction,
        latitude  as candidate_latitude,
        longitude as candidate_longitude
    from {{ ref('int_candidate_apartment_base') }}
    where latitude is not null and longitude is not null
),

violations as (
    select
        record_number,
        record_type_desc,
        description,
        address,
        status,
        open_date,
        latitude,
        longitude
    from {{ ref('stg_code_violations') }}
    where latitude is not null and longitude is not null
),

nearby as (
    select
        c.apartment_id,
        c.apartment_name,
        c.jurisdiction,
        c.candidate_latitude,
        c.candidate_longitude,
        v.record_number,
        v.address           as complaint_address,
        v.open_date         as complaint_open_date,
        v.status            as complaint_status,
        v.record_type_desc  as complaint_type,
        v.description       as complaint_description,
        round(sqrt(
            power((c.candidate_latitude - v.latitude) * 111000, 2) +
            power((c.candidate_longitude - v.longitude) * 75000, 2)
        )::numeric, 0)     as estimated_distance_meters
    from candidates c
    cross join violations v
    where abs(c.candidate_latitude - v.latitude) < 0.006
      and abs(c.candidate_longitude - v.longitude) < 0.008
)

select * from nearby
where estimated_distance_meters <= 500
