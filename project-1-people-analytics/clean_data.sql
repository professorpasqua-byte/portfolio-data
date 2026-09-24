-- PostgreSQL / DuckDB Relational Transformation Pipeline
CREATE OR REPLACE VIEW clean_people_view AS
WITH standardized_telemetry AS (
    SELECT 
        EmployeeID,
        FullName,
        Age,
        Gender,
        MonthlyIncome,
        JobSatisfaction,
        Attrition,
        -- Remap misspelled department groups
        CASE 
            WHEN Department IN ('Engineering', 'Eng.') THEN 'Engineering'
            WHEN Department IN ('Sales', 'Sal3s') THEN 'Sales'
            WHEN Department IN ('Human Resources', 'HR') THEN 'Human Resources'
            ELSE Department 
        END AS Department,
        JobRole,
        -- Order system snapshot records to handle underlying row clutter
        ROW_NUMBER() OVER (
            PARTITION BY EmployeeID 
            ORDER BY exported_at DESC
        ) as row_num
    FROM raw_people
)
SELECT 
    EmployeeID,
    FullName,
    Age,
    Gender,
    Department,
    JobRole,
    MonthlyIncome,
    Attrition,
    JobSatisfaction
FROM standardized_telemetry
WHERE row_num = 1;
