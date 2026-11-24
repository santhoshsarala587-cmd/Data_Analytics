# Task 3 – Web Traffic Analytics

Analyses website traffic logs to understand user behaviour: key metrics, drop-off points, conversion funnel and user journeys.

## Run
```bash
pip install -r requirements.txt
python web_traffic_analysis.py                     # uses generated sample logs
python web_traffic_analysis.py --input logs.csv    # your own log CSV
```
Required columns: `session_id, user_id, timestamp, page, time_on_page_sec`. Optional: `source, device`.

## Approach
1. **Clean** – remove duplicate rows, fix timestamps and page names, drop impossible durations (>30 min on one page).
2. **Sessionise** – one row per session: page views, duration, landing page, exit page, full path, bounce flag.
3. **Key metrics** – page views, sessions, unique visitors, pages per session, session duration, bounce rate.
4. **Page performance** – views, average time on page, exit rate, landing bounce rate.
5. **Drop-off points** – exit rate by page (the goal page Contact is excluded from "problem" pages).
6. **Funnel** – Home > Products > Pricing > Contact, with the loss at each step.
7. **User journeys** – top 10 paths, most common page-to-page moves, transition heatmap.
8. **Segments** – source and device comparison (bounce, duration, goal reach).
9. **Time trends** – daily sessions, peak hour, busiest weekday.
10. **Recommendations** – 8 actions, each tied to a finding and a KPI.

## Main findings (sample data)
- 8,000 sessions, 16,270 page views, 2.0 pages per session.
- Bounce rate 44.7%; average session 2m 21s.
- Pricing has the highest non-goal exit rate (62.5%).
- Funnel: 100% Home > 44% Products > 13% Pricing > 2% Contact; the biggest leak is Pricing to Contact.
- Paid Ads bounce most (56.4%); Email converts best (12.7% reach Contact).
- Mobile bounce 47.6% vs 40.4% on desktop.

## Files
- `web_traffic_analysis.py` – full analysis
- `web_traffic_logs.csv` – sample logs
- `web_traffic_report.md` – findings and recommendations
- `charts/` – 9 charts
