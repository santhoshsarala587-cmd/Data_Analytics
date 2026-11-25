"""
Task 4: Geospatial Data Analysis – where should we open new stores?
-------------------------------------------------------------------
Steps: Load sales + store locations -> Clean -> Distance to nearest store (haversine)
       -> Grid demand analysis -> High-demand / low-presence regions -> Pick 3 new sites
       -> Static maps (matplotlib) + interactive map (Leaflet HTML) -> Report

Usage:
    python geospatial_analysis.py                                   # generated sample (US) data
    python geospatial_analysis.py --orders orders.csv --stores stores.csv
Orders CSV needs : lat, lon, sales_amount   (optional: city)
Stores CSV needs : store_id, lat, lon       (optional: city)
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Ellipse
from sklearn.cluster import KMeans

OUT = Path(__file__).parent
CHARTS = OUT / "charts"
CHARTS.mkdir(exist_ok=True)
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False})

# ---- tunable business assumptions -------------------------------------------------
FAR_KM = 300          # a customer further than this from any store is "not served"
GRID_DEG = 1.0        # size of a map grid cell (about 100 km)
MIN_ORDERS = 10       # a grid cell needs this many orders to count as real demand
HIGH_DEMAND_PCT = 0.75
N_NEW_STORES = 3
MIN_SITE_SEPARATION_KM = 400
CAPTURE_RATE = 0.30   # share of nearby unserved demand a new store is assumed to win
# ------------------------------------------------------------------------------------

# approximate contiguous-US outline (lon, lat) – only for map context
US_OUTLINE = [(-124.7, 48.4), (-124.1, 46.2), (-124.1, 43.0), (-124.4, 40.4), (-123.8, 39.0), (-122.5, 37.5),
              (-121.9, 36.6), (-120.6, 34.5), (-118.5, 34.0), (-117.1, 32.5), (-114.7, 32.7), (-111.0, 31.3),
              (-108.2, 31.3), (-106.5, 31.8), (-104.5, 29.6), (-103.1, 29.0), (-101.4, 29.8), (-99.5, 27.5),
              (-97.4, 25.9), (-97.3, 27.8), (-94.7, 29.4), (-92.0, 29.6), (-90.0, 29.1), (-89.2, 30.3),
              (-87.5, 30.3), (-85.3, 29.7), (-84.0, 30.1), (-82.8, 28.0), (-81.8, 26.1), (-80.4, 25.2),
              (-80.1, 26.8), (-80.6, 28.5), (-81.4, 30.7), (-80.9, 32.0), (-79.0, 33.7), (-76.0, 35.3),
              (-75.5, 37.0), (-75.1, 38.4), (-74.0, 39.7), (-74.0, 40.5), (-72.0, 41.0), (-70.0, 41.7),
              (-70.6, 43.0), (-68.0, 44.4), (-67.0, 44.8), (-67.8, 47.1), (-69.2, 47.4), (-70.8, 45.3),
              (-74.7, 45.0), (-76.5, 44.0), (-79.0, 43.3), (-83.0, 42.3), (-82.4, 43.0), (-82.5, 45.3),
              (-84.4, 46.5), (-89.6, 48.0), (-94.6, 48.7), (-95.2, 49.0), (-123.3, 49.0), (-123.0, 48.3)]

# (city, state, lat, lon, demand weight)
CITIES = [
    ("New York", "NY", 40.71, -74.01, 8.3), ("Los Angeles", "CA", 34.05, -118.24, 3.9),
    ("Chicago", "IL", 41.88, -87.63, 2.7), ("Houston", "TX", 29.76, -95.37, 2.3),
    ("Phoenix", "AZ", 33.45, -112.07, 2.1), ("Philadelphia", "PA", 39.95, -75.17, 1.6),
    ("San Antonio", "TX", 29.42, -98.49, 1.5), ("San Diego", "CA", 32.72, -117.16, 1.4),
    ("Dallas", "TX", 32.78, -96.80, 1.6), ("San Jose", "CA", 37.34, -121.89, 1.0),
    ("Austin", "TX", 30.27, -97.74, 1.0), ("Jacksonville", "FL", 30.33, -81.66, 0.95),
    ("Columbus", "OH", 39.96, -83.00, 0.9), ("Charlotte", "NC", 35.23, -80.84, 0.9),
    ("Indianapolis", "IN", 39.77, -86.16, 0.9), ("Seattle", "WA", 47.61, -122.33, 1.1),
    ("Denver", "CO", 39.74, -104.99, 1.6), ("Boston", "MA", 42.36, -71.06, 1.2),
    ("Nashville", "TN", 36.16, -86.78, 0.8), ("Atlanta", "GA", 33.75, -84.39, 2.2),
    ("Miami", "FL", 25.76, -80.19, 1.1), ("Minneapolis", "MN", 44.98, -93.27, 1.3),
    ("Detroit", "MI", 42.33, -83.05, 0.9), ("Las Vegas", "NV", 36.17, -115.14, 1.0),
    ("Portland", "OR", 45.52, -122.68, 0.7), ("Salt Lake City", "UT", 40.76, -111.89, 0.7),
    ("Kansas City", "MO", 39.10, -94.58, 0.6), ("St. Louis", "MO", 38.63, -90.20, 0.5),
    ("Tampa", "FL", 27.95, -82.46, 0.6), ("Orlando", "FL", 28.54, -81.38, 0.5),
    ("Pittsburgh", "PA", 40.44, -80.00, 0.5), ("New Orleans", "LA", 29.95, -90.07, 0.4),
    ("Oklahoma City", "OK", 35.47, -97.52, 0.6), ("Raleigh", "NC", 35.78, -78.64, 0.5),
    ("Sacramento", "CA", 38.58, -121.49, 0.5), ("Cincinnati", "OH", 39.10, -84.51, 0.4),
]
STORE_CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Philadelphia", "Boston",
                "Seattle", "San Jose", "Dallas", "Miami"]


# ------------------------------------------------------------------ helpers
def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance in km (works with numpy broadcasting)."""
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(a))


def nearest_store(lat, lon, stores):
    """Distance (km) and index of the nearest store for every point."""
    d = haversine_km(np.asarray(lat)[:, None], np.asarray(lon)[:, None],
                     stores["lat"].values[None, :], stores["lon"].values[None, :])
    return d.min(axis=1), d.argmin(axis=1)


# ------------------------------------------------------------------ 1. DATA
def generate_data(n_orders=12000, seed=21):
    rng = np.random.default_rng(seed)
    cdf = pd.DataFrame(CITIES, columns=["city", "state", "lat", "lon", "w"])
    stores = cdf[cdf["city"].isin(STORE_CITIES)].reset_index(drop=True)[["city", "state", "lat", "lon"]].copy()
    stores.insert(0, "store_id", [f"ST{i + 1:02d}" for i in range(len(stores))])

    w = cdf["w"] * np.where(cdf["city"].isin(STORE_CITIES), 1.25, 1.0)   # store cities sell a bit more
    idx = rng.choice(len(cdf), n_orders, p=w / w.sum())
    c = cdf.iloc[idx].reset_index(drop=True)
    orders = pd.DataFrame({
        "order_id": [f"O{100000 + i}" for i in range(n_orders)],
        "city": c["city"], "state": c["state"],
        "lat": c["lat"] + rng.normal(0, .22, n_orders),
        "lon": c["lon"] + rng.normal(0, .26, n_orders),
        "sales_amount": rng.lognormal(np.log(62), .55, n_orders).round(2)})
    # a few scattered rural orders + dirty rows
    k = int(n_orders * .03)
    orders.loc[rng.choice(n_orders, k, replace=False), ["lat", "lon"]] = np.column_stack(
        [rng.uniform(27, 48, k), rng.uniform(-120, -75, k)])
    orders.loc[rng.choice(n_orders, 25, replace=False), "lat"] = np.nan
    orders.loc[rng.choice(n_orders, 10, replace=False), "lon"] = 999
    orders = pd.concat([orders, orders.sample(30, random_state=1)], ignore_index=True)
    return orders, stores


# ------------------------------------------------------------------ 2. CLEAN
def clean_orders(o):
    n0 = len(o)
    o = o.drop_duplicates().copy()
    for c in ["lat", "lon", "sales_amount"]:
        o[c] = pd.to_numeric(o[c], errors="coerce")
    o = o.dropna(subset=["lat", "lon", "sales_amount"])
    o = o[o["lat"].between(-90, 90) & o["lon"].between(-180, 180) & (o["sales_amount"] > 0)]
    print(f"Cleaning orders: {n0:,} -> {len(o):,} rows")
    return o.reset_index(drop=True), n0 - len(o)


# ------------------------------------------------------------------ 3. GRID
def grid_analysis(o, stores):
    o = o.copy()
    o["cell_lat"] = np.floor(o["lat"] / GRID_DEG) * GRID_DEG + GRID_DEG / 2
    o["cell_lon"] = np.floor(o["lon"] / GRID_DEG) * GRID_DEG + GRID_DEG / 2
    o["w_lat"] = o["lat"] * o["sales_amount"]
    o["w_lon"] = o["lon"] * o["sales_amount"]
    g = o.groupby(["cell_lat", "cell_lon"]).agg(orders=("order_id", "size"), sales=("sales_amount", "sum"),
                                                w_lat=("w_lat", "sum"), w_lon=("w_lon", "sum")).reset_index()
    g["lat"], g["lon"] = g["w_lat"] / g["sales"], g["w_lon"] / g["sales"]       # sales-weighted centre
    g["dist_to_store_km"], _ = nearest_store(g["lat"], g["lon"], stores)
    active = g["orders"] >= MIN_ORDERS
    thr = g.loc[active, "sales"].quantile(HIGH_DEMAND_PCT)
    high = active & (g["sales"] >= thr)
    far = g["dist_to_store_km"] > FAR_KM

    g["segment"] = np.select(
        [high & far, high & ~far, active & far, active & ~far],
        ["Opportunity: high demand, low presence", "Core: high demand, served",
         "Low demand, low presence", "Low demand, served"], default="Sparse (too few orders)")
    return g.drop(columns=["w_lat", "w_lon"]), thr


# ------------------------------------------------------------------ 4. SITES
def pick_sites(under, stores):
    """Cluster unserved demand, then pick the strongest well-separated clusters."""
    xy = np.column_stack([under["lon"] * np.cos(np.radians(38)) * 111.32, under["lat"] * 110.57])
    k = min(14, max(N_NEW_STORES, under["city"].nunique() if "city" in under else 10))
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(xy, sample_weight=under["sales_amount"])
    u = under.assign(cluster=km.labels_)
    cl = u.groupby("cluster")["sales_amount"].sum().sort_values(ascending=False)

    chosen = []
    for cid in cl.index:
        m = u[u["cluster"] == cid]
        if "city" in m and m["city"].notna().any():             # snap to the strongest city in the cluster
            top_city = m.groupby("city")["sales_amount"].sum().idxmax()
            m = m[m["city"] == top_city]
            name = top_city
        else:
            name = None
        lat = np.average(m["lat"], weights=m["sales_amount"])
        lon = np.average(m["lon"], weights=m["sales_amount"])
        if all(haversine_km(lat, lon, s["lat"], s["lon"]) >= MIN_SITE_SEPARATION_KM for s in chosen):
            chosen.append({"name": name or f"({lat:.2f}, {lon:.2f})", "lat": lat, "lon": lon})
        if len(chosen) == N_NEW_STORES:
            break
    sites = pd.DataFrame(chosen)

    # assign every unserved order to its nearest new site -> addressable demand
    d = haversine_km(under["lat"].values[:, None], under["lon"].values[:, None],
                     sites["lat"].values[None, :], sites["lon"].values[None, :])
    near, which = d.min(axis=1), d.argmin(axis=1)
    inside = near <= FAR_KM
    rows = []
    for i, s in sites.iterrows():
        mask = inside & (which == i)
        rows.append({"rank": i + 1, "location": s["name"], "lat": round(s["lat"], 3), "lon": round(s["lon"], 3),
                     "unserved_orders": int(mask.sum()),
                     "addressable_sales": round(under.loc[mask, "sales_amount"].sum(), 0),
                     "avg_distance_to_current_store_km": round(under.loc[mask, "dist_km"].mean(), 0),
                     "nearest_current_store_km": round(float(nearest_store([s["lat"]], [s["lon"]], stores)[0][0]), 0)})
    out = pd.DataFrame(rows).sort_values("addressable_sales", ascending=False).reset_index(drop=True)
    out["rank"] = out.index + 1                      # rank by addressable demand, highest first
    out["est_annual_sales_won"] = (out["addressable_sales"] * CAPTURE_RATE).round(0)
    return out


# ------------------------------------------------------------------ 5. CHARTS
def base_map(ax, title):
    ax.add_patch(plt.Polygon(US_OUTLINE, closed=True, fill=True, fc="#f4f1ea", ec="#999", lw=.8, zorder=0))
    ax.set(xlim=(-127, -65), ylim=(23.5, 50.5), title=title, xlabel="Longitude", ylabel="Latitude")
    ax.set_aspect(1 / np.cos(np.radians(38)))


def make_charts(o, stores, grid, sites, under_mask):
    # 1. sales heatmap
    fig, ax = plt.subplots(figsize=(11, 6.5))
    base_map(ax, "Where do we sell? Sales density (log scale) and current stores")
    hb = ax.hexbin(o["lon"], o["lat"], C=o["sales_amount"], reduce_C_function=np.sum, gridsize=48,
                   cmap="YlOrRd", bins="log", mincnt=1, extent=(-127, -65, 23.5, 50.5), zorder=1, alpha=.9)
    ax.scatter(stores["lon"], stores["lat"], marker="*", s=230, c="#1d3557", ec="white", lw=.8, zorder=3, label="Existing store")
    plt.colorbar(hb, ax=ax, shrink=.7, label="log10(total sales $)")
    ax.legend(loc="lower left", frameon=False)
    save(fig, "01_sales_heatmap.png")

    # 2. demand vs presence segments
    colors = {"Opportunity: high demand, low presence": "#d62828", "Core: high demand, served": "#2a9d8f",
              "Low demand, low presence": "#adb5bd", "Low demand, served": "#8ecae6", "Sparse (too few orders)": "#e9ecef"}
    fig, ax = plt.subplots(figsize=(11, 6.5))
    base_map(ax, "High demand vs low presence (each bubble = 1° grid cell)")
    for seg, col in colors.items():
        s = grid[grid["segment"] == seg]
        ax.scatter(s["lon"], s["lat"], s=s["sales"] / grid["sales"].max() * 900 + 10, c=col, alpha=.8,
                   ec="white", lw=.5, label=f"{seg} ({len(s)})", zorder=2)
    ax.scatter(stores["lon"], stores["lat"], marker="*", s=230, c="#1d3557", ec="white", lw=.8, zorder=4, label="Existing store")
    ax.legend(loc="lower left", fontsize=8, frameon=True)
    save(fig, "02_demand_vs_presence.png")

    # 3. recommended sites with 300 km catchments
    fig, ax = plt.subplots(figsize=(11, 6.5))
    base_map(ax, f"Recommended new stores and their {FAR_KM} km catchments")
    ax.scatter(o.loc[~under_mask, "lon"], o.loc[~under_mask, "lat"], s=3, c="#8ecae6", alpha=.4, label="Served orders", zorder=1)
    ax.scatter(o.loc[under_mask, "lon"], o.loc[under_mask, "lat"], s=4, c="#e76f51", alpha=.5, label=f"Orders > {FAR_KM} km from a store", zorder=2)
    ax.scatter(stores["lon"], stores["lat"], marker="*", s=230, c="#1d3557", ec="white", lw=.8, zorder=4, label="Existing store")
    for _, r in sites.iterrows():
        ax.add_patch(Ellipse((r["lon"], r["lat"]), 2 * FAR_KM / (111.32 * np.cos(np.radians(r["lat"]))),
                             2 * FAR_KM / 110.57, fill=False, ec="#d62828", ls="--", lw=1.4, zorder=3))
        ax.scatter(r["lon"], r["lat"], marker="*", s=420, c="#d62828", ec="black", lw=1, zorder=5)
        ax.annotate(f"#{int(r['rank'])} {r['location']}", (r["lon"], r["lat"]), xytext=(8, 8),
                    textcoords="offset points", fontsize=10, fontweight="bold", zorder=6)
    ax.legend(loc="lower left", fontsize=8, frameon=True)
    save(fig, "03_recommended_sites.png")

    # 4. sales by distance band
    bands = pd.cut(o["dist_km"], [-1, 50, 150, FAR_KM, 600, 1e5],
                   labels=["0-50 km", "50-150 km", f"150-{FAR_KM} km", f"{FAR_KM}-600 km", "600+ km"])
    share = o.groupby(bands, observed=True)["sales_amount"].sum() / o["sales_amount"].sum() * 100
    fig, ax = plt.subplots(figsize=(7, 4))
    b = ax.bar(share.index.astype(str), share.values, color=["#2a9d8f", "#2a9d8f", "#f4a261", "#e76f51", "#e76f51"][:len(share)])
    ax.bar_label(b, fmt="%.1f%%", padding=2)
    ax.set(title="Share of sales by distance to nearest store", ylabel="% of sales")
    save(fig, "04_sales_by_distance.png")

    # 5. potential per site
    fig, ax = plt.subplots(figsize=(6.5, 4))
    labels = [f"#{int(r)} {l}" for r, l in zip(sites["rank"], sites["location"])]
    b = ax.bar(labels, sites["addressable_sales"], color="#264653", label="Addressable sales")
    ax.bar(labels, sites["est_annual_sales_won"], color="#e76f51", label=f"Est. won ({CAPTURE_RATE:.0%} capture)")
    ax.set(title="Demand each new store can address ($)")
    ax.legend(frameon=False)
    save(fig, "05_site_potential.png")


def save(fig, name):
    plt.tight_layout()
    fig.savefig(CHARTS / name)
    plt.close(fig)


# ------------------------------------------------------------------ 6. INTERACTIVE MAP
HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Store Expansion Map</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
html,body,#map{height:100%;margin:0}
.box{background:#fff;padding:8px 12px;border-radius:6px;font:13px/1.5 sans-serif;box-shadow:0 0 6px rgba(0,0,0,.3)}
.dot{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:6px}
.pin{background:#d62828;color:#fff;border:2px solid #fff;border-radius:50%;width:28px;height:28px;line-height:24px;text-align:center;font:bold 13px sans-serif;box-shadow:0 0 4px #000}
</style></head>
<body><div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
<script>
const D = __DATA__;
const map = L.map('map').setView(D.center, 4);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 18, attribution: '&copy; OpenStreetMap contributors'}).addTo(map);

const heat = L.heatLayer(D.heat, {radius: 22, blur: 18, maxZoom: 7}).addTo(map);

const stores = L.layerGroup(D.stores.map(s =>
  L.circleMarker([s.lat, s.lon], {radius: 8, color: '#fff', weight: 2, fillColor: '#1d3557', fillOpacity: 1})
   .bindPopup('<b>' + s.id + '</b><br>' + s.city + '<br>Catchment sales: $' + s.sales.toLocaleString())
)).addTo(map);

const gaps = L.layerGroup(D.gaps.map(g =>
  L.circleMarker([g.lat, g.lon], {radius: Math.max(5, g.r), color: '#d62828', weight: 1, fillColor: '#d62828', fillOpacity: .35})
   .bindPopup('<b>High demand, low presence</b><br>Sales: $' + g.sales.toLocaleString() + '<br>Orders: ' + g.orders + '<br>Nearest store: ' + g.dist + ' km')
)).addTo(map);

const sites = L.layerGroup();
D.sites.forEach(s => {
  L.marker([s.lat, s.lon], {icon: L.divIcon({className: '', html: '<div class="pin">' + s.rank + '</div>', iconSize: [28, 28]})})
   .bindPopup('<b>Recommended #' + s.rank + ': ' + s.name + '</b><br>Addressable sales: $' + s.addr.toLocaleString() +
              '<br>Est. sales won: $' + s.won.toLocaleString() + '<br>Nearest current store: ' + s.near + ' km').addTo(sites);
  L.circle([s.lat, s.lon], {radius: D.far * 1000, color: '#d62828', weight: 2, dashArray: '6 6', fill: false}).addTo(sites);
});
sites.addTo(map);

L.control.layers(null, {'Sales heatmap': heat, 'Existing stores': stores, 'High-demand / low-presence areas': gaps, 'Recommended new stores': sites}, {collapsed: false}).addTo(map);

const legend = L.control({position: 'bottomleft'});
legend.onAdd = () => { const d = L.DomUtil.create('div', 'box');
  d.innerHTML = '<b>Store expansion analysis</b><br><span class="dot" style="background:#1d3557"></span>Existing store<br>' +
                '<span class="dot" style="background:#d62828;opacity:.5"></span>Demand gap (no store within ' + D.far + ' km)<br>' +
                '<span class="dot" style="background:#d62828"></span>Recommended new store';
  return d; };
legend.addTo(map);
map.fitBounds(D.bounds);
</script></body></html>
"""


def write_interactive_map(o, stores, grid, sites, store_sales):
    gh = o.assign(la=(o["lat"] / .25).round() * .25, lo=(o["lon"] / .25).round() * .25) \
          .groupby(["la", "lo"])["sales_amount"].sum().reset_index()
    gh["i"] = (gh["sales_amount"] / gh["sales_amount"].quantile(.98)).clip(upper=1).round(3)
    gaps = grid[grid["segment"].str.startswith("Opportunity")]
    payload = {
        "center": [float(o["lat"].median()), float(o["lon"].median())],
        "bounds": [[float(o["lat"].quantile(.01)), float(o["lon"].quantile(.01))],
                   [float(o["lat"].quantile(.99)), float(o["lon"].quantile(.99))]],
        "far": FAR_KM,
        "heat": gh[["la", "lo", "i"]].values.round(3).tolist(),
        "stores": [{"id": r.store_id, "city": str(getattr(r, "city", "")), "lat": r.lat, "lon": r.lon,
                    "sales": int(store_sales.get(r.store_id, 0))} for r in stores.itertuples()],
        "gaps": [{"lat": round(r.lat, 3), "lon": round(r.lon, 3), "sales": int(r.sales), "orders": int(r.orders),
                  "dist": int(r.dist_to_store_km), "r": float(8 + r.sales / grid["sales"].max() * 22)} for r in gaps.itertuples()],
        "sites": [{"rank": int(r.rank), "name": r.location, "lat": r.lat, "lon": r.lon, "addr": int(r.addressable_sales),
                   "won": int(r.est_annual_sales_won), "near": int(r.nearest_current_store_km)} for r in sites.itertuples()],
    }
    (OUT / "interactive_map.html").write_text(HTML.replace("__DATA__", json.dumps(payload)), encoding="utf-8")


# ------------------------------------------------------------------ MAIN
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--orders")
    ap.add_argument("--stores")
    args = ap.parse_args()

    if args.orders and args.stores:
        orders, stores = pd.read_csv(args.orders), pd.read_csv(args.stores)
        if "order_id" not in orders:
            orders.insert(0, "order_id", range(len(orders)))
    else:
        orders, stores = generate_data()
        orders.to_csv(OUT / "sales_data.csv", index=False)
        stores.to_csv(OUT / "store_locations.csv", index=False)
        print("Generated sample data -> sales_data.csv, store_locations.csv")

    o, removed = clean_orders(orders)
    o["dist_km"], nearest_idx = nearest_store(o["lat"], o["lon"], stores)
    o["nearest_store"] = stores["store_id"].values[nearest_idx]
    under_mask = o["dist_km"] > FAR_KM
    under = o[under_mask].copy()

    grid, thr = grid_analysis(o, stores)
    sites = pick_sites(under, stores)
    store_sales = o[~under_mask].groupby("nearest_store")["sales_amount"].sum()
    store_tbl = stores.assign(catchment_sales=stores["store_id"].map(store_sales).fillna(0).round(0),
                              catchment_orders=stores["store_id"].map(o[~under_mask]["nearest_store"].value_counts()).fillna(0).astype(int))

    make_charts(o, stores, grid, sites, under_mask)
    write_interactive_map(o, stores, grid, sites, store_sales)
    grid.sort_values("sales", ascending=False).round(2).to_csv(OUT / "grid_cells_analysis.csv", index=False)
    sites.to_csv(OUT / "recommended_locations.csv", index=False)

    # ---- report
    total, total_u = o["sales_amount"].sum(), under["sales_amount"].sum()
    opp = grid[grid["segment"].str.startswith("Opportunity")].sort_values("sales", ascending=False)
    seg = grid.groupby("segment").agg(cells=("sales", "size"), sales=("sales", "sum")).round(0)
    seg["sales_%"] = (seg["sales"] / total * 100).round(1)
    L = []
    log = L.append
    log("# Geospatial Data Analysis – Store Expansion Findings\n")
    log("## 1. Overview\n")
    log("| Metric | Value |\n|---|---|")
    log(f"| Orders analysed (after cleaning) | {len(o):,} (removed {removed} bad/duplicate rows) |")
    log(f"| Total sales | ${total:,.0f} |")
    log(f"| Existing stores | {len(stores)} |")
    log(f"| Sales from customers > {FAR_KM} km from any store | ${total_u:,.0f} ({total_u / total * 100:.1f}%) |")
    log(f"| Average distance to nearest store (sales-weighted) | {np.average(o['dist_km'], weights=o['sales_amount']):.0f} km |\n")
    log("## 2. Existing store catchments\n")
    log(store_tbl.sort_values("catchment_sales", ascending=False).to_markdown(index=False) + "\n")
    log(f"## 3. Demand vs presence (1° grid cells, high demand = top {int((1 - HIGH_DEMAND_PCT) * 100)}% of cells, "
        f"threshold ${thr:,.0f})\n")
    log(seg.to_markdown() + "\n")
    log("**Top high-demand / low-presence cells**\n")
    cols = ["lat", "lon", "orders", "sales", "dist_to_store_km"]
    log(opp[cols].head(10).round(1).to_markdown(index=False) + "\n")
    log("## 4. Recommended new store locations\n")
    log(sites.to_markdown(index=False) + "\n")
    log(f"*Method: unserved orders (> {FAR_KM} km from a store) are clustered by sales value; the strongest clusters at least "
        f"{MIN_SITE_SEPARATION_KM} km apart become sites. Estimated sales won assumes a {CAPTURE_RATE:.0%} capture rate of addressable demand "
        f"(an adjustable assumption).*\n")
    log("## 5. Key insights\n")
    log(f"1. **{total_u / total * 100:.1f}% of sales (${total_u:,.0f}) come from customers more than {FAR_KM} km from any store** – demand exists without a physical presence.")
    log(f"2. **{len(opp)} grid cells** are high demand but low presence; together they hold ${opp['sales'].sum():,.0f} in sales.")
    log("3. **Recommended sites** (ranked by addressable demand):")
    for _, r in sites.iterrows():
        log(f"   - **#{int(r['rank'])} {r['location']}**: ${r['addressable_sales']:,.0f} addressable sales from {r['unserved_orders']:,} orders; "
            f"nearest current store is {r['nearest_current_store_km']:.0f} km away.")
    far_cell = opp.sort_values("dist_to_store_km", ascending=False).iloc[0] if len(opp) else None
    if far_cell is not None:
        log(f"   - The most isolated high-demand cell is near ({far_cell['lat']:.1f}, {far_cell['lon']:.1f}), "
            f"{far_cell['dist_to_store_km']:.0f} km from the nearest store.")
    log(f"4. The three sites together address **${sites['addressable_sales'].sum():,.0f}** "
        f"({sites['addressable_sales'].sum() / total_u * 100:.0f}% of all currently unserved sales).")
    log(f"5. Estimated incremental sales at {CAPTURE_RATE:.0%} capture: **${sites['est_annual_sales_won'].sum():,.0f}**.\n")
    log("## 6. Recommendations\n")
    log("1. Open stores in the 3 recommended locations, in rank order (highest addressable demand first).")
    log("2. Before signing leases, validate with local rent, competitor presence and demographics (not in this dataset).")
    log("3. Start with a pilot or pop-up in the #1 area and measure uplift in sales within its catchment.")
    log("4. For the next wave, re-run this analysis after adding the new stores; the next-ranked demand gaps will surface.")
    log("5. Track KPIs: sales within catchment, share of sales beyond 300 km, average distance to nearest store.\n")
    (OUT / "geospatial_report.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print("\nSaved: geospatial_report.md, interactive_map.html, recommended_locations.csv, grid_cells_analysis.csv, charts/")


if __name__ == "__main__":
    main()
