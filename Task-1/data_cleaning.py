"""
Task 1: Data Cleaning & Structural Validation
---------------------------------------------
Pipeline: Load -> Profile -> Clean -> Validate -> Export -> Report

Usage:
    python data_cleaning.py                     # generates a sample messy dataset and cleans it
    python data_cleaning.py --input my_data.csv # cleans your own CSV (column names are auto-standardised)
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).parent
RAW_PATH = OUT / "raw_data.csv"
CLEAN_PATH = OUT / "cleaned_data.csv"
REPORT_PATH = OUT / "cleaning_report.json"

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


# ------------------------------------------------------------------ 1. DATA
def generate_messy_data(n=200, seed=42) -> pd.DataFrame:
    """Creates a realistic messy dataset: duplicates, missing values, mixed formats."""
    rng = np.random.default_rng(seed)
    names = ["Arun Kumar", "priya sharma", "RAJESH  KUMAR", " Divya R ", "santhosh m",
             "Meena Iyer", "karthik S", "Anita Das", "Vikram Singh", "lakshmi N"]
    cities = ["Coimbatore", "coimbatore ", "CHENNAI", "Chennai", "Madurai", "bangalore",
              "Bengaluru", "Hyderabad", "hyd", "Salem"]
    depts = ["Sales", "sales", "HR", "hr", "IT", "it ", "Finance", "FINANCE"]
    date_fmts = ["%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y", "%d-%m-%Y"]

    rows = []
    for i in range(n):
        d = pd.Timestamp("2022-01-01") + pd.Timedelta(days=int(rng.integers(0, 1000)))
        name = rng.choice(names)
        rows.append({
            "Employee ID": f"E{1000 + i}",
            "Full Name": name,
            "Email": f"{name.strip().lower().replace(' ', '.')}{i}@example.com",
            "Phone": rng.choice([f"+91 {rng.integers(7000000000, 9999999999)}",
                                 f"{rng.integers(7000000000, 9999999999)}",
                                 f"{str(rng.integers(7000000000, 9999999999))[:5]}-{str(rng.integers(7000000000, 9999999999))[5:]}"]),
            "City": rng.choice(cities),
            "Department": rng.choice(depts),
            "Joining Date": d.strftime(rng.choice(date_fmts)),
            "Salary": rng.choice([str(int(rng.integers(20000, 90000))),
                                  f"Rs. {int(rng.integers(20000, 90000)):,}",
                                  f"{int(rng.integers(20000, 90000)):,}"]),
            "Age": int(rng.integers(21, 60)),
        })
    df = pd.DataFrame(rows).astype(object)

    # inject problems
    for col, frac in [("Email", .06), ("Phone", .08), ("City", .05), ("Salary", .07), ("Age", .06), ("Joining Date", .04)]:
        idx = rng.choice(df.index, int(n * frac), replace=False)
        df.loc[idx, col] = rng.choice([np.nan, "", "N/A", "null", "-"], len(idx))
    df.loc[rng.choice(df.index, 3, replace=False), "Age"] = [-5, 250, 999]       # outliers
    df.loc[rng.choice(df.index, 3, replace=False), "Email"] = ["bad.email", "no@domain", "@x.com"]  # invalid
    dups = df.sample(15, random_state=1)                                         # exact duplicates
    df = pd.concat([df, dups], ignore_index=True)
    near = df.sample(5, random_state=2).copy()                                   # near duplicates (case/space)
    near["Full Name"] = near["Full Name"].str.upper() + " "
    df = pd.concat([df, near], ignore_index=True)
    return df.sample(frac=1, random_state=3).reset_index(drop=True)


# ---------------------------------------------------------------- 2. PROFILE
def profile(df: pd.DataFrame) -> dict:
    return {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "missing_per_column": {c: int(v) for c, v in standardise_missing(df).isna().sum().items()},
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
    }


# ----------------------------------------------------------------- 3. CLEAN
def standardise_columns(df):
    df = df.copy()
    df.columns = [re.sub(r"\W+", "_", c.strip().lower()).strip("_") for c in df.columns]
    return df


def standardise_missing(df):
    """Convert every 'fake missing' marker into a real NaN."""
    markers = {"", "na", "n/a", "nan", "null", "none", "-", "--", "?", "unknown"}
    df = df.copy()
    for c in df.select_dtypes(include=["object", "string"]).columns:
        df[c] = df[c].astype("object").where(
            ~df[c].astype(str).str.strip().str.lower().isin(markers), np.nan)
    return df


def clean_text(df, cols, case="title"):
    for c in cols:
        s = df[c].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
        df[c] = s.str.title() if case == "title" else s.str.upper() if case == "upper" else s.str.lower()
    return df


def parse_dates(series):
    """Handles multiple formats in one column."""
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%b %d, %Y", "%d-%m-%Y"]
    result = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")
    for fmt in formats:
        mask = result.isna() & series.notna()
        result[mask] = pd.to_datetime(series[mask], format=fmt, errors="coerce")
    return result


def clean_phone(s):
    digits = s.astype("string").str.replace(r"\D", "", regex=True)
    digits = digits.str[-10:]                       # keep last 10 digits (drops +91)
    return digits.where(digits.str.len() == 10, pd.NA)


def clean_money(s):
    cleaned = s.astype("string").str.replace(r"[^\d.]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")


def clean(df: pd.DataFrame, log: dict) -> pd.DataFrame:
    df = standardise_columns(df)
    df = standardise_missing(df)

    # 3a. text normalisation
    df = clean_text(df, ["full_name"], "title")
    df = clean_text(df, ["city", "department"], "title")
    df["email"] = df["email"].astype("string").str.strip().str.lower()

    # 3b. consistent category values (map aliases to a single label)
    city_map = {"Hyd": "Hyderabad", "Bangalore": "Bengaluru"}
    df["city"] = df["city"].replace(city_map)
    df["department"] = df["department"].replace({"Hr": "HR", "It": "IT"})

    # 3c. type conversion
    df["joining_date"] = parse_dates(df["joining_date"])
    df["phone"] = clean_phone(df["phone"])
    df["salary"] = clean_money(df["salary"])
    df["age"] = pd.to_numeric(df["age"], errors="coerce")

    # 3d. invalid values -> NaN (do not silently keep wrong data)
    bad_email = ~df["email"].fillna("").str.match(EMAIL_RE) & df["email"].notna()
    log["invalid_emails_set_to_null"] = int(bad_email.sum())
    df.loc[bad_email, "email"] = pd.NA

    bad_age = df["age"].notna() & ~df["age"].between(18, 70)
    log["out_of_range_ages_set_to_null"] = int(bad_age.sum())
    df.loc[bad_age, "age"] = np.nan

    # 3e. remove duplicates (after normalising, so near-duplicates are caught too)
    before = len(df)
    df = df.drop_duplicates(subset=[c for c in df.columns if c != "employee_id"], keep="first")
    df = df.drop_duplicates(subset=["employee_id"], keep="first")
    log["duplicates_removed"] = int(before - len(df))

    # 3f. missing value handling
    log["missing_before_imputation"] = {c: int(v) for c, v in df.isna().sum().items() if v}
    df["city"] = df["city"].fillna("Unknown")                       # categorical -> label
    df["department"] = df["department"].fillna("Unknown")
    df["age"] = df["age"].fillna(df["age"].median()).round().astype("Int64")  # numeric -> median
    df["salary"] = df["salary"].fillna(df.groupby("department")["salary"].transform("median"))
    df["salary"] = df["salary"].fillna(df["salary"].median())
    # email / phone / joining_date stay NULL: guessing them would corrupt data integrity
    log["imputation_strategy"] = {
        "age": "median", "salary": "median per department (fallback overall median)",
        "city/department": "'Unknown'", "email/phone/joining_date": "left null (not guessable)"}

    return df.reset_index(drop=True)


# ------------------------------------------------------------- 4. VALIDATE
def validate(df: pd.DataFrame) -> dict:
    checks = {
        "no_duplicate_rows": not df.duplicated().any(),
        "employee_id_unique": df["employee_id"].is_unique,
        "no_null_employee_id": df["employee_id"].notna().all(),
        "dates_are_datetime": pd.api.types.is_datetime64_any_dtype(df["joining_date"]),
        "age_in_range_18_70": df["age"].dropna().between(18, 70).all(),
        "salary_positive": (df["salary"] > 0).all(),
        "phone_is_10_digits": df["phone"].dropna().str.len().eq(10).all(),
        "emails_valid": df["email"].dropna().str.match(EMAIL_RE).all(),
        "no_leading_trailing_spaces": all(
            (df[c].dropna().astype(str) == df[c].dropna().astype(str).str.strip()).all()
            for c in ["full_name", "city", "department"]),
        "no_missing_in_age_salary_city_dept": not df[["age", "salary", "city", "department"]].isna().any().any(),
    }
    failed = [k for k, v in checks.items() if not v]
    for k, v in checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    if failed:
        raise AssertionError(f"Validation failed: {failed}")
    return {k: bool(v) for k, v in checks.items()}


# -------------------------------------------------------------------- MAIN
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="Path to your raw CSV (optional)")
    args = ap.parse_args()

    if args.input:
        raw = pd.read_csv(args.input, dtype=str)
    else:
        raw = generate_messy_data()
        raw.to_csv(RAW_PATH, index=False)
        print(f"Generated sample messy data -> {RAW_PATH.name}")

    report = {"before": profile(raw)}
    print("\n== BEFORE ==")
    print(json.dumps(report["before"], indent=2))

    cleaned = clean(raw, log := {})
    report["cleaning_log"] = log

    print("\n== VALIDATION ==")
    report["validation"] = validate(cleaned)

    report["after"] = profile(cleaned)
    cleaned.to_csv(CLEAN_PATH, index=False)
    REPORT_PATH.write_text(json.dumps(report, indent=2, default=str))

    print("\n== AFTER ==")
    print(json.dumps(report["after"], indent=2))
    print(f"\nSaved: {CLEAN_PATH.name}, {REPORT_PATH.name}")


if __name__ == "__main__":
    main()
