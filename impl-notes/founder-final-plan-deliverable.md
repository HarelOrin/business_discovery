# Founder Final Plan Deliverable

## Purpose

Plain-language summary of the complete discovery system plan so the founder can make final directional decisions without technical clutter.

## Canonical Companion

Use together with:

- `handoffs/execution-plan-overview.md`

---

## Mission

Build a system that discovers business opportunities matching the founder's thesis, scores them objectively, shortlists the strongest candidates, and produces deep-research briefs — so the founder can make a confident final selection.

## Founder Thesis (What We're Scoring Against)

- massive potential customer pool with room to scale despite incumbents
- prefer no employees or a small team of skilled professionals
- high-margin offerings over low-margin commodity dynamics
- boring/crowded categories are acceptable when economics are strong
- avoid dependence on off-the-shelf product selling
- low starting investment and speed-to-scale are explicit fit dimensions

## How It Works (Stage-By-Stage)

### Stage 1 — Metric Design (Complete)

Defined 13 scoring metrics (market headroom, margin quality, distribution efficiency, capital intensity, speed to revenue, team model fit, operational complexity, demand urgency, recurring revenue, revenue fragmentation, regulatory drag, differentiation, AI leverage). Each metric is scored 0-3 with short reasoning and confidence.

### Stage 2 — Broad AI Scoring

Every business in the dataset gets scored by AI against all 13 metrics using world-knowledge (no deep external research at this stage). Output per business: all scores, per-metric reasoning, overall fit summary, and a floor-pass flag.

### Stage 3 — Shortlist Gating

Two-part filter:
- **Floor rules**: market headroom, margin quality, and distribution efficiency must each score >= 2 (Solid)
- **Average threshold**: non-floor metrics must average >= 1.9

Candidates passing both are shortlisted. Those with non-floor average >= 2.5 are auto-approved for deep research. Those between 1.9 and 2.5 go to a manual approval queue for the founder to decide.

### Stage 4 — Deep Research

For every approved shortlist candidate, the system generates a deep-research brief covering 8 dimensions: market landscape, competitive intel, unit economics, regulatory scan, operating model, thesis stress test, speed to revenue, and risk scan. AI produces this using deeper prompting, not web search.

### Stage 5 — Founder Decision

After receiving automated deep-research briefs, the founder performs:
1. **Personal energy check** — quick gut-reaction filter
2. **Competitor review** — 15-30 min per candidate checking real products/pricing
3. **Customer accessibility probe** — can you reach 10 prospects in 2 weeks?
4. **Regulatory verification** — 15-20 min for flagged candidates
5. **Final go/no-go ranking** — written rationale for top choices

Budget: ~1-2 hours manual time per candidate.

## What Is Automated vs Manual

| Automated | Manual (Founder) |
|---|---|
| Data intake from NAICS + G2 | Borderline candidate approvals (1.9-2.5 range) |
| Dataset normalization and deduplication | Personal energy check on shortlist |
| AI scoring of all 700+ candidates | Competitor review for survivors |
| Floor and threshold gating | Customer accessibility probe |
| Deep-research brief generation | Regulatory spot-checks |
| | Final go/no-go ranking |

## Data Source

One-time dataset from two locked sources:
- **NAICS** — broad economic taxonomy (~industry classification backbone)
- **G2 category hierarchy** — modern software/service categories

Target: 700+ unique canonical business types after deduplication.

## Known Risks and Mitigations

- **AI scoring inconsistency** — mitigated by fixed output schema, validation, and rerun/escalation queue
- **Hidden deduplication errors** — mitigated by three-tier dedupe (exact, alias, similarity-review) with merge logs
- **Irrelevant categories in dataset** — the scorer will naturally give low scores; floor rules filter them out
- **Deep-research surface depth** — mitigated by structured counterargument requirements and calibrated confidence labels

## What Is Approved

- full metric set and scoring format
- floor rules and shortlist thresholds
- dataset sources and volume target
- deep-research scope and quality gates
- execution order and phase gating
- manual vs automated work split

## What Remains Optional

- specific AI model brand selection (balanced vs stronger tier is locked; exact provider is implementation choice)
- minor threshold tuning after first real scoring run
- dataset expansion beyond the two locked sources (deferred to future runs)

## Final Founder Decision Required

Authorize execution kickoff starting with `source-puller` phase, running through the strict plan → write → run → verify → advance protocol for each phase.

---

*This deliverable is self-contained. Implementation agents use the separate technical handoff package.*
