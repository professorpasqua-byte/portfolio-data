import duckdb

print("🚀 Booting up Solmere analytical pipeline via DuckDB...")

conn = duckdb.connect("solmere_insights.db")

# clean_data.sql loads solmere_churn_raw.csv itself (all_varchar=true, so the
# mixed Yes/No/1/0/True bool formats and $/USD currency strings never get
# silently mis-cast on read), then writes solmere_churn_clean.csv at the end.
with open("clean_data.sql", "r") as file:
    sql_script = file.read()

conn.execute(sql_script)

print("✅ Pipeline execution finalized. Pristine table exported as 'solmere_churn_clean.csv'.")
