with source as (
    select
        id,
        raw_record,
        ingested_at
    from {{ source('raw', 'raw_rental_registration') }}
)

select
    id                                                      as row_id,
    raw_record ->> 'permitnum'                              as registration_id,
    raw_record ->> 'propertyname'                           as property_name,
    raw_record ->> 'permittypedesc'                         as registration_type,
    raw_record ->> 'statuscurrent'                          as status,
    (raw_record ->> 'rentalhousingunits')::integer          as rental_units,
    raw_record ->> 'originaladdress1'                       as address,
    raw_record ->> 'originalcity'                           as city,
    raw_record ->> 'originalstate'                          as state,
    raw_record ->> 'originalzip'                            as zip_code,
    (raw_record ->> 'registereddate')::date                 as registered_date,
    (raw_record ->> 'expiresdate')::date                    as expires_date,
    (raw_record ->> 'latitude')::double precision           as latitude,
    (raw_record ->> 'longitude')::double precision          as longitude,
    ingested_at
from source
