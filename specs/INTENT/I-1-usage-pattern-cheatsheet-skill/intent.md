---
id: I-1
title: Usage-pattern cheatsheet skill
slug: usage-pattern-cheatsheet-skill
status: complete
opened: 2026-06-05
closed: 2026-06-05
superseded_by: null
verdict_outcomes_passed: 6
verdict_outcomes_passed_by_test: 0
verdict_outcomes_total: 6
verdict_checked_at: 2026-06-05T18:26:29Z
---

# Intent: Usage-pattern cheatsheet skill

- **Author:** Jason Lo
- **Last updated:** 2026-06-05

## Problem
Across my own GitHub repositories I keep reusing how I first learned a library or API, so obsolete patterns and misconceptions persist long after the official guidance has moved on. I have no quick way to see, for a given topic, how my code actually uses it today versus what current best practice says — and where the gap is conceptual, not just syntactic.

## Outcome
- **WHEN** invoked with a use case and an explicit target **THE SYSTEM SHALL** resolve the authenticated GitHub user via the `gh` CLI and collect, from that user's repositories, the files relevant to the target before analyzing.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/mines-own-repos-via-gh.md]
- **WHEN** relevant files have been collected **THE SYSTEM SHALL** establish current best practice from context7 documentation (falling back to web search when context7 lacks the target) and classify each observed usage as current or obsolete.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/grounds-in-current-docs.md]
- **WHEN** analysis completes **THE SYSTEM SHALL** write one markdown cheatsheet containing a minimal current reference code snippet reflecting present-day idiomatic usage of the target, a "Typical usage patterns" section, and a "Learnings" section that names each obsolete pattern or misconception found alongside its current replacement.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/cheatsheet-has-required-sections.md]
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/has-reference-snippet.md]
- **WHILE** writing every section **THE SYSTEM SHALL** keep content in concise point form, including explanatory detail only when it is a future-use must-know/tip or aids learning, and omitting incidental detail.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/concise-point-form.md]
- **WHILE** writing the Learnings section **THE SYSTEM SHALL** frame every correction at the level of concept and intent rather than syntax or API signatures.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/conceptual-altitude-not-syntax.md]
- **WHEN** a cheatsheet file is written **THE SYSTEM SHALL** add an entry for it to the repository-root index.md.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/registers-in-index.md]

## Non-Goals
- A syntax/API quick-reference — altitude is conceptual usage and intent, not signatures.
- Editing, refactoring, or auto-fixing the analyzed source code.
- Analyzing repositories belonging to other users or upstream library authors.
- Producing exhaustive documentation; the cheatsheet is a curated, opinionated digest.
- A scored "correctness" audit or CI gate over the user's repos.

## Constraints
- GitHub data is accessed only via the `gh` CLI (P-5); no direct REST/GraphQL or SDK.
- The skill is a prompted agent workflow (P-6); any deterministic helper is a self-contained `uv` script with PEP 723 metadata (P-1/P-2).
- Cheatsheets are markdown files registered in the repository-root `index.md` (P-4).
- Favor the simplest workflow that produces a useful cheatsheet (P-3).

## Change Log
- **2026-06-05** — Initial draft.
- **2026-06-05** — Added a required current reference code snippet to the cheatsheet, and a concise-point-form invariant that filters detail to future-use must-knows/tips or learning value. Reason: make cheatsheets quicker to scan and ground a "what does it look like today" snippet in current practice.
