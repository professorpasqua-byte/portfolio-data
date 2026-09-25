import duckdb

print("🚀 Booting up analytical pipeline via DuckDB...")

# Initialize standalone storage profile
conn = duckdb.connect("meridian_insights.db")

# clean_data.sql loads meridian_works_raw.csv itself (with all_varchar=true, so
# "Yes"/"No" in Attrition can never be auto-detected as a boolean — that silent
# cast was why the dashboard showed 0.0% attrition before), then writes
# meridian_works_clean.csv at the end.
with open("clean_data.sql", "r") as file:
    sql_script = file.read()

conn.execute(sql_script)

print("✅ Pipeline execution finalized. Pristine table exported as 'meridian_works_clean.csv'.")
