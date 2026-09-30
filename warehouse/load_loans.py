import psycopg2
import os
from dotenv import load_dotenv
from ingestion.clean_loans import clean_origination, clean_performance
from ingestion.parse_loans import load_origination, load_performance

import numpy as np
import pandas as pd

def clean_value(val):
    if pd.isna(val):
        return None
    return val


load_dotenv()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cur = conn.cursor()

def load_dim_loan(df):
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO dim_loan (
                loan_id, credit_score, vantage_score, first_payment_date, maturity_date,
                property_state, property_type, postal_code, occupancy_status, loan_purpose,
                channel, amortization_type, original_upb, original_ltv, original_cltv,
                original_dti, original_interest_rate, original_loan_term, num_units,
                num_borrowers, first_time_homebuyer, seller_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (loan_id) DO NOTHING
        """, (
            row["loan_id"], row["credit_score"], row["vantage_score"],
            row["first_payment_date"], row["maturity_date"], row["property_state"],
            row["property_type"], row["postal_code"], row["occupancy_status"],
            row["loan_purpose"], row["channel"], row["amortization_type"],
            row["original_upb"], row["original_ltv"], row["original_cltv"],
            row["original_dti"], row["original_interest_rate"], row["original_loan_term"],
            row["num_units"], row["num_borrowers"], row["first_time_homebuyer"],
            row["seller_name"]
        ))

def load_fact_performance(df):
    for _, row in df.iterrows():
        cur.execute("""
    INSERT INTO fact_loan_performance_monthly (
        loan_id, period, current_actual_upb, delinquency_status, loan_age,
        current_interest_rate, estimated_ltv, zero_balance_code, servicer_name
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (loan_id, period) DO NOTHING
""", (
    clean_value(row["loan_id"]), clean_value(row["period"]),
    clean_value(row["current_actual_upb"]), clean_value(row["delinquency_status"]),
    clean_value(row["loan_age"]), clean_value(row["current_interest_rate"]),
    clean_value(row["estimated_ltv"]), clean_value(row["zero_balance_code"]),
    clean_value(row["servicer_name"])
))

if __name__ == "__main__":
    print("Loading and cleaning data...")
    orig = clean_origination(load_origination("data/sample_orig_2023.txt"))
    perf = clean_performance(load_performance("data/sample_perf_2023.txt"))

    print(f"Inserting {len(orig)} loans into dim_loan...")
    load_dim_loan(orig)
    conn.commit()
    print("Done.")

    print(f"Inserting {len(perf)} rows into fact_loan_performance_monthly...")
    load_fact_performance(perf)
    conn.commit()
    print("Done.")

    cur.close()
    conn.close()