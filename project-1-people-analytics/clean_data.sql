-- PostgreSQL / DuckDB Relational Transformation Pipeline
CREATE OR REPLACE VIEW clean_people_view AS
SELECT 
    EmployeeID,
    FullName,
    Age,
    Gender,
    CASE 
        WHEN Department IN ('Engineering', 'Eng.') THEN 'Engineering'
        WHEN Department IN ('Sales', 'Sal3s') THEN 'Sales'
        WHEN Department IN ('Human Resources', 'HR') THEN 'Human Resources'
        ELSE Department 
    END AS Department,
    JobRole,
    MonthlyIncome,
    Attrition,
    JobSatisfaction
FROM raw_people;
