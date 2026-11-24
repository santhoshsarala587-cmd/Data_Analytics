# Customer Churn Analysis – Findings

- Customers analysed: **5,000**
- Overall churn rate: **10.9%** (543 churned)

## 1. Churn by segment

**Churn rate by contract type**

| contract   |   churn_rate |   count |
|:-----------|-------------:|--------:|
| Monthly    |         12.9 |    3194 |
| Annual     |          7.2 |    1806 |

**Churn rate by plan**

| plan     |   churn_rate |   count |
|:---------|-------------:|--------:|
| Premium  |         14.3 |    1021 |
| Standard |         12.2 |    1660 |
| Basic    |          8.4 |    2319 |

**Churn rate by payment method**

| payment_method   |   churn_rate |   count |
|:-----------------|-------------:|--------:|
| Wallet           |         13   |     740 |
| UPI              |         11   |    1747 |
| NetBanking       |         10.7 |     806 |
| Card             |          9.8 |    1707 |

**Churn rate by customer tenure**

| tenure_group   |   churn_rate |   count |
|:---------------|-------------:|--------:|
| 0-6 mo         |         18.9 |     636 |
| 7-12 mo        |         16.3 |     650 |
| 13-24 mo       |         13   |    1280 |
| 25+ mo         |          6.2 |    2434 |

**Churn rate by monthly logins**

| login_group   |   churn_rate |   count |
|:--------------|-------------:|--------:|
| 0-4           |         17.2 |     575 |
| 5-10          |         14.7 |    1087 |
| 11-20         |          9.8 |    2317 |
| 20+           |          5.6 |    1021 |

**Churn rate by days since last login**

| inactive_group   |   churn_rate |   count |
|:-----------------|-------------:|--------:|
| 30+ d            |         21.2 |     193 |
| 15-30 d          |         16.9 |     811 |
| 8-14 d           |         10.1 |    1165 |
| 0-7 d            |          8.7 |    2831 |

**Churn rate by support tickets**

| ticket_group   |   churn_rate |   count |
|:---------------|-------------:|--------:|
| 3+             |         15.8 |     576 |
| 1-2            |         11.3 |    2927 |
| 0              |          8   |    1497 |

## 2. Churned vs retained customers (average behaviour)

|                       |   Retained |   Churned |   difference_% |
|:----------------------|-----------:|----------:|---------------:|
| tenure_months         |      24.66 |     17.98 |          -27.1 |
| logins_per_month      |      14.37 |     11.37 |          -20.9 |
| features_used         |       5.12 |      4.21 |          -17.8 |
| avg_session_minutes   |      18.08 |     18.55 |            2.6 |
| support_tickets       |       1.16 |      1.44 |           24.1 |
| days_since_last_login |       8.64 |     12.58 |           45.6 |
| satisfaction_score    |       3.72 |      3.3  |          -11.3 |
| monthly_price         |     362.54 |    408.21 |           12.6 |

## 3. Key churn drivers (predictive model)

- Random Forest ROC-AUC: **0.75**, Logistic Regression ROC-AUC: **0.76**
- Top 8 drivers by importance:

|                       |   importance |
|:----------------------|-------------:|
| tenure_months         |        0.165 |
| logins_per_month      |        0.165 |
| satisfaction_score    |        0.16  |
| days_since_last_login |        0.128 |
| features_used         |        0.095 |
| avg_session_minutes   |        0.094 |
| support_tickets       |        0.05  |
| contract_Monthly      |        0.042 |

```
              precision    recall  f1-score   support

    Retained       0.93      0.86      0.89      1114
     Churned       0.28      0.47      0.35       136

    accuracy                           0.81      1250
   macro avg       0.61      0.66      0.62      1250
weighted avg       0.86      0.81      0.83      1250
```

## 4. Customer risk bands

| risk_band   |   customers |   actual_churn_pct |
|:------------|------------:|-------------------:|
| Low         |        2370 |                1   |
| Medium      |        2016 |                6.8 |
| High        |         614 |               62.4 |

## 5. Revenue impact

- Monthly recurring revenue lost to churn: **Rs. 221,657** (annualised: Rs. 2,659,884)
- Saving just 10% of churners would protect about **Rs. 265,988 per year**.

## 6. Key insights

1. **Contract type**: monthly customers churn at 12.9% vs 7.2% for annual (about 1.8x higher).
2. **Early life is risky**: customers in their first 6 months churn at 18.9% vs 6.2% after 25+ months.
3. **Inactivity is a strong early warning sign**: 21.2% churn when no login for 30+ days vs 8.7% within 7 days.
4. **Low engagement**: churned users log in about 21% less often and use fewer features (see section 2).
5. **Support friction**: customers with 3+ tickets churn much more, so unresolved problems drive cancellations.
6. **Satisfaction**: churned customers rate the product lower, which is an early measurable signal.
7. **Price sensitivity**: Premium churns at 14.3% vs 8.4% for Basic, so higher-paying users need to see more value.

## 7. Retention recommendations

| # | Problem found | Action | KPI to track |
|---|---|---|---|
| 1 | Monthly contracts churn most | Offer 10-20% discount for annual upgrade after month 3 | % on annual plan |
| 2 | First 6 months are risky | Onboarding emails, in-app tour, 30/60/90 day check-ins | 6-month retention |
| 3 | Inactivity precedes cancellation | Auto 'we miss you' campaign at 7 and 14 days of no login | Reactivation rate |
| 4 | Few features used | Feature-adoption nudges, tutorials, webinars | Avg features used |
| 5 | Many support tickets | Faster resolution SLA, proactive outreach after 2nd ticket | Tickets per user, CSAT |
| 6 | Low satisfaction | Short in-app NPS survey; call low scorers within 48h | NPS / satisfaction |
| 7 | High-risk customers identified | Give the 'High' risk band list to the retention team weekly | Save rate |
| 8 | Wallet payers churn more | Promote auto-pay via card/UPI to reduce failed payments | Failed-payment rate |
