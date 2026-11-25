# Geospatial Data Analysis – Store Expansion Findings

## 1. Overview

| Metric | Value |
|---|---|
| Orders analysed (after cleaning) | 11,965 (removed 65 bad/duplicate rows) |
| Total sales | $864,963 |
| Existing stores | 10 |
| Sales from customers > 300 km from any store | $316,451 (36.6%) |
| Average distance to nearest store (sales-weighted) | 265 km |

## 2. Existing store catchments

| store_id   | city         | state   |   lat |     lon |   catchment_sales |   catchment_orders |
|:-----------|:-------------|:--------|------:|--------:|------------------:|-------------------:|
| ST01       | New York     | NY      | 40.71 |  -74.01 |            153730 |               2140 |
| ST02       | Los Angeles  | CA      | 34.05 | -118.24 |             92196 |               1306 |
| ST04       | Houston      | TX      | 29.76 |  -95.37 |             66596 |                908 |
| ST03       | Chicago      | IL      | 41.88 |  -87.63 |             65944 |                892 |
| ST06       | Dallas       | TX      | 32.78 |  -96.8  |             33307 |                480 |
| ST08       | Seattle      | WA      | 47.61 | -122.33 |             31498 |                443 |
| ST05       | Philadelphia | PA      | 39.95 |  -75.17 |             29153 |                419 |
| ST07       | San Jose     | CA      | 37.34 | -121.89 |             28296 |                375 |
| ST09       | Boston       | MA      | 42.36 |  -71.06 |             24545 |                311 |
| ST10       | Miami        | FL      | 25.76 |  -80.19 |             23246 |                325 |

## 3. Demand vs presence (1° grid cells, high demand = top 25% of cells, threshold $9,212)

| segment                                |   cells |   sales |   sales_% |
|:---------------------------------------|--------:|--------:|----------:|
| Core: high demand, served              |      16 |  406340 |      47   |
| Low demand, low presence               |      46 |  164186 |      19   |
| Low demand, served                     |      29 |  119555 |      13.8 |
| Opportunity: high demand, low presence |       9 |  136753 |      15.8 |
| Sparse (too few orders)                |     308 |   38129 |       4.4 |

**Top high-demand / low-presence cells**

|   lat |    lon |   orders |   sales |   dist_to_store_km |
|------:|-------:|---------:|--------:|-------------------:|
|  33.7 |  -84.4 |      388 | 26676.1 |              952.7 |
|  29.4 |  -98.5 |      318 | 22809   |              302.2 |
|  33.5 | -112.2 |      285 | 20542.5 |              558.4 |
|  30.3 |  -81.6 |      182 | 13370.7 |              529.1 |
|  39.7 | -104.8 |      170 | 12472.1 |             1049.3 |
|  33.4 | -111.8 |      162 | 12365.6 |              597.9 |
|  39.7 | -105.2 |      139 |  9805.2 |             1076.8 |
|  35.3 |  -80.8 |      119 |  9474.4 |              715.3 |
|  44.8 |  -93.3 |      130 |  9237.9 |              564.2 |

## 4. Recommended new store locations

|   rank | location   |    lat |      lon |   unserved_orders |   addressable_sales |   avg_distance_to_current_store_km |   nearest_current_store_km |   est_annual_sales_won |
|-------:|:-----------|-------:|---------:|------------------:|--------------------:|-----------------------------------:|---------------------------:|-----------------------:|
|      1 | Columbus   | 39.965 |  -83.019 |               590 |               42852 |                                414 |                        442 |                  12856 |
|      2 | Atlanta    | 33.747 |  -84.387 |               497 |               34563 |                                936 |                        948 |                  10369 |
|      3 | Phoenix    | 33.429 | -112.072 |               469 |               34145 |                                573 |                        574 |                  10244 |

*Method: unserved orders (> 300 km from a store) are clustered by sales value; the strongest clusters at least 400 km apart become sites. Estimated sales won assumes a 30% capture rate of addressable demand (an adjustable assumption).*

## 5. Key insights

1. **36.6% of sales ($316,451) come from customers more than 300 km from any store** – demand exists without a physical presence.
2. **9 grid cells** are high demand but low presence; together they hold $136,753 in sales.
3. **Recommended sites** (ranked by addressable demand):
   - **#1 Columbus**: $42,852 addressable sales from 590 orders; nearest current store is 442 km away.
   - **#2 Atlanta**: $34,563 addressable sales from 497 orders; nearest current store is 948 km away.
   - **#3 Phoenix**: $34,145 addressable sales from 469 orders; nearest current store is 574 km away.
   - The most isolated high-demand cell is near (39.7, -105.2), 1077 km from the nearest store.
4. The three sites together address **$111,560** (35% of all currently unserved sales).
5. Estimated incremental sales at 30% capture: **$33,469**.

## 6. Recommendations

1. Open stores in the 3 recommended locations, in rank order (highest addressable demand first).
2. Before signing leases, validate with local rent, competitor presence and demographics (not in this dataset).
3. Start with a pilot or pop-up in the #1 area and measure uplift in sales within its catchment.
4. For the next wave, re-run this analysis after adding the new stores; the next-ranked demand gaps will surface.
5. Track KPIs: sales within catchment, share of sales beyond 300 km, average distance to nearest store.
