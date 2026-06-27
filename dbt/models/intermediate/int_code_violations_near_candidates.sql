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

violations as (
    select
        record_number,
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
        c.normalized_address,
        v.record_number,
        v.status         as violation_status,
        v.open_date,
        sqrt(
            power((c.latitude - v.latitude) * 111000, 2) +
            power((c.longitude - v.longitude) * 75000, 2)
        ) as distance_meters
    from candidates c
    cross join violations v
    where abs(c.latitude - v.latitude) < 0.006
      and abs(c.longitude - v.longitude) < 0.008
),

filtered as (
    select * from nearby
    where distance_meters <= 500
)

select
    apartment_id,
    apartment_name,
    normalized_address,
    count(*)                                                    as complaints_nearby_count,
    count(*) filter (
        where open_date >= current_date - interval '365 days'
    )                                                           as recent_complaints_nearby_count,
    count(*) filter (
        where violation_status not in ('Completed', 'Closed')
    )                                                           as open_violations_nearby_count,
    max(open_date)                                              as latest_complaint_date
from filtered
group by apartment_id, apartment_name, normalized_address
