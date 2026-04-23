# Problem Framing — Get It Done Service Request Operations

**Engagement type:** Self-initiated analysis of public operational data
**Analyst:** Sezgi Ozren
**Data:** City of San Diego Get It Done (311) reports, Open Data Portal (PDDL license)
**Date:** July 2026

## Background

Get It Done is San Diego's 311 intake system: residents report non-emergency
problems (potholes, graffiti, illegal dumping, parking violations, etc.) via
mobile app, web, or phone. Every report since the program's May 2016 launch is
published on the city's open data portal.

The city publishes the data with known caveats: duplicate reports, reports
outside city jurisdiction, unverifiable reports, and reports referred outside
the Get It Done system. Closure timestamps reflect when the reporter was
*notified* a case was addressed — not when work was performed. All findings in
this analysis are scoped accordingly.

## Stakeholders (simulated for this engagement)

| Stakeholder | Interest | What they need from analysis |
|---|---|---|
| Director of Neighborhood Services (primary audience) | Resource allocation across service categories and districts | A defensible recommendation, with tradeoffs stated |
| 311 / Get It Done Program Manager | Intake quality, duplicate rate, channel mix | Data-quality findings that map to process changes |
| Council District offices | Equity of response times across districts | Transparent per-district comparison with honest caveats |
| Performance & Analytics Dept. (data owner) | Correct use of published data | Methodology that respects documented data limitations |

## Business Questions

1. **Where does resolution time diverge most?** By service category and council
   district — which combinations are outliers relative to citywide medians, and
   is the divergence explained by volume, category mix, or something else?
2. **What share of intake is waste?** Duplicates, out-of-jurisdiction reports,
   and referrals consume triage capacity without producing city work. How big
   is that share, and does it vary by intake channel (app vs. web vs. phone)?
3. **What does the open backlog look like?** Age distribution and composition
   of currently open reports — is the backlog structural (a few slow
   categories) or general?

## Out of Scope

- Anything requiring work-order data (actual repair timing, cost, crew data) —
  not in the published dataset.
- Demographic overlays. Doable with census joins, but out of scope for v1; the
  decision memo notes it as a validation step.
- Predictive modeling. This is an operational analysis, not a forecasting
  exercise.

## Success Criteria for the Analysis

- Every finding survives the caveats the city itself documents (notified-vs-
  fixed, duplicates, referrals).
- At most three findings, each of which would plausibly change a resource or
  process decision.
- One recommendation, with named costs — not just benefits.
- All numbers reproducible from `02-analysis/` against a pinned data snapshot,
  validated by `scripts/verify_data.py`.

