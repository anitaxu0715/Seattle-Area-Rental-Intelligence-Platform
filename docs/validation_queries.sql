-- Proximity Validation Query
-- Run after adding coordinates and rebuilding dbt models:
--   make load-candidates && make dbt-run
--
-- Notes:
-- * Seattle candidates can use Seattle public complaint/permit proximity signals.
-- * Shoreline candidates may still show 0 for Seattle public records because
--   Shoreline is a different jurisdiction, even with coordinates. Shoreline
--   candidates require future Shoreline/King County integration or manual
--   review for equivalent local signals.
-- * Complaints and permits are based on a 1,000-row ingestion sample ordered
--   by most recent date. Counts are lower bounds, not totals.

SELECT
    apartment_id,
    apartment_name,
    jurisdiction,
    has_coordinates,
    coordinate_quality_note,
    complaints_nearby_count,
    recent_complaints_nearby_count,
    permits_nearby_count,
    active_permits_nearby_count,
    flag_registration_not_found,
    flag_recent_complaints_nearby,
    flag_active_construction_nearby,
    flag_partial_public_data_coverage,
    total_public_record_flags,
    total_coverage_limitation_flags,
    total_renter_fit_flags,
    total_due_diligence_flags
FROM marts.mart_apartment_due_diligence
ORDER BY apartment_id;
