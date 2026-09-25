-- Solmere: raw -> clean
-- Run with: duckdb -c ".read clean_data.sql" from inside project-2-behavioral-churn/

CREATE OR REPLACE TABLE raw_subscribers AS
    SELECT * FROM read_csv('solmere_churn_raw.csv', header=true, all_varchar=true);

-- Step 1: dedupe. Retried checkouts left repeat rows for the same subscriber; keep one.
CREATE OR REPLACE TABLE deduped AS
    SELECT * FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY subscriber_id ORDER BY subscriber_id) AS rn
        FROM raw_subscribers
    ) WHERE rn = 1;

-- Step 2: clean and cast every column.
CREATE OR REPLACE TABLE clean_subscribers AS
SELECT
    subscriber_id AS SubscriberID,
    region AS Region,
    plan AS Plan,
    TRY_CAST(onboarding_score AS DOUBLE) AS OnboardingScore,

    -- Booleans arrived as Yes/No, 1/0 and True/False depending on the export run
    (lower(trim(negative_ticket_pre_renewal)) IN ('yes', '1', 'true')) AS HasNegativeTicketPreRenewal,
    (lower(trim(cancelled)) IN ('yes', '1', 'true')) AS Cancelled,

    -- Currency: strip $ / USD / commas before casting
    TRY_CAST(
        regexp_replace(regexp_replace(total_spent, '(?i)usd', ''), '[\$,]', '')
        AS DOUBLE
    ) AS TotalSpent,

    -- Missing (no negative ticket in the pre-renewal window) stays NULL, never 0.
    -- A 0 would mean "ticket filed on renewal day itself", which is not the same thing.
    CASE WHEN trim(days_before_renewal_negative_ticket) = ''
         THEN NULL
         ELSE TRY_CAST(days_before_renewal_negative_ticket AS DOUBLE)
    END AS DaysBeforeRenewalLastNegativeTicket,

    -- Free-text cancellation reasons mapped to a fixed set of categories
    CASE
        WHEN lower(trim(cancellation_reason)) LIKE '%expensive%' THEN 'Price'
        WHEN lower(trim(cancellation_reason)) LIKE '%alternative%' THEN 'Switched provider'
        WHEN lower(trim(cancellation_reason)) LIKE '%no longer needed%' THEN 'No longer needed'
        WHEN lower(trim(cancellation_reason)) LIKE '%quality%' THEN 'Product quality'
        WHEN lower(trim(cancellation_reason)) LIKE '%support%' THEN 'Support experience'
        WHEN lower(trim(cancellation_reason)) LIKE '%shipping%' THEN 'Shipping issues'
        WHEN lower(trim(cancellation_reason)) LIKE '%moving%' OR lower(trim(cancellation_reason)) LIKE '%relocat%' THEN 'Relocation'
        WHEN lower(trim(cancellation_reason)) LIKE '%paused%' THEN 'Paused'
        ELSE NULL
    END AS CancellationReason

FROM deduped;

COPY clean_subscribers TO 'solmere_churn_clean.csv' (HEADER, DELIMITER ',');
