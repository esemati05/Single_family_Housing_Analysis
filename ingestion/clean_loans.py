import pandas as pd
from parse_loans import load_origination, load_performance

# Sentinel values Freddie Mac uses to mean "not available" for specific fields
SENTINELS = {
    "credit_score": ["9999"],
    "vantage_score": ["9999"],
    "mi_percent": ["999"],
    "original_cltv": ["999"],
    "original_dti": ["999"],
    "estimated_ltv": ["999"],
}

NUMERIC_COLUMNS_ORIG = [
    "credit_score", "mi_percent", "num_units", "original_cltv", "original_dti",
    "original_upb", "original_ltv", "original_interest_rate", "original_loan_term",
    "num_borrowers", "vantage_score"
]

NUMERIC_COLUMNS_PERF = [
    "current_actual_upb", "loan_age", "remaining_months", "current_interest_rate",
    "current_non_interest_upb", "estimated_ltv", "current_interest_upb"
]


def yyyymm_to_date(series):
    # Converts "202305" -> a real date, the 1st of that month
    return pd.to_datetime(series, format="%Y%m", errors="coerce")


def clean_origination(df):
    df = df.copy()

    # Replace sentinel "not available" codes with real nulls
    for col, sentinel_values in SENTINELS.items():
        if col in df.columns:
            df[col] = df[col].replace(sentinel_values, pd.NA)

    # Convert numeric-looking text columns into actual numbers
    for col in NUMERIC_COLUMNS_ORIG:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Convert YYYYMM date columns into real dates
    df["first_payment_date"] = yyyymm_to_date(df["first_payment_date"])
    df["maturity_date"] = yyyymm_to_date(df["maturity_date"])

    return df


def clean_performance(df):
    df = df.copy()

    for col in NUMERIC_COLUMNS_PERF:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["period"] = yyyymm_to_date(df["period"])

    # Replace estimated_ltv sentinel (999) with null
    df["estimated_ltv"] = df["estimated_ltv"].replace(999, pd.NA)

    return df


if __name__ == "__main__":
    orig = load_origination("data/sample_orig_2023.txt")
    perf = load_performance("data/sample_perf_2023.txt")

    orig_clean = clean_origination(orig)
    perf_clean = clean_performance(perf)

    print("Cleaned origination sample:")
    print(orig_clean[["loan_id", "credit_score", "vantage_score", "first_payment_date", "property_state"]].head())

    print("\nCleaned performance sample:")
    print(perf_clean[["loan_id", "period", "current_actual_upb", "delinquency_status", "estimated_ltv"]].head())

    print(f"\nNull credit scores after cleaning: {orig_clean['credit_score'].isna().sum()}")
    print(f"Null vantage scores after cleaning: {orig_clean['vantage_score'].isna().sum()}")