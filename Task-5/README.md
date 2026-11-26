# Task 5 – Interactive Dashboard Development

A single-page executive dashboard (plain HTML + CSS + JavaScript, **no libraries, works offline**).
Open `index.html` in any browser.

## Features
- **5 KPI cards** (revenue, profit, margin, orders, target attainment) with change vs previous period
- **Trends over time** line chart with hover tooltip; switch between Revenue / Profit / Orders; revenue shows the target line
- **Regional performance** tile map coloured by target attainment; click a tile to filter the whole dashboard
- **Department performance** buttons (Sales, Marketing, Finance, HR, Operations) with 3 KPIs each, status (on/near/off target), sparkline and trend
- **Revenue by category** with margin, and a **region x category heatmap** (click a cell to filter)
- **Actionable insights** generated automatically from the current filters, each with a suggested action
- Filters: period, region, category; **Reset**, **Export CSV**, **Light/Dark theme**
- Responsive layout (works on mobile)

## Run / rebuild
```bash
pip install -r requirements.txt
python build_dashboard.py                  # makes sample CSVs + builds index.html
python build_dashboard.py --sales my_sales.csv --kpis my_kpis.csv   # use your own data
```
- sales CSV: `month (YYYY-MM), region, category, revenue, profit, orders, target_revenue`
- kpis CSV: `month, region, department, kpi, value, target`

## Publish a live link (GitHub Pages)
Repo > Settings > Pages > Deploy from branch `main` / root. Your dashboard will be live at
`https://<username>.github.io/<repo>/`.

## Files
- `index.html` – the finished dashboard
- `dashboard_template.html` – source template
- `build_dashboard.py` – data generator and builder
- `sales_data.csv`, `department_kpis.csv` – sample data
