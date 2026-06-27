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

permits as (
    select
        permit_number,
        permit_type,
        description,
        address,
        status,
        issued_date,
        latitude,
        longitude
    from {{ ref('stg_building_permits') }}
    where latitude is not null and longitude is not null
),

nearby as (
    select
        c.apartment_id,
        c.apartment_name,
        c.jurisdiction,
        c.candidate_latitude,
        c.candidate_longitude,
        p.permit_number,
        p.address           as permit_address,
        p.issued_date,
        p.status            as permit_status,
        p.permit_type,
        p.description       as permit_description,
        round(sqrt(
            power((c.candidate_latitude - p.latitude) * 111000, 2) +
            power((c.candidate_longitude - p.longitude) * 75000, 2)
        )::numeric, 0)     as estimated_distance_meters
    from candidates c
    cross join permits p
    where abs(c.candidate_latitude - p.latitude) < 0.006
      and abs(c.candidate_longitude - p.longitude) < 0.008
)

select * from nearby
where estimated_distance_meters <= 500
