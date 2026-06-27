with source as (
    select
        id,
        raw_record,
        ingested_at
    from {{ source('raw', 'raw_building_permits') }}
)

select
    id                                                      as row_id,
    raw_record ->> 'permitnum'                              as permit_number,
    raw_record ->> 'permittypedesc'                         as permit_type,
    raw_record ->> 'permitclass'                            as permit_class,
    raw_record ->> 'permitclassmapped'                      as permit_class_mapped,
    raw_record ->> 'statuscurrent'                          as status,
    raw_record ->> 'description'                            as description,
    raw_record ->> 'originaladdress1'                       as address,
    raw_record ->> 'originalcity'                           as city,
    raw_record ->> 'originalstate'                          as state,
    raw_record ->> 'originalzip'                            as zip_code,
    raw_record ->> 'contractorcompanyname'                  as contractor,
    (raw_record ->> 'applieddate')::timestamp               as applied_date,
    (raw_record ->> 'issueddate')::timestamp                as issued_date,
    (raw_record ->> 'expiresdate')::timestamp               as expires_date,
    (raw_record ->> 'completeddate')::timestamp             as completed_date,
    (raw_record ->> 'estprojectcost')::numeric              as est_project_cost,
    (raw_record ->> 'latitude')::double precision           as latitude,
    (raw_record ->> 'longitude')::double precision          as longitude,
    ingested_at
from source
