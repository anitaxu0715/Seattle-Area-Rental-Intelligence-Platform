with source as (
    select
        id,
        raw_record,
        ingested_at
    from {{ source('raw', 'raw_code_violations') }}
)

select
    id                                                      as row_id,
    raw_record ->> 'recordnum'                              as record_number,
    raw_record ->> 'recordtype'                             as record_type,
    raw_record ->> 'recordtypedesc'                         as record_type_desc,
    raw_record ->> 'statuscurrent'                          as status,
    raw_record ->> 'description'                            as description,
    raw_record ->> 'originaladdress1'                       as address,
    raw_record ->> 'originalcity'                           as city,
    raw_record ->> 'originalstate'                          as state,
    raw_record ->> 'originalzip'                            as zip_code,
    (raw_record ->> 'opendate')::timestamp                  as open_date,
    (raw_record ->> 'lastinspdate')::timestamp              as last_inspection_date,
    raw_record ->> 'lastinspresult'                         as last_inspection_result,
    (raw_record ->> 'latitude')::double precision           as latitude,
    (raw_record ->> 'longitude')::double precision          as longitude,
    ingested_at
from source
