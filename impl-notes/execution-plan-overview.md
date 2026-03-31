# High-Level Execution Plan

## Outcome

A functioning discovery pipeline that goes from raw category sources to shortlist and deep-research packets, with auditable decision logs.

## What Gets Built

1. source intake and canonical dataset creation
2. AI scoring and shortlist gating
3. deep-research packet generation for approved candidates

## What Founder Reviews

- shortlist outputs
- manual approval queue for borderline candidates
- deep-research packets
- final ranked "go/no-go" candidate decisions

## Manual vs Automated (Operationally)

- automated:
  - intake processing
  - canonical shaping
  - broad-pass scoring
  - threshold gating
  - deep-research packet generation
- manual (founder):
  - borderline candidate approvals (non-floor average < 2.5)
  - personal energy check on shortlisted candidates
  - competitor review (15-30 min per candidate)
  - customer accessibility probe
  - regulatory verification for flagged candidates
  - final go/no-go ranking with written rationale

## Build Phases

1. source-puller
2. dataset-shaper
3. ai-scorer
4. gate-keeper
5. research-runner

## Completion Definition

Execution package is complete when:

- each phase has a verified pass package
- gates behave exactly per locked rules
- deep-research packets are generated for approved candidates
