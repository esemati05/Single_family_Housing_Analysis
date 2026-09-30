-- Delinquency rate by property state (states with 100+ loans)
SELECT 
    dl.property_state,
    COUNT(DISTINCT dl.loan_id) AS total_loans,
    COUNT(DISTINCT CASE WHEN lsh.delinquency_status NOT IN ('00', 'XX') THEN lsh.loan_id END) AS ever_delinquent,
    ROUND(
        COUNT(DISTINCT CASE WHEN lsh.delinquency_status NOT IN ('00', 'XX') THEN lsh.loan_id END)::NUMERIC 
        / COUNT(DISTINCT dl.loan_id) * 100, 2
    ) AS delinquency_rate_pct
FROM dim_loan dl
JOIN loan_status_history lsh ON dl.loan_id = lsh.loan_id
GROUP BY dl.property_state
HAVING COUNT(DISTINCT dl.loan_id) >= 100
ORDER BY delinquency_rate_pct DESC;

-- Delinquency rate by credit score band
SELECT 
    CASE 
        WHEN dl.credit_score >= 760 THEN '760+'
        WHEN dl.credit_score >= 700 THEN '700-759'
        WHEN dl.credit_score >= 640 THEN '640-699'
        ELSE 'Below 640'
    END AS credit_score_band,
    COUNT(DISTINCT dl.loan_id) AS total_loans,
    COUNT(DISTINCT CASE WHEN lsh.delinquency_status NOT IN ('00', 'XX') THEN lsh.loan_id END) AS ever_delinquent,
    ROUND(
        COUNT(DISTINCT CASE WHEN lsh.delinquency_status NOT IN ('00', 'XX') THEN lsh.loan_id END)::NUMERIC 
        / COUNT(DISTINCT dl.loan_id) * 100, 2
    ) AS delinquency_rate_pct
FROM dim_loan dl
JOIN loan_status_history lsh ON dl.loan_id = lsh.loan_id
WHERE dl.credit_score IS NOT NULL
GROUP BY credit_score_band
ORDER BY delinquency_rate_pct DESC;