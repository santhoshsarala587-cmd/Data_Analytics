"""
Task 5: Interactive Dashboard Development
-----------------------------------------
1) Generates sample business data (sales_data.csv, department_kpis.csv)
2) Embeds the data into dashboard_template.html -> index.html (a single self-contained file, no libraries, works offline)

Usage:
    python build_dashboard.py                      # generate sample data + build dashboard
    python build_dashboard.py --sales my_sales.csv --kpis my_kpis.csv   # use your own CSVs
sales CSV : month(YYYY-MM), region, category, revenue, profit, orders, target_revenue
kpis  CSV : month, region, department, kpi, value, target
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).parent
REGIONS = ["North", "South", "East", "West", "Central"]
CATS = ["Electronics", "Apparel", "Home", "Grocery"]
MONTHS = [d.strftime("%Y-%m") for d in pd.date_range("2025-01-01", "2026-10-01", freq="MS")]

# kpi: (department, unit, better, aggregation, decimals, base value, base target)
KPI_META = {
    "Win rate":              ("Sales", "%", "higher", "mean", 1, 27, 30),
    "Avg deal size":         ("Sales", "$K", "higher", "mean", 1, 14.5, 15),
    "Sales cycle":           ("Sales", "days", "lower", "mean", 0, 46, 42),
    "Leads generated":       ("Marketing", "", "higher", "sum", 0, 820, 900),
    "Lead conversion":       ("Marketing", "%", "higher", "mean", 1, 11.5, 12.5),
    "Cost per lead":         ("Marketing", "$", "lower", "mean", 1, 24, 22),
    "Gross margin":          ("Finance", "%", "higher", "mean", 1, 38, 39),
    "Opex ratio":            ("Finance", "%", "lower", "mean", 1, 24, 23),
    "Days sales outstanding": ("Finance", "days", "lower", "mean", 0, 41, 38),
    "Headcount":             ("HR", "", "higher", "sum", 0, 120, 125),
    "Attrition":             ("HR", "%", "lower", "mean", 1, 1.3, 1.0),
    "Employee satisfaction": ("HR", "/5", "higher", "mean", 2, 3.9, 4.1),
    "On-time delivery":      ("Operations", "%", "higher", "mean", 1, 92, 95),
    "Defect rate":           ("Operations", "%", "lower", "mean", 2, 2.1, 1.8),
    "Fulfilment time":       ("Operations", "days", "lower", "mean", 1, 3.4, 3.0),
}


def make_sales(seed=5):
    rng = np.random.default_rng(seed)
    base = {"North": 95, "South": 110, "East": 150, "West": 130, "Central": 85}          # $K / month / category
    growth = {"North": .010, "South": -.002, "East": .012, "West": .022, "Central": .004}  # monthly trend
    cat_mult = {"Electronics": 1.5, "Apparel": 1.0, "Home": .9, "Grocery": 1.2}
    margin = {"Electronics": .17, "Apparel": .30, "Home": .26, "Grocery": .14}
    rows = []
    for i, m in enumerate(MONTHS):
        mo = int(m[-2:])
        season = 1 + .12 * np.sin((mo - 3) / 12 * 2 * np.pi) + (.10 if mo in (11, 12) else 0)
        for r in REGIONS:
            for c in CATS:
                rev = base[r] * cat_mult[c] * (1 + growth[r]) ** i * season * rng.normal(1, .05) * 1000
                mg = margin[c] + rng.normal(0, .012)
                if r == "South" and c == "Apparel":
                    mg -= .008 * i * .6                      # margin erosion
                if r == "Central" and c == "Electronics":
                    rev *= .88                                # underperformer
                tgt = base[r] * cat_mult[c] * (1.008) ** i * (1 + .12 * np.sin((mo - 3) / 12 * 2 * np.pi) + (.10 if mo in (11, 12) else 0)) * 1000 * 1.02
                rows.append([m, r, c, round(rev), round(rev * mg), int(rev / rng.normal(58, 4)), round(tgt)])
    return pd.DataFrame(rows, columns=["month", "region", "category", "revenue", "profit", "orders", "target_revenue"])


def make_kpis(seed=6):
    rng = np.random.default_rng(seed)
    rows = []
    reg_bias = {"North": 0, "South": -.04, "East": .02, "West": .03, "Central": -.03}
    for i, m in enumerate(MONTHS):
        for r in REGIONS:
            for k, (dept, unit, better, agg, dec, bv, bt) in KPI_META.items():
                scale = 1 / len(REGIONS) if agg == "sum" else 1
                sign = 1 if better == "higher" else -1
                drift = (.004 * i) * (1 if k not in ("Attrition", "Defect rate") else -.2)   # slow improvement
                v = bv * (1 + sign * (reg_bias[r] + drift) + rng.normal(0, .025)) * scale
                if r == "South" and k in ("Attrition", "Days sales outstanding"):
                    v *= 1 + .01 * i * .4                                                      # getting worse
                t = bt * scale
                rows.append([m, r, dept, k, round(v, 3), round(t, 3)])
    return pd.DataFrame(rows, columns=["month", "region", "department", "kpi", "value", "target"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sales")
    ap.add_argument("--kpis")
    a = ap.parse_args()
    sales = pd.read_csv(a.sales) if a.sales else make_sales()
    kpis = pd.read_csv(a.kpis) if a.kpis else make_kpis()
    if not a.sales:
        sales.to_csv(OUT / "sales_data.csv", index=False)
    if not a.kpis:
        kpis.to_csv(OUT / "department_kpis.csv", index=False)

    payload = {
        "months": sorted(sales["month"].unique().tolist()),
        "regions": sorted(sales["region"].unique().tolist()),
        "categories": sorted(sales["category"].unique().tolist()),
        "sales": sales[["month", "region", "category", "revenue", "profit", "orders", "target_revenue"]].values.tolist(),
        "kpis": kpis[["month", "region", "department", "kpi", "value", "target"]].values.tolist(),
        "kpi_meta": {k: {"dept": v[0], "unit": v[1], "better": v[2], "agg": v[3], "dec": v[4]} for k, v in KPI_META.items()},
    }
    html = (OUT / "dashboard_template.html").read_text(encoding="utf-8").replace("__DATA__", json.dumps(payload, separators=(",", ":")))
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(f"Built index.html  ({len(html) // 1024} KB) | sales rows: {len(sales):,} | kpi rows: {len(kpis):,}")


if __name__ == "__main__":
    main()
