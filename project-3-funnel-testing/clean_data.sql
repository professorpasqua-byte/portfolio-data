-- Tallywell: raw -> clean
-- Run with: duckdb -c ".read clean_data.sql" from inside project-3-funnel-testing/

CREATE OR REPLACE TABLE raw_sessions AS
    SELECT * FROM read_csv('tallywell_funnel_raw.csv', header=true, all_varchar=true);

-- Step 1: assignment checks. Sessions with a broken or missing variant flag
-- are dropped, not guessed into a bucket.
CREATE OR REPLACE TABLE valid_variant AS
    SELECT * FROM raw_sessions
    WHERE trim(assigned_variant) IN ('Variant A', 'Variant B');

-- Step 2: bot traffic. Sessions completing the full form in under two
-- seconds are excluded as non-human. duration_min is in MINUTES, so the
-- 2-second cutoff is 2/60 minutes here, not 2.0.
CREATE OR REPLACE TABLE no_bots AS
    SELECT * FROM valid_variant
    WHERE TRY_CAST(duration_min AS DOUBLE) >= (2.0 / 60);

-- Step 3: timestamps. Event times arrive in three client time zones; normalize to UTC.
CREATE OR REPLACE TABLE clean_sessions AS
SELECT
    session_id AS SessionID,
    assigned_variant AS AssignedVariant,
    device_type AS DeviceType,
    (lower(trim(completed_signup)) IN ('true', 'yes', '1')) AS CompletedSignup,
    NULLIF(trim(dropoff_field), '') AS DropoffField,
    TRY_CAST(duration_min AS DOUBLE) AS DurationMin,

    -- event_timestamp carries its own UTC offset (e.g. 2026-05-10T12:00:00-05:00);
    -- strptime with %z parses it and DuckDB stores/prints TIMESTAMPTZ as UTC.
    TRY_STRPTIME(event_timestamp, '%Y-%m-%dT%H:%M:%S%z') AS EventTimestampUTC

FROM no_bots;

COPY clean_sessions TO 'tallywell_funnel_clean.csv' (HEADER, DELIMITER ',');
