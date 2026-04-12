# Status and Progress — Business Discovery

*Last updated: April 2026*

## Where Things Stand

The scoring pipeline is complete. A dataset of 3,606 business types has been evaluated across 12 founder-fit metrics using the o3 reasoning model. The dataset is ready for analysis and filtering.

**The discovery and decision phase has not formally started yet.**

---

## What's Already Done

### The Scored Dataset

`broad_pass_packet.json` — 3,606 business types, each with:
- Scores 0-3 on all 12 metrics
- Per-metric reasoning and confidence (low / medium / high)
- Overall fit summary paragraph
- `passes_floor` boolean
- `non_floor_average` float (8-metric average, excluding informational regulatory metric)

**High-level results:**
| Filter | Count |
|---|---|
| Total business types scored | 3,606 |
| Pass all 3 floor gates (≥ 2 each) | 1,044 |
| Pass floor + non-floor avg ≥ 1.9 (shortlist threshold) | ~756 |
| Non-floor avg ≥ 2.5 (strongest candidates) | ~14 |
| Mean non-floor average across all records | 1.40 |

### The Scoring Framework

12 metrics, locked. Tiers:
- **Floor (must score ≥ 2):** market_headroom, margin_quality, distribution_efficiency
- **Tier 2 (high priority, in average):** startup_capital_intensity, speed_to_first_revenue, team_model_fit, recurring_revenue_potential, owner_independence_potential
- **Tier 3 (signal, in average):** demand_urgency, non_commodity_differentiation, ai_automation_leverage
- **Informational (not in average):** regulatory_liability_drag

### What the Pipeline Built (For Reference)

The technical pipeline that produced this dataset lives in the `business_discovery` repo and is separate from this project. Phases 1-3 are complete (Source Puller, Dataset Shaper, AI Scorer). Phases 4-5 (Gate Keeper, Research Runner) are not yet built, but their output can be approximated manually or in chat — the data is all there.

---

## What Comes Next

The discovery work is open-ended and will happen across multiple chats. The rough sequence:

**1. Initial filtering and shortlisting**
Use the scored data to identify the strongest candidates — by metric thresholds, business type clusters, and founder-fit intuition. The ~756 businesses that clear the shortlist threshold are the starting pool.

**2. Manual review (Harel-led)**
Personal energy / fit check - does Harel see himself doing this business based on description of fit

**3. Deep dives on promising candidates**
Pick the most interesting candidates and research them properly: market size, real competitors, pricing/margins, operating model, Israel-specific considerations, path to first revenue.

**4. Stress-testing**
For any business that looks strong, run a serious counterargument pass. What's the realistic failure mode? What would the thesis stress test say? competitor review

**6. Final go/no-go ranking**
A written rationale for the top choices, ordered by conviction. This is the output that leads to actually starting something.

---

## Open Questions

These are the key unknowns that the discovery phase needs to resolve:

- Which business categories actually look attractive once you go past the scores into real-world operating realities?
- Which ones are genuinely accessible from Jerusalem — either via remote delivery or local market demand?
- Which ones are realistic on ~$40K starting capital in the first 12 months?
- Which ones have a plausible path to the 5-10 year self-running goal?
- Which one does Harel actually want to work on?
