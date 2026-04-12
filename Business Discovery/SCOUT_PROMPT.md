# Business Scout — Continuation Prompt

Use this prompt in a **new Cowork session** to continue iterating on the app or to do deep-dives after reviewing.

---

## Prompt: Export & Deep-Dive Session

```
I've been using Business Scout (business_scout.html) to review 574 shortlisted businesses from my scored dataset.
The app saves progress to localStorage and exports approved businesses as JSON.

I now have an approved list and want to do deep-dives.

The workspace folder contains:
- business_scout.html — the Tinder-style reviewer app (self-contained, no server needed)
- shortlist.json — 574 filtered businesses (passes floor + non_floor_avg >= 1.9), sorted by score desc
- broad_pass_packet.json — original full dataset (3,606 records)

Each business record has:
  id, name, definition, archetype, customer_type, revenue_model,
  summary, reasoning, metrics (12 scores 0-3 each with reasoning),
  non_floor_avg, reg_drag, auto_approve

Scoring framework:
- Floor gates (all must be >= 2): market_headroom, margin_quality, distribution_efficiency
- Shortlist threshold: non_floor_avg >= 1.9 (8 non-floor metrics, excl. reg_drag)
- Auto-approve: non_floor_avg >= 2.5
- regulatory_liability_drag: informational only, not in average

My context:
- First-time founder, Jerusalem-based, ~$40K capital
- Goals: high margins, no/few employees, low capex, fast first revenue
- 5-10yr horizon: self-running, step back to part-time
- Jerusalem geography matters — remote/global delivery is a plus

[TASK: describe what you want — e.g. "deep-dive on [business name]", 
 "show me all approved businesses sorted by owner_independence score",
 "compare my top 5 approved businesses side by side",
 "add a Notes field to the app so I can annotate each card"]
```

---

## Prompt: App Improvements

```
I have a standalone HTML app (business_scout.html) in my Business Discovery workspace folder.
It's a Tinder-style business reviewer — shows 574 businesses one at a time, lets me Keep/Discard,
saves all decisions to localStorage, and exports approved businesses as JSON.

The app is self-contained (data embedded, no server needed — just open in Chrome).

Current features:
- Queue tab: card with name, score badge, archetype/customer/revenue tags, reg drag pill, summary
- Expand: shows full reasoning + 12 metric scores with dot indicators and reasoning text
- Actions: ← Discard | → Keep | ↑ Back (also keyboard shortcuts: arrow keys)
- Approved tab: list newest-first, with remove + export JSON button
- Discarded tab: list newest-first, with restore-to-queue button
- Progress bar: X of 574 reviewed

Please [describe the improvement you want, e.g.:
- "add a notes/annotation field per business that also saves to localStorage"
- "add a filter by archetype to the queue"
- "add a 'Maybe' pile in addition to Keep/Discard"
- "make the metrics grid sortable by score"
- "add a search bar to the approved/denied lists"]
```

---

## Quick reference: metric keys

| Key | Type | Description |
|-----|------|-------------|
| market_headroom | Floor | Total addressable demand |
| margin_quality | Floor | Gross margin potential |
| distribution_efficiency | Floor | How easy/cheap to reach customers |
| startup_capital_intensity | T2 | How little capital needed to start |
| speed_to_first_revenue | T2 | How fast first $ arrives |
| team_model_fit | T2 | Solo/small team viability |
| recurring_revenue_potential | T2 | Subscription / repeat potential |
| owner_independence_potential | T2 | Can founder step back eventually |
| demand_urgency | T3 | Customers feel urgency to buy |
| non_commodity_differentiation | T3 | Can you avoid racing to the bottom |
| ai_automation_leverage | T3 | Can AI/software reduce ops costs |
| regulatory_liability_drag | Info | Regulatory risk (not in avg) |
