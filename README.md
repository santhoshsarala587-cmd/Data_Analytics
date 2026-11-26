# Data Analytics Internship Projects

**Intern:** Santhosh | **Program:** VirtualWorks – Data Analytics Internship

A portfolio of five end-to-end data analytics projects covering data cleaning, customer analytics, web analytics, geospatial analysis and dashboard development. Every project is reproducible: each folder has its own code, data, results and README.

---

## Projects at a Glance

| # | Project | Focus | Key Tools | Folder |
|---|---------|-------|-----------|--------|
| 1 | Data Cleaning & Structural Validation | Duplicates, missing values, inconsistent formats | Python, Pandas, NumPy | [Task-1](./Task-1) |
| 2 | Customer Churn Analysis | Why customers cancel and how to retain them | Pandas, scikit-learn, Matplotlib | [Task-2](./Task-2) |
| 3 | Web Traffic Analytics | Page views, session duration, drop-offs, user journeys | Pandas, Matplotlib | [Task-3](./Task-3) |
| 4 | Geospatial Data Analysis | Best locations for business expansion | Pandas, scikit-learn, Leaflet | [Task-4](./Task-4) |
| 5 | Interactive Dashboard Development | Executive dashboard with filters and insights | HTML, CSS, JavaScript | [Task-5](./Task-5) |

---

## Task 1 – Data Cleaning & Structural Validation

**Goal:** Turn raw, messy data into a reliable dataset for analysis while preserving data integrity.

**What was done**
- Profiled the data and caught hidden missing values (`N/A`, `null`, `-`).
- Standardised text, 4 mixed date formats, phone numbers and currency values.
- Removed exact and near-duplicate records.
- Treated invalid emails and impossible ages as null instead of keeping wrong data.
- Filled missing values with justified methods (median, group median, `Unknown`).
- Ran 10 automated validation checks; the pipeline stops if any check fails.

**Result:** 220 raw rows became 200 clean rows, with 0 duplicates and 10/10 validation checks passed.

**Files:** `data_cleaning.py`, `raw_data.csv`, `cleaned_data.csv`, `cleaning_report.json`

---

## Task 2 – Customer Churn Analysis

**Goal:** Find the patterns behind subscription cancellations and suggest retention improvements.

**What was done**
- Measured churn by contract, plan, payment method, tenure, logins, inactivity and support tickets.
- Compared the behaviour of churned and retained customers.
- Built Random Forest and Logistic Regression models (ROC-AUC about 0.75) to rank churn drivers.
- Scored every customer as Low, Medium or High risk.
- Estimated the revenue lost to churn and wrote 8 retention recommendations with KPIs.

**Key findings**
- Overall churn is 10.9%.
- Monthly contracts churn at 12.9%, versus 7.2% for annual contracts.
- Customers in their first 6 months churn at 18.9%, versus 6.2% after 25+ months.
- The High-risk band churns at 62%, versus 1% for the Low band.

**Files:** `churn_analysis.py`, `customer_data.csv`, `churn_report.md`, `customer_risk_scores.csv`, `charts/`

---

## Task 3 – Web Traffic Analytics

**Goal:** Understand user behaviour, find drop-off points and map user journeys.

**What was done**
- Cleaned the logs and built session-level metrics.
- Calculated page views, unique visitors, pages per session, session duration and bounce rate.
- Analysed page performance, exit rates and a conversion funnel (Home → Products → Pricing → Contact).
- Mapped the top user journeys and the page-to-page transitions.
- Compared traffic sources and devices, and wrote 8 engagement recommendations.

**Key findings**
- 8,000 sessions generated 16,270 page views, with a 44.7% bounce rate.
- The funnel runs 100% → 44% → 13% → 2%, and the biggest leak is Pricing to Contact.
- Pricing has the highest exit rate among non-goal pages (62.5%).
- Paid Ads bounce most, Email converts best, and mobile bounces more than desktop.

**Files:** `web_traffic_analysis.py`, `web_traffic_logs.csv`, `web_traffic_report.md`, `charts/`

---

## Task 4 – Geospatial Data Analysis

**Goal:** Identify the best areas for business expansion by finding high-demand, low-presence regions.

**What was done**
- Calculated each order's distance to the nearest store using the haversine formula.
- Split the map into grid cells and labelled each one: Opportunity, Core, Low demand served, or Low demand low presence.
- Clustered unserved demand with weighted KMeans and picked 3 well-separated new store sites.
- Produced static maps and an interactive Leaflet map (`interactive_map.html`).

**Key findings**
- 36.6% of sales come from customers more than 300 km from any store.
- Recommended new stores: **Columbus, Atlanta, Phoenix**.
- Together they address about $111,560 in sales, or 35% of all unserved demand.

**Files:** `geospatial_analysis.py`, `sales_data.csv`, `store_locations.csv`, `geospatial_report.md`, `recommended_locations.csv`, `grid_cells_analysis.csv`, `interactive_map.html`, `charts/`

---

## Task 5 – Interactive Dashboard Development

**Goal:** Present trends, performance metrics and actionable insights in one interactive dashboard.

**Live demo:** https://santhoshsarala587-cmd.github.io/Data_Analytics/Task-5/

**Features**
- 5 KPI cards with change versus the previous period.
- Trend chart with hover tooltips, switchable between Revenue, Profit and Orders.
- Regional performance tile map; click a tile to filter the whole dashboard.
- Department views for Sales, Marketing, Finance, HR and Operations, with on/near/off-target status.
- Region × category target-attainment heatmap.
- Auto-generated actionable insights that update with the filters.
- Period, region and category filters, CSV export and a light/dark theme.
- Pure HTML, CSS and JavaScript: no libraries, works offline.

**Files:** `index.html`, `dashboard_template.html`, `build_dashboard.py`, `sales_data.csv`, `department_kpis.csv`

---

## Repository Structure

```
Data_Analytics/
├── Task-1/   Data cleaning pipeline
├── Task-2/   Customer churn analysis
├── Task-3/   Web traffic analytics
├── Task-4/   Geospatial analysis
├── Task-5/   Interactive dashboard
└── README.md
```

## How to Run Any Project

```bash
git clone https://github.com/santhoshsarala587-cmd/Data_Analytics.git
cd Data_Analytics/Task-1          # or Task-2, Task-3, Task-4, Task-5
pip install -r requirements.txt   # if the folder has one
python <script_name>.py
```

For Task 5, open `index.html` in any browser.

## Tech Stack

- **Languages:** Python, JavaScript, HTML, CSS
- **Libraries:** Pandas, NumPy, scikit-learn, Matplotlib
- **Mapping:** Leaflet (interactive map)

## Notes

- The datasets are **synthetic sample data**, generated to demonstrate each workflow. Every script also accepts your own CSV file, as described in each task's README.
- Findings quoted above come from the sample data.

## Author

**Santhosh** – Data Analytics Intern, VirtualWorks
GitHub: [santhoshsarala587-cmd](https://github.com/santhoshsarala587-cmd)
