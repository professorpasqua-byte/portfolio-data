import duckdb

print("🚀 Booting up Tallywell analytical pipeline via DuckDB...")

conn = duckdb.connect("tallywell_insights.db")

# clean_data.sql loads tallywell_funnel_raw.csv itself (all_varchar=true), drops
# sessions with a broken/missing variant flag, drops bot sessions (<2 seconds,
# i.e. duration_min < 2/60 — not < 2.0, which was a real bug caught while
# building this), and normalizes the three client time zones to UTC.
with open("clean_data.sql", "r") as file:
    sql_script = file.read()

conn.execute(sql_script)

print("✅ Pipeline execution finalized. Pristine table exported as 'tallywell_funnel_clean.csv'.")
