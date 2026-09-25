-- Meridian Works: raw -> clean
-- Run with: duckdb -c ".read clean_data.sql" against raw_employees loaded from meridian_works_raw.csv

CREATE OR REPLACE TABLE raw_employees AS
    SELECT * FROM read_csv('meridian_works_raw.csv', header=true, all_varchar=true);

-- Step 1: dedupe. Some emp_ids appear twice (export re-runs); keep one row per emp_id.
CREATE OR REPLACE TABLE deduped AS
    SELECT * FROM (
        SELECT *, ROW_NUMBER() OVER (PARTITION BY emp_id ORDER BY emp_id) AS rn
        FROM raw_employees
    ) WHERE rn = 1;

-- Step 2: clean and cast every column.
CREATE OR REPLACE TABLE clean_employees AS
SELECT
    emp_id AS EmployeeID,

    -- Names: trim stray whitespace, normalize to title case
    trim(regexp_replace(
        array_to_string(
            list_transform(
                str_split(lower(trim(full_name)), ' '),
                x -> upper(substr(x,1,1)) || substr(x,2)
            ), ' '
        ), '\s+', ' '
    )) AS FullName,

    -- Department: fix typos / abbreviations
    CASE
        WHEN lower(trim(department)) IN ('sales', 'sal3s') THEN 'Sales'
        WHEN lower(trim(department)) IN ('eng.', 'engineering') THEN 'Engineering'
        WHEN lower(trim(department)) IN ('hr', 'human resources') THEN 'Human Resources'
        ELSE trim(department)
    END AS Department,

    job_role AS JobRole,

    -- Dates: try each format the raw export used, first match wins
    COALESCE(
        TRY_STRPTIME(hire_date, '%d/%m/%Y'),
        TRY_STRPTIME(hire_date, '%Y-%m-%d'),
        TRY_STRPTIME(hire_date, '%d %b %Y'),
        TRY_STRPTIME(hire_date, '%Y/%m/%d')
    )::DATE AS HireDate,

    CASE WHEN term_date IN ('', 'NULL', 'N/A') THEN NULL ELSE
        COALESCE(
            TRY_STRPTIME(term_date, '%d/%m/%Y'),
            TRY_STRPTIME(term_date, '%Y-%m-%d'),
            TRY_STRPTIME(term_date, '%d %b %Y'),
            TRY_STRPTIME(term_date, '%Y/%m/%d')
        )::DATE
    END AS TermDate,

    -- Income: strip $ and , ; treat -1 (and any non-positive) as missing, not zero
    CASE
        WHEN TRY_CAST(regexp_replace(monthly_income, '[\$,]', '') AS DOUBLE) > 0
            THEN ROUND(TRY_CAST(regexp_replace(monthly_income, '[\$,]', '') AS DOUBLE))
        ELSE NULL
    END AS MonthlyIncome,

    TRY_CAST(age AS INTEGER) AS Age,
    gender AS Gender,
    TRY_CAST(tenure_years AS DOUBLE) AS TenureYears,

    -- Survey fields: map text answers to the 1-4 scale, null anything outside it
    CASE lower(trim(environment_satisfaction))
        WHEN 'low' THEN 1 WHEN 'medium' THEN 2 WHEN 'high' THEN 3 WHEN 'very high' THEN 4
        ELSE (CASE WHEN TRY_CAST(environment_satisfaction AS INTEGER) BETWEEN 1 AND 4
                   THEN TRY_CAST(environment_satisfaction AS INTEGER) ELSE NULL END)
    END AS EnvironmentSatisfaction,

    CASE lower(trim(job_involvement))
        WHEN 'low' THEN 1 WHEN 'medium' THEN 2 WHEN 'high' THEN 3 WHEN 'very high' THEN 4
        ELSE (CASE WHEN TRY_CAST(job_involvement AS INTEGER) BETWEEN 1 AND 4
                   THEN TRY_CAST(job_involvement AS INTEGER) ELSE NULL END)
    END AS JobInvolvement,

    CASE lower(trim(job_satisfaction))
        WHEN 'low' THEN 1 WHEN 'medium' THEN 2 WHEN 'high' THEN 3 WHEN 'very high' THEN 4
        ELSE (CASE WHEN TRY_CAST(job_satisfaction AS INTEGER) BETWEEN 1 AND 4
                   THEN TRY_CAST(job_satisfaction AS INTEGER) ELSE NULL END)
    END AS JobSatisfaction,

    CASE lower(trim(relationship_satisfaction))
        WHEN 'low' THEN 1 WHEN 'medium' THEN 2 WHEN 'high' THEN 3 WHEN 'very high' THEN 4
        ELSE (CASE WHEN TRY_CAST(relationship_satisfaction AS INTEGER) BETWEEN 1 AND 4
                   THEN TRY_CAST(relationship_satisfaction AS INTEGER) ELSE NULL END)
    END AS RelationshipSatisfaction,

    CASE lower(trim(work_life_balance))
        WHEN 'low' THEN 1 WHEN 'medium' THEN 2 WHEN 'high' THEN 3 WHEN 'very high' THEN 4
        ELSE (CASE WHEN TRY_CAST(work_life_balance AS INTEGER) BETWEEN 1 AND 4
                   THEN TRY_CAST(work_life_balance AS INTEGER) ELSE NULL END)
    END AS WorkLifeBalance,

    -- Attrition: derived, kept as text Yes/No (never let this become a boolean on read)
    CASE WHEN term_date IN ('', 'NULL', 'N/A') THEN 'No' ELSE 'Yes' END AS Attrition

FROM deduped;

COPY clean_employees TO 'meridian_works_clean.csv' (HEADER, DELIMITER ',');
