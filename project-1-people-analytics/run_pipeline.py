"""
Meridian Works: raw -> clean (pure-Python version)

This mirrors clean_data.sql line for line, step for step, but runs on
Python's standard library only (csv, re, datetime) instead of DuckDB.

Why this exists: DuckDB has no precompiled wheel for Termux/ARM, so
`pip install duckdb` means compiling from source on-device, which can take
30-60+ minutes and risks getting killed by the OS mid-build on a phone.
This produces an identical meridian_works_clean.csv without that dependency.

clean_data.sql remains the canonical documented pipeline (DuckDB syntax,
readable as a single declarative script). This file is a drop-in runtime
substitute that does the same transformations imperatively.

Usage: python run_pipeline.py
"""

import csv
import re
from datetime import datetime

RAW_PATH = "meridian_works_raw.csv"
CLEAN_PATH = "meridian_works_clean.csv"

EMPTY_TERM_VALUES = {"", "NULL", "N/A"}
DATE_FORMATS = ["%d/%m/%Y", "%Y-%m-%d", "%d %b %Y", "%Y/%m/%d"]

SCORE_WORDS = {"low": 1, "medium": 2, "high": 3, "very high": 4}


def parse_date(value):
    if value is None:
        return None
    value = value.strip()
    if value in EMPTY_TERM_VALUES:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def clean_name(raw_name):
    # trim, lowercase, split on whitespace, title-case each word, rejoin
    # with single spaces (mirrors the SQL's list_transform + regexp_replace)
    words = raw_name.strip().lower().split()
    titled = [w[:1].upper() + w[1:] if w else w for w in words]
    return " ".join(titled).strip()


def clean_department(raw_dept):
    d = raw_dept.strip().lower()
    if d in ("sales", "sal3s"):
        return "Sales"
    if d in ("eng.", "engineering"):
        return "Engineering"
    if d in ("hr", "human resources"):
        return "Human Resources"
    return raw_dept.strip()


def clean_income(raw_income):
    stripped = re.sub(r"[\$,]", "", raw_income or "")
    try:
        val = float(stripped)
    except ValueError:
        return None
    return round(val) if val > 0 else None


def clean_score(raw_score):
    s = (raw_score or "").strip().lower()
    if s in SCORE_WORDS:
        return SCORE_WORDS[s]
    try:
        n = int(raw_score)
    except (TypeError, ValueError):
        return None
    return n if 1 <= n <= 4 else None


def clean_int(raw_val):
    try:
        return int(raw_val)
    except (TypeError, ValueError):
        return None


def clean_float(raw_val):
    try:
        return float(raw_val)
    except (TypeError, ValueError):
        return None


def main():
    print("Loading raw export...")
    with open(RAW_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(f"  {len(rows)} raw rows")

    # Step 1: dedupe on emp_id, keep first occurrence
    seen = set()
    deduped = []
    for row in rows:
        if row["emp_id"] in seen:
            continue
        seen.add(row["emp_id"])
        deduped.append(row)
    print(f"  {len(deduped)} rows after dedupe")

    # Step 2: clean and cast every column
    clean_rows = []
    for row in deduped:
        term_date_raw = (row.get("term_date") or "").strip()
        clean_rows.append({
            "EmployeeID": row["emp_id"],
            "FullName": clean_name(row["full_name"]),
            "Department": clean_department(row["department"]),
            "JobRole": row["job_role"],
            "HireDate": parse_date(row["hire_date"]) or "",
            "TermDate": parse_date(term_date_raw) or "",
            "MonthlyIncome": clean_income(row["monthly_income"]) or "",
            "Age": clean_int(row["age"]) if clean_int(row["age"]) is not None else "",
            "Gender": row["gender"],
            "TenureYears": clean_float(row["tenure_years"]) if clean_float(row["tenure_years"]) is not None else "",
            "EnvironmentSatisfaction": clean_score(row["environment_satisfaction"]) if clean_score(row["environment_satisfaction"]) is not None else "",
            "JobInvolvement": clean_score(row["job_involvement"]) if clean_score(row["job_involvement"]) is not None else "",
            "JobSatisfaction": clean_score(row["job_satisfaction"]) if clean_score(row["job_satisfaction"]) is not None else "",
            "RelationshipSatisfaction": clean_score(row["relationship_satisfaction"]) if clean_score(row["relationship_satisfaction"]) is not None else "",
            "WorkLifeBalance": clean_score(row["work_life_balance"]) if clean_score(row["work_life_balance"]) is not None else "",
            "Attrition": "No" if term_date_raw in EMPTY_TERM_VALUES else "Yes",
        })

    fieldnames = [
        "EmployeeID", "FullName", "Department", "JobRole", "HireDate", "TermDate",
        "MonthlyIncome", "Age", "Gender", "TenureYears",
        "EnvironmentSatisfaction", "JobInvolvement", "JobSatisfaction",
        "RelationshipSatisfaction", "WorkLifeBalance", "Attrition",
    ]

    with open(CLEAN_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(clean_rows)

    attrition_rate = sum(1 for r in clean_rows if r["Attrition"] == "Yes") / len(clean_rows)
    print(f"Pipeline execution finalized. {len(clean_rows)} rows written to '{CLEAN_PATH}'.")
    print(f"Attrition rate: {attrition_rate:.1%}")


if __name__ == "__main__":
    main()
