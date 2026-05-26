"""Get It Done operational analysis.

SQL runs via DuckDB directly against the CSVs — the queries below are the
actual analysis, not pseudocode. Python handles orchestration and output
formatting only.

Run after pull_data.py and verify_data.py:
    python 02-analysis/analysis.py
Writes findings tables to 02-analysis/output/ as markdown.

Methodology notes (mirrored in the decision memo):
- "Resolution days" = date_closed - date_requested, i.e. request-to-
  NOTIFICATION time. The dataset does not contain work-completion timestamps.
- Rows closed before opened (data errors) are excluded; verify_data.py bounds
  that exclusion at <0.5% of rows.
- Medians are used throughout. 311 durations are heavy-tailed; means reward
  nobody and mislead everybody.
"""

from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent / "output"
OUT.mkdir(exist_ok=True)

con = duckdb.connect()

con.execute(f"""
CREATE VIEW closed AS
SELECT *,
       -- date_closed truncates to midnight while date_requested keeps
       -- time-of-day, so same-day closures appear to close "before" they
       -- opened by a few hours (verify_data.py: 99.996% of the ~30% of
       -- rows this affects are same-day, median apparent gap ~10h). Floor
       -- the negative-but-same-day case at 0 instead of dropping the row —
       -- dropping it would silently remove the fastest resolutions from
       -- every median in this analysis, biasing all of them upward.
       GREATEST(0, date_diff('day', CAST(date_requested AS TIMESTAMP),
                                    CAST(date_closed   AS TIMESTAMP))) AS resolution_days
FROM read_csv_auto('{DATA}/closed_*.csv', union_by_name=true)
WHERE date_requested IS NOT NULL
  AND date_closed    IS NOT NULL
  -- only drop genuine multi-day inversions (data errors), not same-day
  -- truncation artifacts. verify_data.py confirms this is 4 rows.
  AND date_diff('day', CAST(date_closed AS TIMESTAMP),
                       CAST(date_requested AS TIMESTAMP)) <= 1;

CREATE VIEW open_reports AS
SELECT *,
       date_diff('day', CAST(date_requested AS TIMESTAMP), now()) AS age_days
FROM read_csv_auto('{DATA}/open.csv', union_by_name=true)
WHERE date_requested IS NOT NULL;
""")

QUERIES: dict[str, str] = {
    # Q1a — citywide baseline by category (top 15 by volume)
    "q1_category_baseline": """
        SELECT service_name,
               COUNT(*)                                        AS n_closed,
               MEDIAN(resolution_days)                         AS median_days,
               QUANTILE_CONT(resolution_days, 0.90)            AS p90_days
        FROM closed
        GROUP BY service_name
        ORDER BY n_closed DESC
        LIMIT 15
    """,
    # Q1b — district deviation from that category's citywide median.
    # A district can look slow simply because it gets slow categories;
    # comparing within category removes that excuse.
    "q1_district_vs_category": """
        WITH category_median AS (
            SELECT service_name, MEDIAN(resolution_days) AS city_median
            FROM closed GROUP BY service_name HAVING COUNT(*) >= 1000
        )
        SELECT c.council_district,
               c.service_name,
               COUNT(*)                          AS n,
               MEDIAN(c.resolution_days)         AS district_median,
               cm.city_median,
               MEDIAN(c.resolution_days) - cm.city_median AS gap_days
        FROM closed c
        JOIN category_median cm USING (service_name)
        WHERE c.council_district IS NOT NULL
        GROUP BY c.council_district, c.service_name, cm.city_median
        HAVING COUNT(*) >= 200
        ORDER BY gap_days DESC
        LIMIT 20
    """,
    # Q2 — intake waste: closures that produced no city work, by channel.
    # status has only two values (Closed/Referred) — "duplicate" is never a
    # status string, it's identified structurally via service_request_parent_id
    # (a non-null parent = this row is a child/duplicate of an existing report).
    # Waste = duplicate OR referred; both consume triage capacity without
    # producing city work.
    "q2_intake_waste_by_channel": """
        SELECT case_origin,
               COUNT(*) AS n_closed,
               100 * AVG(CASE WHEN service_request_parent_id IS NOT NULL
                          OR status = 'Referred'
                        THEN 1.0 ELSE 0.0 END)   AS waste_pct,
               SUM(CASE WHEN service_request_parent_id IS NOT NULL
                        THEN 1 ELSE 0 END)        AS n_duplicate,
               SUM(CASE WHEN status = 'Referred'
                        THEN 1 ELSE 0 END)        AS n_referred
        FROM closed
        GROUP BY case_origin
        HAVING COUNT(*) >= 100
        ORDER BY n_closed DESC
    """,
    # Q3 — backlog composition: is the open queue a few slow categories
    # (structural) or everything (capacity)?
    "q3_backlog_composition": """
        SELECT service_name,
               COUNT(*)                              AS n_open,
               MEDIAN(age_days)                      AS median_age_days,
               SUM(CASE WHEN age_days > 90  THEN 1 ELSE 0 END) AS over_90d,
               SUM(CASE WHEN age_days > 365 THEN 1 ELSE 0 END) AS over_1yr
        FROM open_reports
        GROUP BY service_name
        ORDER BY n_open DESC
        LIMIT 15
    """,
}


def main() -> None:
    for name, sql in QUERIES.items():
        df = con.execute(sql).df()
        path = OUT / f"{name}.md"
        path.write_text(df.to_markdown(index=False, floatfmt=".1f") + "\n")
        print(f"wrote {path.relative_to(ROOT)}  ({len(df)} rows)")

    print("\nNext: read the output tables, pick <=3 findings, write 03-decision-memo.md")


if __name__ == "__main__":
    main()

