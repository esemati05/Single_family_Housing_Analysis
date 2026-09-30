import psycopg2
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"), host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT")
)

def clean_value(val):
    if pd.isna(val):
        return None
    return val

# Pull the monthly data back out of Postgres, sorted so each loan's months are in order
query = """
    SELECT loan_id, period, delinquency_status
    FROM fact_loan_performance_monthly
    ORDER BY loan_id, period
"""
df = pd.read_sql(query, conn)

history_rows = []

for loan_id, group in df.groupby("loan_id"):
    group = group.reset_index(drop=True)
    current_status = None
    start_date = None

    for i, row in group.iterrows():
        if row["delinquency_status"] != current_status:
            # Status changed (or this is the first row) — close out the previous run
            if current_status is not None:
                history_rows.append({
                    "loan_id": loan_id,
                    "delinquency_status": current_status,
                    "effective_start_date": start_date,
                    "effective_end_date": group.loc[i - 1, "period"],
                    "current_flag": False
                })
            current_status = row["delinquency_status"]
            start_date = row["period"]

    # After the loop, close out the loan's final (still-current) status
    history_rows.append({
        "loan_id": loan_id,
        "delinquency_status": current_status,
        "effective_start_date": start_date,
        "effective_end_date": group.iloc[-1]["period"],
        "current_flag": True
    })

print(f"Derived {len(history_rows)} status history rows from {df['loan_id'].nunique()} loans")

cur = conn.cursor()
for r in history_rows:
    cur.execute("""
        INSERT INTO loan_status_history (loan_id, delinquency_status, effective_start_date, effective_end_date, current_flag)
        VALUES (%s, %s, %s, %s, %s)
    """, (clean_value(r["loan_id"]), clean_value(r["delinquency_status"]),
          clean_value(r["effective_start_date"]), clean_value(r["effective_end_date"]),
          r["current_flag"]))

conn.commit()
cur.close()
conn.close()
print("Done.")