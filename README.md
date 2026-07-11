# San Diego Get It Done — 311 Operations Analysis

A business-analysis engagement on real municipal data: San Diego's 311 service
requests (Get It Done program, 12-month window: 2025 closed reports + current
open backlog). Not a dashboard — a decision.

**Deliverables:** [Problem framing](01-problem-framing.md) · [Decision memo](03-decision-memo.md) · [Requirements (lite BRD)](04-requirements.md) · [Analysis (SQL + Python)](02-analysis/)

**Stack:** Python · DuckDB / SQL (analysis) · Claude + Copilot (AI-assisted)

**The call:** [the decision memo](03-decision-memo.md) recommends that the four
structural infrastructure categories be split out of the standard 311 flow into
a capital-assessment track with honest status language and district capacity
targets (starting sidewalk repair, Districts 2 and 7), with tradeoffs.
[Requirements](04-requirements.md) specs the recommended change,
with user stories and acceptance criteria.

## Findings

| # | Finding | So what |
|---|---|---|
| 1 | Sidewalk repairs in District 2 take 506 days (median) vs. a 37-day citywide median; District 7 takes 666 days | Two districts carrying the highest volume are also the slowest — not a small-sample fluke |
| 2 | 25.8% of Mobile-app intake and 16.9% of Web intake are duplicates or referrals that produce no city work | Self-service channels have no way to tell a resident "already reported" before they submit |
| 3 | Sidewalk backlog has a 1,091-day median age; 82% of open sidewalk tickets are over a year old | The backlog is structural (4 infrastructure categories), not a general capacity problem |

**Recommendation:** Split the four structural infrastructure categories out of
the standard 311 flow into a capital-assessment track with honest status
language and district capacity targets — starting with sidewalk repair in
Districts 2 and 7. Not "triage harder": the fix is ending the misleading "open"
label on multi-year work, paired with a measurable service commitment where the
disparity is worst.

## What's in this repo

| Artifact | What it shows |
|---|---|
| [01-problem-framing.md](01-problem-framing.md) | Stakeholders, business questions, scope, success criteria |
| [02-analysis/](02-analysis/) | SQL (DuckDB) + Python. Queries are the analysis, not decoration |
| [03-decision-memo.md](03-decision-memo.md) | 1-2 page exec memo: findings → recommendation → tradeoffs |
| [04-requirements.md](04-requirements.md) | Lite BRD for the recommended change: as-is/to-be, user stories, acceptance criteria, edge cases |
| [scripts/verify_data.py](scripts/verify_data.py) | Data validation gate — analysis output is untrusted until this passes |

## A note on how this was built

**This is a self-directed analysis on public data.** It was not commissioned by
the City of San Diego or any employer. The stakeholder in the decision memo
(Director of Neighborhood Services) is illustrative — it defines who the memo
is *written for*, not a real engagement. The data, the timestamp-artifact
investigation, and the findings are real; the city has not reviewed or acted
on any of this.

## Reproduce

```bash
pip install -r requirements.txt
python 02-analysis/pull_data.py      # downloads 2 files (closed 2025, open) from data.sandiego.gov
python scripts/verify_data.py        # hard-fails on schema drift / ID dupes / date garbage
python 02-analysis/analysis.py       # writes findings tables to 02-analysis/output/
```

## Methodology notes

- **~30% of closed_2025 rows have `date_closed` earlier than `date_requested`.**
  Investigated, not just excluded: 99.996% of these are a same-day timestamp
  precision artifact (`date_closed` truncates to midnight while
  `date_requested` keeps time-of-day — median apparent gap is 10 hours, same
  calendar day). Only 4 of 111,985 rows show a genuine multi-day inversion.
  `analysis.py` floors the same-day case at 0 days instead of dropping it —
  dropping all ~112K rows would have silently removed the fastest
  resolutions from every median, biasing results upward. Only the 4 genuine
  multi-day inversions are excluded.
- **Resolution time = request-to-notification.** The city's dataset records
  when the reporter was notified, not when work was completed. Every claim in
  the memo is scoped to resident-experienced responsiveness.
- **Medians, not means.** 311 durations are heavy-tailed.
- **Within-category district comparison.** A district isn't "slow" if it just
  receives slower categories; district gaps are measured against each
  category's citywide median.
- **Known data caveats** (duplicates, out-of-jurisdiction reports, referrals)
  are treated as a finding, not noise — they're the triage-capacity story.

Data: [City of San Diego Open Data Portal](https://data.sandiego.gov/datasets/get-it-done-311/),
PDDL license.

