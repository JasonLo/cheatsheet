---
id: I-1
title: Usage-pattern cheatsheet skill
slug: usage-pattern-cheatsheet-skill
status: complete
opened: 2026-06-05
closed: 2026-06-05
superseded_by: null
verdict_outcomes_passed: 9
verdict_outcomes_passed_by_test: 0
verdict_outcomes_total: 9
verdict_checked_at: 2026-06-05T19:50:00Z
---

# Intent: Usage-pattern cheatsheet skill

- **Author:** Jason Lo
- **Last updated:** 2026-06-05 (refined — top-3 cap on usage/learnings)

## Problem
Across my own GitHub repositories I keep reusing how I first learned a library or API, so obsolete patterns and misconceptions persist long after the official guidance has moved on. I have no quick way to see, for a given topic, how my code actually uses it today versus what current best practice says — and where the gap is conceptual, not just syntactic. The digest is also written only for human scanning, so a coding agent (e.g. Claude Code) working in those repos can't directly apply its corrections as rules.

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
- **WHILE** writing the "Typical usage patterns" and "Learnings" sections **THE SYSTEM SHALL** include only the 3 highest-value points in each section, adding a 4th or further point only when it carries strong justification.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/top-three-value-points.md]
- **WHILE** writing the Learnings section **THE SYSTEM SHALL** frame every correction at the level of concept and intent rather than syntax or API signatures.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/conceptual-altitude-not-syntax.md]
- **WHEN** writing the cheatsheet **THE SYSTEM SHALL** include an "Agent rules" section stating each must-follow guardrail as an imperative ALWAYS/NEVER directive in point form, so a coding agent (e.g. Claude Code) can apply the corrections directly without rereading the prose.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/agent-actionable-rules.md]
- **WHEN** a cheatsheet file is written **THE SYSTEM SHALL** add an entry for it to the repository-root index.md.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/registers-in-index.md]
- **WHILE** writing the cheatsheet **THE SYSTEM SHALL** exclude the name, owner/repo slug, URL, and verbatim code or content of any private repository — citing and quoting only public sources, and conveying patterns learned from private repositories in redacted, generalized form (Constitution P-7).
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/no-private-repo-leak.md]

## Non-Goals
- A syntax/API quick-reference — altitude is conceptual usage and intent, not signatures.
- Editing, refactoring, or auto-fixing the analyzed source code.
- Analyzing repositories belonging to other users or upstream library authors.
- Producing exhaustive documentation; the cheatsheet is a curated, opinionated digest.
- A scored "correctness" audit or CI gate over the user's repos.
- Machine-parseable agent metadata (heavy YAML frontmatter, tags, schemas) — not load-bearing for plain markdown in Claude Code; the agent signal comes from structure and imperative rules, not metadata.
- Auto-wiring cheatsheets into a consuming repo's context (CLAUDE.md `@`-imports, agent config) — the skill writes one self-contained, agent-actionable file; how a repo loads it is the user's call.

## Constraints
- GitHub data is accessed only via the `gh` CLI (P-5); no direct REST/GraphQL or SDK.
- The skill is a prompted agent workflow (P-6); any deterministic helper is a self-contained `uv` script with PEP 723 metadata (P-1/P-2).
- Cheatsheets are markdown files registered in the repository-root `index.md` (P-4).
- Favor the simplest workflow that produces a useful cheatsheet (P-3).
- Agent-directed content lives inside the same single markdown cheatsheet — no separate machine-readable artifact per topic (P-3/P-4).
- No private repository may be disclosed or reproduced in the cheatsheet (P-7); repo visibility is resolved via `gh` and only public sources are cited or quoted.

## Change Log
- **2026-06-05** — Initial draft.
- **2026-06-05** — Added a required current reference code snippet to the cheatsheet, and a concise-point-form invariant that filters detail to future-use must-knows/tips or learning value. Reason: make cheatsheets quicker to scan and ground a "what does it look like today" snippet in current practice.
- **2026-06-05** — Made cheatsheets AI-agent-friendly: added an outcome requiring an "Agent rules" section of imperative ALWAYS/NEVER point-form guardrails (Claude Code research shows imperative rules are load-bearing, frontmatter is not), plus non-goals excluding cargo-cult metadata and auto-wiring into consuming repos. Reason: let a coding agent apply a cheatsheet's corrections directly, not just a human scanning it.
- **2026-06-05** — Added a no-private-repo-leak outcome and constraint: the cheatsheet must exclude any private repo's name/slug/URL and verbatim content, citing only public sources. Reason: enforce Constitution P-7 at the feature level after the principle was ratified.
- **2026-06-05** — Added a top-3 invariant: the "Typical usage patterns" and "Learnings" sections each carry only the 3 highest-value points, with a strong-justification exception for going beyond. Reason: force ruthless curation so the highest-leverage points aren't diluted by marginal ones.
