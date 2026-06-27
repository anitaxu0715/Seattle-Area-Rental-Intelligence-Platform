-- Approximate distance calculation at Seattle's latitude (~47.6 N):
--   1 degree latitude  ~ 111,000 meters
--   1 degree longitude ~ 75,000 meters (111,000 * cos(47.6))
-- Search radius: 500 meters

with candidates as (
    select
        apartment_id,
        apartment_name,
        normalized_address,
        latitude,
        longitude
    from {{ ref('int_candidate_apartment_base') }}
    where latitude is not null and longitude is not null
),

permits as (
    select
        permit_number,
        address,
        status,
        permit_type,
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
        c.normalized_address,
        p.permit_number,
        p.status         as permit_status,
        p.issued_date,
        sqrt(
            power((c.latitude - p.latitude) * 111000, 2) +
            power((c.longitude - p.longitude) * 75000, 2)
        ) as distance_meters
    from candidates c
    cross join permits p
    where abs(c.latitude - p.latitude) < 0.006
      and abs(c.longitude - p.longitude) < 0.008
),

filtered as (
    select * from nearby
    where distance_meters <= 500
)

select
    apartment_id,
    apartment_name,
    normalized_address,
    count(*)                                                    as permits_nearby_count,
    count(*) filter (
        where issued_date >= current_date - interval '365 days'
    )                                                           as recent_permits_nearby_count,
    count(*) filter (
        where permit_status in ('Issued', 'In Review', 'Permit Issued')
    )                                                           as active_permits_nearby_count,
    max(issued_date)                                            as latest_permit_date
from filtered
group by apartment_id, apartment_name, normalized_address
