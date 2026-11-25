# Task 4 – Geospatial Data Analysis (Store Expansion)

Finds regions with high sales demand but low store presence, and recommends 3 new store locations.

## Run
```bash
pip install -r requirements.txt
python geospatial_analysis.py                                      # generated sample (US) data
python geospatial_analysis.py --orders orders.csv --stores stores.csv
```
- Orders CSV needs: `lat, lon, sales_amount` (optional `city`)
- Stores CSV needs: `store_id, lat, lon` (optional `city`)

Open `interactive_map.html` in a browser (internet needed for the map tiles).

## Approach
1. **Clean** – remove duplicates, missing/invalid coordinates, non-positive sales.
2. **Distance to nearest store** – haversine (great-circle) distance for every order.
3. **Grid demand analysis** – 1° cells (~100 km): sales, orders, sales-weighted centre, distance to nearest store.
4. **Segmentation** – high demand (top 25% of active cells) vs presence (nearest store within/over 300 km):
   Opportunity / Core / Low demand served / Low demand low presence.
5. **Site selection** – cluster unserved orders (KMeans weighted by sales), keep the strongest clusters at least 400 km apart,
   snap each to its strongest city, rank by addressable demand.
6. **Visualise** – 5 static maps/charts + an interactive Leaflet map (heatmap, stores, demand gaps, new sites with 300 km catchments).
7. **Report** – tables, insights and recommendations.

## Main findings (sample data)
- 36.6% of sales come from customers more than 300 km from any store.
- 9 high-demand / low-presence grid cells hold $136,753 in sales.
- Recommended sites: Columbus, Atlanta, Phoenix (about $111,560 addressable sales, 35% of unserved demand).
- Most isolated high-demand cell is near Denver (1,077 km from a store).

## Adjustable assumptions (top of the script)
`FAR_KM`, `GRID_DEG`, `MIN_ORDERS`, `HIGH_DEMAND_PCT`, `N_NEW_STORES`, `MIN_SITE_SEPARATION_KM`, `CAPTURE_RATE`

## Files
- `geospatial_analysis.py` – full analysis
- `sales_data.csv`, `store_locations.csv` – sample data
- `geospatial_report.md` – findings and recommendations
- `recommended_locations.csv`, `grid_cells_analysis.csv` – result tables
- `interactive_map.html` – interactive map
- `charts/` – 5 maps and charts
