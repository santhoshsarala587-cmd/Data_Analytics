"""
Task 3: Web Traffic Analytics
-----------------------------
Steps: Load logs -> Clean -> Key metrics (page views, sessions, duration, bounce)
       -> Page performance -> Drop-off / exit points -> Funnel -> User journeys
       -> Segments (source / device) -> Time trends -> Charts -> Insights & recommendations

Usage:
    python web_traffic_analysis.py                      # generates a sample traffic log
    python web_traffic_analysis.py --input logs.csv     # your own CSV
Required columns: session_id, user_id, timestamp, page, time_on_page_sec
Optional columns: source, device
"""
import argparse
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).parent
CHARTS = OUT / "charts"
CHARTS.mkdir(exist_ok=True)
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False})

PAGES = ["Home", "Products", "Pricing", "About", "Blog", "Contact"]
FUNNEL = ["Home", "Products", "Pricing", "Contact"]


# ------------------------------------------------------------------ 1. DATA
def generate_logs(n_sessions=8000, seed=11) -> pd.DataFrame:
    """Simulates visitor behaviour with a Markov chain over pages."""
    rng = np.random.default_rng(seed)
    # next-page probabilities (last column = exit)
    T = {
        "Home":     [0.00, 0.38, 0.05, 0.12, 0.15, 0.02, 0.28],
        "Products": [0.08, 0.00, 0.30, 0.04, 0.06, 0.04, 0.48],
        "Pricing":  [0.04, 0.14, 0.00, 0.03, 0.02, 0.17, 0.60],
        "About":    [0.20, 0.18, 0.04, 0.00, 0.08, 0.14, 0.36],
        "Blog":     [0.15, 0.20, 0.03, 0.03, 0.00, 0.02, 0.57],
        "Contact":  [0.10, 0.05, 0.03, 0.02, 0.02, 0.00, 0.78],
    }
    start_p = {"Home": .52, "Products": .17, "Blog": .22, "Pricing": .04, "About": .05}
    mean_time = {"Home": 38, "Products": 75, "Pricing": 120, "About": 45, "Blog": 150, "Contact": 60}
    sources = rng.choice(["Organic Search", "Direct", "Social", "Email", "Paid Ads", "Referral"],
                         n_sessions, p=[.34, .22, .17, .10, .11, .06])
    devices = rng.choice(["Mobile", "Desktop", "Tablet"], n_sessions, p=[.57, .36, .07])
    start = pd.Timestamp("2026-09-01")

    rows = []
    for s in range(n_sessions):
        src, dev = sources[s], devices[s]
        # behaviour differs by channel / device (so the analysis finds real patterns)
        exit_boost = {"Paid Ads": .12, "Social": .08, "Email": -.08, "Direct": -.05}.get(src, 0) \
                     + (.07 if dev == "Mobile" else 0)
        day = int(rng.integers(0, 60))
        hour = int(np.clip(rng.normal(14, 5), 0, 23))
        ts = start + pd.Timedelta(days=day, hours=hour, minutes=int(rng.integers(0, 60)))
        page = rng.choice(list(start_p), p=list(start_p.values()))
        uid = f"U{rng.integers(1, 5200)}"
        for step in range(15):
            t = max(3, rng.gamma(2, mean_time[page] / 2) * (0.8 if dev == "Mobile" else 1.0))
            rows.append((f"S{s}", uid, ts, page, round(float(t), 1), src, dev))
            ts += pd.Timedelta(seconds=float(t))
            p = np.array(T[page], dtype=float)
            p[-1] = min(.95, max(.05, p[-1] + exit_boost))
            p[:-1] *= (1 - p[-1]) / p[:-1].sum()
            nxt = rng.choice(PAGES + ["EXIT"], p=p)
            if nxt == "EXIT":
                break
            page = nxt
    df = pd.DataFrame(rows, columns=["session_id", "user_id", "timestamp", "page",
                                     "time_on_page_sec", "source", "device"])
    # dirty rows so cleaning is meaningful
    df = pd.concat([df, df.sample(60, random_state=1)], ignore_index=True)
    return df.sample(frac=1, random_state=2).reset_index(drop=True)


# ------------------------------------------------------------------ 2. CLEAN
def clean(df):
    n0 = len(df)
    df = df.drop_duplicates().copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["page"] = df["page"].astype(str).str.strip().str.title()
    df["time_on_page_sec"] = pd.to_numeric(df["time_on_page_sec"], errors="coerce")
    df = df.dropna(subset=["session_id", "timestamp", "page"])
    df["time_on_page_sec"] = df["time_on_page_sec"].fillna(df.groupby("page")["time_on_page_sec"].transform("median"))
    df = df[df["time_on_page_sec"].between(0, 1800)]            # drop impossible values (>30 min on one page)
    for c in ["source", "device"]:
        if c not in df:
            df[c] = "Unknown"
    df = df.sort_values(["session_id", "timestamp"]).reset_index(drop=True)
    df["step"] = df.groupby("session_id").cumcount() + 1
    print(f"Cleaning: {n0:,} -> {len(df):,} rows")
    return df


# ------------------------------------------------------------ 3. SESSIONS
def build_sessions(df):
    s = df.groupby("session_id").agg(
        user_id=("user_id", "first"), source=("source", "first"), device=("device", "first"),
        start=("timestamp", "min"), pageviews=("page", "size"),
        duration_sec=("time_on_page_sec", "sum"),
        landing=("page", "first"), exit_page=("page", "last"),
        path=("page", lambda x: " > ".join(x)))
    s["bounced"] = s["pageviews"] == 1
    s["reached_contact"] = s["path"].str.contains("Contact")
    return s


def funnel_counts(sessions):
    counts, remaining = [], sessions
    for stage in FUNNEL:
        remaining = remaining[remaining["path"].apply(lambda p: stage in p)]
        counts.append(len(remaining))
        # ordered: next stage must come after this one
        remaining = remaining.assign(path=remaining["path"].apply(lambda p, st=stage: p.split(st, 1)[1]))
    return counts


def save(fig, name):
    plt.tight_layout()
    fig.savefig(CHARTS / name)
    plt.close(fig)


# ----------------------------------------------------------------- 4. MAIN
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    args = ap.parse_args()
    if args.input:
        raw = pd.read_csv(args.input)
    else:
        raw = generate_logs()
        raw.to_csv(OUT / "web_traffic_logs.csv", index=False)
        print("Generated sample logs -> web_traffic_logs.csv")

    df = clean(raw)
    ses = build_sessions(df)
    L = []
    log = L.append
    log("# Web Traffic Analytics – Findings\n")

    # ---- KPIs
    total_pv, total_s, total_u = len(df), len(ses), ses["user_id"].nunique()
    bounce = ses["bounced"].mean() * 100
    avg_dur, med_dur = ses["duration_sec"].mean(), ses["duration_sec"].median()
    pps = ses["pageviews"].mean()
    conv = ses["reached_contact"].mean() * 100
    log("## 1. Key metrics\n")
    log("| Metric | Value |\n|---|---|")
    log(f"| Total page views | {total_pv:,} |")
    log(f"| Sessions | {total_s:,} |")
    log(f"| Unique visitors | {total_u:,} |")
    log(f"| Pages per session | {pps:.2f} |")
    log(f"| Avg session duration | {avg_dur // 60:.0f}m {avg_dur % 60:.0f}s (median {med_dur // 60:.0f}m {med_dur % 60:.0f}s) |")
    log(f"| Bounce rate (1-page sessions) | {bounce:.1f}% |")
    log(f"| Sessions reaching Contact (goal) | {conv:.1f}% |\n")

    # ---- page performance
    pg = df.groupby("page").agg(page_views=("page", "size"), unique_sessions=("session_id", "nunique"),
                                avg_time_sec=("time_on_page_sec", "mean"))
    exits = ses["exit_page"].value_counts()
    landings = ses["landing"].value_counts()
    pg["exit_rate_%"] = (exits.reindex(pg.index).fillna(0) / pg["page_views"] * 100).round(1)
    pg["landing_sessions"] = landings.reindex(pg.index).fillna(0).astype(int)
    bounces = ses[ses["bounced"]]["landing"].value_counts()
    pg["bounce_rate_%"] = (bounces.reindex(pg.index).fillna(0) / pg["landing_sessions"].replace(0, np.nan) * 100).round(1)
    pg["avg_time_sec"] = pg["avg_time_sec"].round(0)
    pg = pg.sort_values("page_views", ascending=False)
    log("## 2. Page performance\n")
    log(pg.astype(object).fillna("-").to_markdown() + "\n")

    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].bar(pg.index, pg["page_views"], color="#264653")
    ax[0].set(title="Page views by page", ylabel="Views")
    t = pg.sort_values("avg_time_sec", ascending=False)
    ax[1].bar(t.index, t["avg_time_sec"], color="#2a9d8f")
    ax[1].set(title="Average time on page (seconds)")
    save(fig, "01_page_views_and_time.png")

    # ---- drop-off
    e = pg["exit_rate_%"].sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    b = ax.bar(e.index, e.values, color="#e76f51")
    ax.bar_label(b, fmt="%.1f%%", padding=2, fontsize=9)
    ax.set(title="Exit rate by page (drop-off points)", ylabel="% of views that were the last page")
    save(fig, "02_exit_rate.png")

    # ---- funnel
    fc = funnel_counts(ses)
    log("## 3. Conversion funnel (Home > Products > Pricing > Contact)\n")
    log("| Stage | Sessions | % of previous | % of start |\n|---|---|---|---|")
    for i, (st, c) in enumerate(zip(FUNNEL, fc)):
        prev = f"{c / fc[i - 1] * 100:.1f}%" if i else "-"
        log(f"| {st} | {c:,} | {prev} | {c / fc[0] * 100:.1f}% |")
    log("")
    fig, ax = plt.subplots(figsize=(7, 3.8))
    b = ax.barh(FUNNEL[::-1], fc[::-1], color=["#e76f51", "#f4a261", "#2a9d8f", "#264653"])
    ax.bar_label(b, labels=[f"{c:,} ({c / fc[0] * 100:.0f}%)" for c in fc[::-1]], padding=3, fontsize=9)
    ax.set(title="Conversion funnel", xlim=(0, max(fc) * 1.25))
    save(fig, "03_funnel.png")
    worst_i = int(np.argmin([fc[i] / fc[i - 1] for i in range(1, len(fc))])) + 1
    worst_drop = (1 - fc[worst_i] / fc[worst_i - 1]) * 100

    # ---- journeys
    log("## 4. User journeys\n")
    top_paths = ses["path"].value_counts().head(10)
    log("**Top 10 most common paths**\n")
    log("| Path | Sessions | % |\n|---|---|---|")
    for p, c in top_paths.items():
        log(f"| {p} | {c:,} | {c / total_s * 100:.1f}% |")
    log("")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.barh(top_paths.index[::-1], top_paths.values[::-1], color="#264653")
    ax.set(title="Top 10 user journeys", xlabel="Sessions")
    save(fig, "04_top_paths.png")

    # page-to-page transitions
    df["next_page"] = df.groupby("session_id")["page"].shift(-1).fillna("EXIT")
    trans = pd.crosstab(df["page"], df["next_page"], normalize="index") * 100
    cols = [c for c in PAGES + ["EXIT"] if c in trans.columns]
    trans = trans.reindex(index=[p for p in PAGES if p in trans.index], columns=cols).fillna(0)
    fig, ax = plt.subplots(figsize=(7.5, 5))
    im = ax.imshow(trans.values, cmap="YlOrRd")
    ax.set_xticks(range(len(cols)), cols, rotation=30)
    ax.set_yticks(range(len(trans.index)), trans.index)
    for i in range(trans.shape[0]):
        for j in range(trans.shape[1]):
            ax.text(j, i, f"{trans.values[i, j]:.0f}", ha="center", va="center", fontsize=8)
    ax.set(title="Where do users go next? (% from page > to page)", xlabel="Next page", ylabel="Current page")
    plt.colorbar(im, ax=ax, shrink=.8)
    save(fig, "05_transition_heatmap.png")

    pairs = Counter()
    for p in ses["path"]:
        parts = p.split(" > ")
        pairs.update(zip(parts, parts[1:]))
    log("**Most common page-to-page moves**\n")
    log("| From | To | Count |\n|---|---|---|")
    for (a, b_), c in pairs.most_common(6):
        log(f"| {a} | {b_} | {c:,} |")
    log("")

    # ---- segments
    def seg(col):
        g = ses.groupby(col).agg(sessions=("pageviews", "size"), bounce_rate=("bounced", lambda x: x.mean() * 100),
                                 avg_duration_sec=("duration_sec", "mean"), pages_per_session=("pageviews", "mean"),
                                 contact_rate=("reached_contact", lambda x: x.mean() * 100)).round(1)
        return g.sort_values("sessions", ascending=False)
    src, dev = seg("source"), seg("device")
    log("## 5. Traffic sources and devices\n")
    log("**By source**\n\n" + src.to_markdown() + "\n")
    log("**By device**\n\n" + dev.to_markdown() + "\n")
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    s2 = src.sort_values("bounce_rate")
    ax[0].barh(s2.index, s2["bounce_rate"], color="#e76f51")
    ax[0].set(title="Bounce rate by source (%)")
    s3 = src.sort_values("contact_rate")
    ax[1].barh(s3.index, s3["contact_rate"], color="#2a9d8f")
    ax[1].set(title="Sessions reaching Contact by source (%)")
    save(fig, "06_source_performance.png")
    fig, ax = plt.subplots(figsize=(5.5, 4))
    d2 = dev.sort_index()
    ax.bar(d2.index, d2["bounce_rate"], color="#f4a261")
    ax.set(title="Bounce rate by device (%)")
    save(fig, "07_device_bounce.png")

    # ---- time trends
    ses["date"] = ses["start"].dt.date
    daily = ses.groupby("date").size()
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.plot(daily.index, daily.values, color="#264653", lw=1.2)
    ax.plot(daily.index, daily.rolling(7).mean(), color="#e76f51", lw=2, label="7-day average")
    ax.set(title="Daily sessions", ylabel="Sessions")
    ax.legend(frameon=False)
    save(fig, "08_daily_sessions.png")
    hour = ses["start"].dt.hour.value_counts().sort_index()
    peak_hr = int(hour.idxmax())
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.bar(hour.index, hour.values, color="#2a9d8f")
    ax.set(title="Sessions by hour of day", xlabel="Hour")
    save(fig, "09_hourly.png")
    ses["dow"] = ses["start"].dt.day_name()
    dow = ses["dow"].value_counts()

    # ---- insights
    top_page = pg.index[0]
    e_nogoal = e.drop("Contact", errors="ignore")      # Contact is the goal page, so exiting there is normal
    high_exit = e_nogoal.index[0]
    blog_t = pg["avg_time_sec"].get("Blog", np.nan)
    blog_x = pg["exit_rate_%"].get("Blog", np.nan)
    price_t = pg["avg_time_sec"].get("Pricing", np.nan)
    best_src = src.sort_values("contact_rate", ascending=False).index[0]
    worst_src = src.sort_values("bounce_rate", ascending=False).index[0]
    has_md = {"Mobile", "Desktop"} <= set(dev.index)
    log("## 6. Key insights\n")
    log(f"1. **Traffic**: {total_s:,} sessions generated {total_pv:,} page views ({pps:.1f} pages per session).")
    log(f"2. **Most viewed page** is {top_page} ({pg.loc[top_page, 'page_views']:,} views); "
        f"the page where people spend most time is {pg['avg_time_sec'].idxmax()} ({pg['avg_time_sec'].max():.0f}s).")
    log(f"3. **Biggest drop-off page**: {high_exit} has the highest exit rate ({e_nogoal.iloc[0]}%) "
        f"(Contact is excluded because leaving after contacting you is the goal, not a loss).")
    log(f"4. **Funnel leak**: the weakest funnel step is {FUNNEL[worst_i - 1]} to {FUNNEL[worst_i]} "
        f"(lose {worst_drop:.0f}% of visitors); only {fc[-1] / fc[0] * 100:.1f}% of Home visitors reach Contact.")
    log(f"5. **Bounce rate** is {bounce:.1f}% overall; {worst_src} traffic bounces the most "
        f"({src.loc[worst_src, 'bounce_rate']}%).")
    log(f"6. **Best converting source**: {best_src} ({src.loc[best_src, 'contact_rate']}% reach Contact).")
    if has_md:
        mob, desk = dev.loc["Mobile"], dev.loc["Desktop"]
        log(f"7. **Mobile vs desktop**: mobile bounce rate {mob['bounce_rate']}% vs {desk['bounce_rate']}% on desktop; "
            f"mobile sessions last {mob['avg_duration_sec']:.0f}s vs {desk['avg_duration_sec']:.0f}s.")
    else:
        log("7. **Device**: see the device table above.")
    log(f"8. **Peak time**: most sessions start around {peak_hr}:00; busiest weekday is {dow.index[0]}.\n")

    log("## 7. Recommendations to improve engagement\n")
    log("| # | Finding | Recommendation | KPI |\n|---|---|---|---|")
    log(f"| 1 | {high_exit} has the highest exit rate ({e_nogoal.iloc[0]}%) | Add clear next-step buttons and related links on that page | Exit rate |")
    log(f"| 2 | Biggest funnel loss: {FUNNEL[worst_i - 1]} to {FUNNEL[worst_i]} | Add a CTA, testimonials and a simple contact form on the earlier page | Funnel step conversion |")
    log(f"| 3 | {worst_src} traffic bounces most | Match landing page to the ad/post message; speed up first load | Bounce rate by source |")
    log("| 4 | Mobile bounces more than desktop | Optimise mobile layout, image size, sticky call-to-action | Mobile bounce rate |")
    log(f"| 5 | Blog holds attention ({blog_t:.0f}s) but {blog_x:.0f}% leave from it | Add product CTAs and email sign-up inside blog posts | Blog to Products clicks |")
    log(f"| 6 | People read Pricing ({price_t:.0f}s) but few go on to Contact | Add FAQ, comparison table and a 'talk to us' button on Pricing | Pricing to Contact rate |")
    log(f"| 7 | Traffic peaks around {peak_hr}:00 | Schedule posts, emails and campaigns shortly before the peak | Sessions at peak |")
    log(f"| 8 | Best converting source is {best_src} | Invest more in this channel and replicate its content | Cost per contact |\n")

    (OUT / "web_traffic_report.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\nSaved web_traffic_report.md and {len(list(CHARTS.glob('*.png')))} charts in /charts")


if __name__ == "__main__":
    main()
