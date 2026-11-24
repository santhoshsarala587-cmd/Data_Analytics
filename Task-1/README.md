# Task 1 – Data Cleaning & Structural Validation

A reproducible pipeline that turns a messy dataset (duplicates, missing values, inconsistent formats) into a clean, validated one.

## Run
```bash
pip install pandas numpy
python data_cleaning.py                      # uses a generated messy sample dataset
python data_cleaning.py --input your.csv     # or your own CSV
```

## Pipeline
1. **Profile** – rows, dtypes, duplicates, missing values (including fake ones like `N/A`, `null`, `-`).
2. **Standardise** – snake_case column names, trim/collapse whitespace, consistent casing.
3. **Fix formats** – 4 mixed date formats -> one datetime; phones -> 10 digits; salary `Rs. 45,000` -> `45000`.
4. **Consistent categories** – `hyd`->Hyderabad, `Bangalore`->Bengaluru, `hr`->HR.
5. **Invalid data** – bad emails and ages outside 18–70 become null (never silently kept).
6. **Deduplicate** – after normalising, so near-duplicates (case/space differences) are also removed.
7. **Missing values** – age: median; salary: median per department; city/department: `Unknown`; email/phone/date: left null (can't be guessed, preserves integrity).
8. **Validate** – 10 automated checks; script fails loudly if any check fails.
9. **Export** – `cleaned_data.csv` + `cleaning_report.json` (before/after stats).

## Results (sample data)
| Metric | Before | After |
|---|---|---|
| Rows | 220 | 200 |
| Duplicate rows | 15 exact + 5 near | 0 |
| Date formats | 4 mixed | 1 (datetime) |
| Validation checks | – | 10/10 pass |

## Files
- `data_cleaning.py` – pipeline
- `raw_data.csv` – messy input
- `cleaned_data.csv` – output
- `cleaning_report.json` – audit log
