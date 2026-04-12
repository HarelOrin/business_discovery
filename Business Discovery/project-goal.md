# Project Goal — Business Discovery

## What This Project Is

This project is about finding the right business for Harel to start. A scoring pipeline has already been built and run, producing a dataset of 3,606 business types — each evaluated across 12 founder-fit metrics. The work in this Claude Project is what comes next: analyzing that dataset, filtering and shortlisting candidates, researching specific businesses in depth, and ultimately making a go/no-go decision.

This is not about implementation or code. It is about discovery, analysis, and decision-making.

## The Question Being Answered

Which business category is the best fit for Harel's specific situation — his capital, location, skills, work style, and 5-10 year vision — and why?

## What the Dataset Contains

The scored dataset (`broad_pass_packet.json`) has 3,606 business types, each with:
- Scores 0-3 on 12 founder-fit metrics
- Per-metric reasoning with confidence labels (low / medium / high)
- An overall fit summary paragraph written by the AI
- Floor pass status (true/false)
- Non-floor average score (computed across 8 non-floor metrics)

**Scoring summary:**
- 1,044 business types pass all three floor gates (market headroom, margin quality, distribution efficiency all ≥ 2)
- ~756 pass the full shortlist threshold (floor pass + non-floor average ≥ 1.9)
- ~14 score ≥ 2.5 non-floor average (strongest candidates)

## What Happens in This Project

Chats in this project will cover:

- **Filtering and ranking** — slicing the scored dataset by metric combinations, thresholds, or specific founder priorities to surface the strongest candidates
- **Comparing clusters** — exploring how related business types compare against each other across the scoring dimensions
- **Deep dives** — researching specific business categories in detail: market size, competition, pricing, operating model, what it actually takes to start and run
- **Stress-testing** — challenging high-scoring candidates with counterarguments, realistic operating scenarios, and founder-fit friction
- **Manual review** — Harel's personal checks: energy/motivation fit, competitor review, customer accessibility, regulatory flags
- **Decision-making** — working toward a final ranked shortlist with written go/no-go rationale

## The End Goal

A clear, confident decision: one (or a small number of) business category or categories that Harel will actually pursue, with documented reasoning for why.
