# Web Traffic Analytics – Findings

## 1. Key metrics

| Metric | Value |
|---|---|
| Total page views | 16,270 |
| Sessions | 8,000 |
| Unique visitors | 4,071 |
| Pages per session | 2.03 |
| Avg session duration | 2m 21s (median 1m 42s) |
| Bounce rate (1-page sessions) | 44.7% |
| Sessions reaching Contact (goal) | 9.4% |

## 2. Page performance

| page     |   page_views |   unique_sessions |   avg_time_sec |   exit_rate_% |   landing_sessions | bounce_rate_%   |
|:---------|-------------:|------------------:|---------------:|--------------:|-------------------:|:----------------|
| Home     |         5228 |              4719 |             34 |          32.1 |               4187 | 32.4            |
| Products |         4264 |              3798 |             67 |          52.1 |               1347 | 53.6            |
| Blog     |         2860 |              2737 |            132 |          61.4 |               1758 | 62.8            |
| Pricing  |         1843 |              1714 |            106 |          62.5 |                302 | 64.2            |
| About    |         1312 |              1242 |             40 |          42.4 |                406 | 48.3            |
| Contact  |          763 |               750 |             54 |          83.4 |                  0 | -               |

## 3. Conversion funnel (Home > Products > Pricing > Contact)

| Stage | Sessions | % of previous | % of start |
|---|---|---|---|
| Home | 4,719 | - | 100.0% |
| Products | 2,095 | 44.4% | 44.4% |
| Pricing | 625 | 29.8% | 13.2% |
| Contact | 109 | 17.4% | 2.3% |

## 4. User journeys

**Top 10 most common paths**

| Path | Sessions | % |
|---|---|---|
| Home | 1,358 | 17.0% |
| Blog | 1,104 | 13.8% |
| Home > Products | 791 | 9.9% |
| Products | 722 | 9.0% |
| Home > Blog | 349 | 4.4% |
| Home > Products > Pricing | 249 | 3.1% |
| Products > Pricing | 245 | 3.1% |
| Home > About | 198 | 2.5% |
| About | 196 | 2.5% |
| Pricing | 194 | 2.4% |

**Most common page-to-page moves**

| From | To | Count |
|---|---|---|
| Home | Products | 1,885 |
| Products | Pricing | 1,195 |
| Home | Blog | 741 |
| Home | About | 615 |
| Blog | Products | 538 |
| Blog | Home | 365 |

## 5. Traffic sources and devices

**By source**

| source         |   sessions |   bounce_rate |   avg_duration_sec |   pages_per_session |   contact_rate |
|:---------------|-----------:|--------------:|-------------------:|--------------------:|---------------:|
| Organic Search |       2763 |          42.8 |              140.1 |                 2   |            9.5 |
| Direct         |       1766 |          39.5 |              156.4 |                 2.2 |           10.7 |
| Social         |       1377 |          53.7 |              121   |                 1.7 |            7.6 |
| Paid Ads       |        850 |          56.4 |              108   |                 1.7 |            5.8 |
| Email          |        787 |          34.3 |              178.8 |                 2.5 |           12.7 |
| Referral       |        457 |          44.9 |              140.7 |                 2.1 |            9.8 |

**By device**

| device   |   sessions |   bounce_rate |   avg_duration_sec |   pages_per_session |   contact_rate |
|:---------|-----------:|--------------:|-------------------:|--------------------:|---------------:|
| Mobile   |       4555 |          47.6 |              117.7 |                 1.9 |            8.1 |
| Desktop  |       2880 |          40.4 |              171.9 |                 2.2 |           11.2 |
| Tablet   |        565 |          42.7 |              169.1 |                 2.2 |           10.4 |

## 6. Key insights

1. **Traffic**: 8,000 sessions generated 16,270 page views (2.0 pages per session).
2. **Most viewed page** is Home (5,228 views); the page where people spend most time is Blog (132s).
3. **Biggest drop-off page**: Pricing has the highest exit rate (62.5%) (Contact is excluded because leaving after contacting you is the goal, not a loss).
4. **Funnel leak**: the weakest funnel step is Pricing to Contact (lose 83% of visitors); only 2.3% of Home visitors reach Contact.
5. **Bounce rate** is 44.7% overall; Paid Ads traffic bounces the most (56.4%).
6. **Best converting source**: Email (12.7% reach Contact).
7. **Mobile vs desktop**: mobile bounce rate 47.6% vs 40.4% on desktop; mobile sessions last 118s vs 172s.
8. **Peak time**: most sessions start around 14:00; busiest weekday is Friday.

## 7. Recommendations to improve engagement

| # | Finding | Recommendation | KPI |
|---|---|---|---|
| 1 | Pricing has the highest exit rate (62.5%) | Add clear next-step buttons and related links on that page | Exit rate |
| 2 | Biggest funnel loss: Pricing to Contact | Add a CTA, testimonials and a simple contact form on the earlier page | Funnel step conversion |
| 3 | Paid Ads traffic bounces most | Match landing page to the ad/post message; speed up first load | Bounce rate by source |
| 4 | Mobile bounces more than desktop | Optimise mobile layout, image size, sticky call-to-action | Mobile bounce rate |
| 5 | Blog holds attention (132s) but 61% leave from it | Add product CTAs and email sign-up inside blog posts | Blog to Products clicks |
| 6 | People read Pricing (106s) but few go on to Contact | Add FAQ, comparison table and a 'talk to us' button on Pricing | Pricing to Contact rate |
| 7 | Traffic peaks around 14:00 | Schedule posts, emails and campaigns shortly before the peak | Sessions at peak |
| 8 | Best converting source is Email | Invest more in this channel and replicate its content | Cost per contact |
