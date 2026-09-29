import pandas as pd

ORIGINATION_COLUMNS = [
    "credit_score", "first_payment_date", "first_time_homebuyer", "maturity_date",
    "msa", "mi_percent", "num_units", "occupancy_status", "original_cltv",
    "original_dti", "original_upb", "original_ltv", "original_interest_rate",
    "channel", "prepayment_penalty_flag", "amortization_type", "property_state",
    "property_type", "postal_code", "loan_id", "loan_purpose", "original_loan_term",
    "num_borrowers", "seller_name", "super_conforming_flag", "pre_harp_loan_seq_num",
    "special_eligibility_program", "harp_indicator", "property_valuation_method",
    "interest_only_flag", "vantage_score"
]

PERFORMANCE_COLUMNS = [
    "loan_id", "period", "current_actual_upb", "delinquency_status", "loan_age",
    "remaining_months", "defect_settlement_date", "modification_flag",
    "zero_balance_code", "zero_balance_date", "current_interest_rate",
    "current_non_interest_upb", "ddlpi", "mi_recoveries", "net_sales_proceeds",
    "non_mi_recoveries", "total_expenses", "legal_costs", "maintenance_costs",
    "taxes_insurance", "misc_expenses", "actual_loss", "cumulative_mod_costs",
    "interest_rate_step_flag", "payment_deferral_flag", "estimated_ltv",
    "zero_balance_removal_upb", "delinquent_accrued_interest", "disaster_delinquency",
    "borrower_assistance_plan", "current_period_mod_costs", "current_interest_upb",
    "mi_cancellation_flag", "servicer_name", "bankruptcy_cramdown_costs"
]

def load_origination(filepath):
    df = pd.read_csv(filepath, sep="|", header=None, names=ORIGINATION_COLUMNS, dtype=str)
    return df

def load_performance(filepath):
    df = pd.read_csv(filepath, sep="|", header=None, names=PERFORMANCE_COLUMNS, dtype=str)
    return df

if __name__ == "__main__":
    orig = load_origination("data/sample_orig_2023.txt")
    perf = load_performance("data/sample_perf_2023.txt")

    print(f"Origination file: {len(orig)} loans, {len(orig.columns)} columns")
    print(f"Performance file: {len(perf)} rows, {len(perf.columns)} columns")

    print("\nFirst origination row:")
    print(orig.iloc[0])

    print("\nFirst 3 performance rows:")
    print(perf.head(3))