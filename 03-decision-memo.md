# Decision Memo — Get It Done Service Request Operations

**To:** Director of Neighborhood Services (simulated stakeholder)
**From:** Sezgi Ozren, Business Analyst
**Date:** July 2026
**Re:** The sidewalk-repair backlog is misclassified, not just slow

## Situation

San Diego's Get It Done program closed 378,669 service requests in 2025. Using
that full-year record plus the current open backlog, this memo identifies where
resolution time diverges and recommends one change. The headline is not that a
few categories are slow — it is that the slowest ones are structurally different
work being run through a queue built for something else.

Two scope notes. The dataset records when a resident was *notified* a case was
addressed, not when work was performed, so findings describe resident-experienced
responsiveness. The resolution-time metric here was validated against the city's
own `case_age_days` field and matches it exactly across all 378,669 records.

## Findings

### 1. "Resolution time" is two different kinds of work wearing one label

Consumable requests close almost immediately — illegal dumping and graffiti have
a median resolution of 0 days (70% and 57% close same-day), missed collection one
day. Infrastructure requests run to months or years — street light maintenance
has a median of 166 days. These are not slow versions of the same process; they
are capital and maintenance work sharing an intake and a status vocabulary with
same-day cleanup. A single program-wide target is therefore meaningless.

### 2. The sidewalk-repair delay is real, concentrated, and not a small-sample fluke

Sidewalk repair has a 37-day citywide median but collapses by district: District
2 runs 506 days (median, n=983), District 7 runs 666 days (n=507). These are the
two highest-volume districts for the category *and* the two slowest — the pattern
that rules out a small-sample artifact. Whatever is happening to sidewalk repair
is worst exactly where demand is highest.

### 3. The backlog is structural, and its status label is misleading residents

The open backlog is not a general capacity shortfall; it is four infrastructure
categories that functionally never drain. Sidewalk repair has 14,786 open
requests at a median age of 1,091 days — three years — with 82% over a year old.
Pavement maintenance sits at a 1,272-day median open age. Meanwhile parking and
encampment requests clear in a median of 12–21 days. Every one of those aged
sidewalk requests is labeled "open," implying pending action that, in practice,
is years away. That gap between the implied and the real is the program's
clearest trust liability — and it generates its own duplicate reports, as
residents re-file issues they reasonably assume were dropped.

## Recommendation

**Split the four structural infrastructure categories out of the standard 311
flow into a capital-assessment track with honest status language and
district-level capacity targets — starting with sidewalk repair in Districts 2
and 7.**

This is deliberately *not* "triage the sidewalk queue harder." Triage reorders a
queue; it does not pour concrete, and a 1,091-day backlog is a funding-and-crew
constraint that no amount of prioritization dissolves. The fixable harm is the
misrepresentation: a report queued for multi-year capital work should say so
("assessed — queued for capital planning"), not sit under an "open" label that
implies imminent action. Alongside that, the genuinely schedulable share of the
work gets explicit district capacity targets where the disparity is worst (D2,
D7), so the reclassification is paired with a measurable service commitment
rather than just a relabel.

## Tradeoffs and Risks

- **Comms/political optics (the real cost):** honest status means telling a
  resident the city will not fix their sidewalk soon. That is politically harder
  than an "open" ticket that quietly does nothing. This recommendation trades a
  comfortable ambiguity for an uncomfortable truth, and leadership has to want
  that trade.
- **It does not create budget.** The backlog needs capital funding this memo
  cannot conjure; the process change makes the constraint *visible and honest*,
  not gone. Naming that plainly is the point, not a weakness to hide.
- **Equity of targeting D2/D7:** singling out two districts invites "why these
  two." The answer must stay data-anchored (highest volume *and* slowest, per
  Finding 2), and post-change monitoring must confirm the fix narrows the gap
  rather than shifting it to a third district.
- **Urgent-within-slow risk:** a genuine sidewalk hazard must not be buried by an
  honest-but-slow default; the track needs a hazard-escalation path.

## What I'd Validate Next

- Confirm sidewalk repair is capital-funded vs. operations-and-maintenance. The
  entire reframe hinges on this; if it is actually under-resourced O&M, the
  recommendation changes shape.
- Pull crew and budget allocation by district to confirm D2/D7 slowness is
  capacity, not category mix — the analysis already controls for category by
  comparing sidewalk repair against its own citywide median.
- Track duplicate re-reporting of infrastructure issues before and after the
  status-language change, as a direct measure of whether honesty reduces the
  re-filing that inflates intake.

---
*Methodology, queries, and data-quality checks: see `02-analysis/` and
`scripts/verify_data.py`. All figures reproduce against the 2025 data snapshot;
the resolution-time metric matches the city's published `case_age_days` field
exactly.*

