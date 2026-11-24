# Task 2 – Customer Churn Analysis

Finds why subscribers cancel, which behaviours predict it, and what to do about it.

## Run
```bash
pip install -r requirements.txt
python churn_analysis.py                     # uses generated sample data
python churn_analysis.py --input yours.csv   # your CSV needs a 0/1 `churned` column
```

## Approach
1. **Data prep** – remove duplicate customers, fill numeric gaps with the median.
2. **Overall churn** – churn rate and customer count.
3. **Segment analysis** – churn by contract, plan, payment method, tenure, logins, inactivity, support tickets.
4. **Behaviour comparison** – churned vs retained averages + distributions + correlation.
5. **Key drivers** – Random Forest and Logistic Regression (ROC-AUC ~0.75); feature importance ranks the drivers.
6. **Risk scoring** – every customer gets a churn probability and a Low/Medium/High band (`customer_risk_scores.csv`).
7. **Revenue impact** – monthly and annual revenue lost to churn.
8. **Recommendations** – 8 actions, each linked to a finding and a KPI.

## Main findings (sample data)
- Overall churn 10.9%.
- Monthly contracts churn 12.9% vs 7.2% on annual.
- First 6 months churn 18.9% vs 6.2% after 25+ months.
- 30+ days without login churns at 21.2% vs 8.7% for active users.
- Top drivers: tenure, login frequency, satisfaction, days since last login, features used.
- The High-risk band churns at 62% vs 1% for Low, so the model finds who to target.

## Files
- `churn_analysis.py` – full analysis
- `customer_data.csv` – dataset
- `churn_report.md` – findings and recommendations
- `customer_risk_scores.csv` – per-customer risk
- `charts/` – 10 charts
