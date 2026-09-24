import duckdb
import pandas as pd

print("🚀 Booting up analytical pipeline via DuckDB...")

# Initialize standalone storage profile
conn = duckdb.connect("meridian_insights.db")

# Load raw dataset directly into database view engine
conn.execute("CREATE OR REPLACE TABLE raw_people AS SELECT * FROM read_csv_auto('meridian_works_raw.csv');")

# Read localized PostgreSQL pipeline queries
with open("clean_data.sql", "r") as file:
    sql_script = file.read()

# Execute data transformations
conn.execute(sql_script)

# Output completely verified pristine dashboard target CSV
conn.execute("COPY (SELECT * FROM clean_people_view) TO 'meridian_works_clean.csv' (HEADER, DELIMITER ',');")

print("✅ Pipeline execution finalized. Pristine table exported as 'meridian_works_clean.csv'.")
