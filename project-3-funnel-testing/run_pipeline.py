import duckdb
print("🏁 Executing Project 2 Data Pipeline...")
conn = duckdb.connect("solmere_analytics.db")
conn.execute("CREATE OR REPLACE TABLE raw_churn AS SELECT * FROM read_csv_auto('solmere_churn_raw.csv');")
with open("clean_data.sql", "r") as file:
    conn.execute(file.read())
conn.execute("COPY (SELECT * FROM clean_churn_view) TO 'solmere_churn_clean.csv' (HEADER, DELIMITER ',');")
print("✅ Project 2 Complete: 'solmere_churn_clean.csv' generated.")
