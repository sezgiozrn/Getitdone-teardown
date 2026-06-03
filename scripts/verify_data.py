"""Validate Get It Done data before any analysis touches it.

Checks are derived from the caveats the city itself documents on the dataset
page (duplicates, referrals, notified-vs-fixed timestamps) plus generic
sanity checks. Analysis findings are only trustworthy if this passes — or if
its warnings are explicitly accounted for in the memo.

Usage:
    python scripts/verify_data.py
Exit code 0 = all hard checks passed (warnings allowed).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Columns the analysis actually depends on. The portal occasionally renames
# columns; this check fails loudly instead of letting downstream code KeyError.
REQUIRED_COLUMNS = {
    "service_request_id",
    "date_requested",
    "status",
    "service_name",
    "council_district",
}
OPTIONAL_COLUMNS = {
    "date_closed",
    "case_age_days",
    "case_origin",       # intake channel: app / web / phone
    "comm_plan_name",
    "public_description",
    "lat",
    "lng",
    "referred",
}

HARD_FAILS: list[str] = []
WARNINGS: list[str] = []


def check(condition: bool, message: str, hard: bool = False) -> None:
    if condition:
        return
    (HARD_FAILS if hard else WARNINGS).append(message)


def load(name: str) -> pd.DataFrame | None:
    path = DATA_DIR / name
    if not path.exists():
        HARD_FAILS.append(f"{name}: missing — run 02-analysis/pull_data.py first")
        return None
    df = pd.read_csv(path, low_memory=False)
    print(f"{name}: {len(df):,} rows, {len(df.columns)} columns")
    return df


def verify_frame(name: str, df: pd.DataFrame) -> None:
    cols = set(df.columns)

    missing_req = REQUIRED_COLUMNS - cols
    check(not missing_req, f"{name}: missing required columns {sorted(missing_req)} "
          f"(schema drift — update column mapping)", hard=True)
    if missing_req:
        return

    missing_opt = OPTIONAL_COLUMNS - cols
    check(not missing_opt, f"{name}: missing optional columns {sorted(missing_opt)}")

    # --- ID integrity ---
    dupe_ids = df["service_request_id"].duplicated().sum()
    check(dupe_ids == 0, f"{name}: {dupe_ids:,} duplicated service_request_id values", hard=True)

    # --- Date sanity ---
    req = pd.to_datetime(df["date_requested"], errors="coerce")
    unparseable = req.isna().sum()
    check(unparseable / max(len(df), 1) < 0.01,
          f"{name}: {unparseable:,} unparseable date_requested values (>1%)", hard=True)
    check((req >= "2016-05-01").all() or bool(req.isna().any()),
          f"{name}: date_requested values before program launch (May 2016)")
    future = (req > pd.Timestamp.now()).sum()
    check(future == 0, f"{name}: {future:,} reports dated in the future")

    if "date_closed" in cols:
        closed = pd.to_datetime(df["date_closed"], errors="coerce")
        both = req.notna() & closed.notna()
        negative = (closed[both] < req[both]).sum()
        # closed-before-opened rows are excluded by the analysis; verify the
        # exclusion is small enough that it can't move the findings.
        check(negative / max(both.sum(), 1) < 0.005,
              f"{name}: {negative:,} rows closed before opened (>0.5%)")

    # --- Category / district plausibility ---
    n_categories = df["service_name"].nunique()
    check(5 <= n_categories <= 500,
          f"{name}: implausible service_name cardinality ({n_categories})")

    districts = pd.to_numeric(df["council_district"], errors="coerce")
    bad_districts = ((districts < 1) | (districts > 9)).sum()
    check(bad_districts == 0,
          f"{name}: {bad_districts:,} rows with council_district outside 1-9")

    null_district = df["council_district"].isna().mean()
    check(null_district < 0.10,
          f"{name}: {null_district:.1%} rows missing council_district")


def main() -> int:
    frames = {name: load(name) for name in ("closed_2025.csv", "open.csv")}

    for name, df in frames.items():
        if df is not None:
            verify_frame(name, df)

    # Cross-file: an open report should not also appear as closed.
    if frames["open.csv"] is not None and frames["closed_2025.csv"] is not None:
        overlap = set(frames["open.csv"]["service_request_id"]) & set(
            frames["closed_2025.csv"]["service_request_id"])
        check(len(overlap) == 0,
              f"{len(overlap):,} request IDs appear in both open and closed_2025")

    print()
    for w in WARNINGS:
        print(f"WARN  {w}")
    for f in HARD_FAILS:
        print(f"FAIL  {f}")

    if HARD_FAILS:
        print(f"\n{len(HARD_FAILS)} hard failure(s). Do not trust analysis output.")
        return 1
    print(f"\nOK — {len(WARNINGS)} warning(s), 0 hard failures. "
          "Warnings must be addressed in the memo's methodology notes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

