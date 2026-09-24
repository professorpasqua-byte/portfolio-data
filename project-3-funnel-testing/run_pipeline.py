import duckdb
print("🏁 Executing Project 3 Data Pipeline...")
conn = duckdb.connect("tallywell_funnel.db")
conn.execute("CREATE OR REPLACE TABLE raw_funnel AS SELECT * FROM read_csv_auto('tallywell_funnel_raw.csv');")
with open("clean_data.sql", "r") as file:
    conn.execute(file.read())
conn.execute("COPY (SELECT * FROM funnel_experiment_view) TO 'tallywell_funnel_clean.csv' (HEADER, DELIMITER ',');")
print("✅ Project 3 Complete: 'tallywell_funnel_clean.csv' generated.")
