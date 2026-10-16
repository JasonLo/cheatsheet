---
id: I-1
title: Usage-pattern cheatsheet skill
slug: usage-pattern-cheatsheet-skill
status: complete
opened: 2026-06-05
closed: 2026-10-15
superseded_by: null
verdict_outcomes_passed: 10
verdict_outcomes_passed_by_test: 3
verdict_outcomes_total: 10
verdict_checked_at: 2026-10-16T03:50:53Z
---

# Intent: Usage-pattern cheatsheet skill

- **Author:** Jason Lo
- **Last updated:** 2026-10-15 (refined — STE rewrite, STE outcome, and pytest citations for O-4, O-9, and O-10)

## Problem
I use the same patterns that I first learned for a library or an API in many of my GitHub repositories. The official guidance changes, but my old patterns and errors stay in my code. I have no fast method to compare how my code uses a topic with the current best practice. Often the difference is in the concept, not in the syntax. Also, the summary is for humans only. A coding agent, for example Claude Code, cannot apply its corrections as rules.

## Outcome
- **WHEN** the skill starts with a target **THE SYSTEM SHALL** use the `gh` CLI to get the target files from the user's GitHub repositories. The input is a use case and a target. The skill gets the files before the analysis.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/mines-own-repos-via-gh.md]
- **WHEN** the skill has the files **THE SYSTEM SHALL** find the current best practice for the target in context7 documentation. If context7 has no data for the target, the skill uses a web search. Then the skill marks each usage as current or not current.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/grounds-in-current-docs.md]
- **WHEN** the analysis is complete **THE SYSTEM SHALL** write one markdown cheatsheet with three parts. The first part is a short code snippet that shows the current correct usage of the target. The second part is a "Typical usage patterns" section. The third part is a "Learnings" section. This section gives each old pattern or error and its current replacement.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/cheatsheet-has-required-sections.md]
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/has-reference-snippet.md]
- **WHILE** the skill writes a section **THE SYSTEM SHALL** use short points. A point gives an explanation only if it is an important tip for the future or helps the user learn. The skill removes all other detail.
  - [test: pytest:tests/test_cheatsheet_form.py::test_cheatsheet_point_form]
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/concise-point-form.md]
- **WHILE** the skill writes the "Typical usage patterns" and "Learnings" sections **THE SYSTEM SHALL** put only the 3 most important points in each section. The skill adds a fourth point only for a strong reason.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/top-three-value-points.md]
- **WHILE** the skill writes the "Learnings" section **THE SYSTEM SHALL** write each correction at the level of concept and intent. The skill does not write corrections about syntax or API signatures.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/conceptual-altitude-not-syntax.md]
- **WHEN** the skill writes the cheatsheet **THE SYSTEM SHALL** add an "Agent rules" section. Each rule in this section is one ALWAYS or NEVER instruction in point form. Then a coding agent, for example Claude Code, can apply the corrections directly.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/agent-actionable-rules.md]
- **WHEN** the skill writes a cheatsheet file **THE SYSTEM SHALL** add an entry for that file to the `index.md` file in the repository root.
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/registers-in-index.md]
- **WHILE** the skill writes the cheatsheet **THE SYSTEM SHALL** not show the name, slug, URL, code, or text of a private repository (Constitution P-7). The skill cites and quotes only public sources. It gives patterns from private repositories only in a general form without identifiers.
  - [test: pytest:tests/test_no_private_repo_leak.py::test_cited_repos_are_public]
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/no-private-repo-leak.md]
- **WHEN** the skill writes a cheatsheet **THE SYSTEM SHALL** write all prose in ASD-STE100 Simplified Technical English (Constitution P-8). Code, commands, identifiers, file paths, URLs, and quoted tool output are exempt.
  - [test: pytest:tests/test_ste_prose.py::test_cheatsheet_sentence_length]
  - [test: pytest:tests/test_ste_prose.py::test_cheatsheet_approved_words]
  - [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/prose-in-ste.md]

## Non-Goals
- A quick reference for syntax or API signatures. The cheatsheet is about concepts and intent.
- Changes to the analyzed source code, for example edits, refactors, or automatic fixes.
- Analysis of repositories that other users or library authors own.
- Complete documentation. The cheatsheet is a short summary with selected content.
- A score for correctness, or a CI gate on my repositories.
- Agent metadata that a machine can parse, for example large YAML frontmatter, tags, or schemas. Claude Code does not need this metadata for plain markdown. The agent gets its information from the structure and the instructions.
- Automatic connection of cheatsheets to the context of a different repository, for example CLAUDE.md `@` imports or agent configuration. The skill writes one cheatsheet file. The user decides how a repository loads it.

## Constraints
- The skill gets GitHub data only with the `gh` CLI (P-5). It does not use the REST API, the GraphQL API, or an SDK directly.
- The skill is a prompted agent workflow (P-6). Each deterministic helper is a self-contained `uv` script with PEP 723 metadata (P-1, P-2).
- Each cheatsheet is a markdown file. The `index.md` file in the repository root lists each cheatsheet (P-4).
- The skill uses the most simple workflow that makes a useful cheatsheet (P-3).
- The content for agents is in the same markdown cheatsheet. There is no separate machine-readable file for each topic (P-3, P-4).
- The cheatsheet does not show or copy a private repository (P-7). The skill uses `gh` to find the visibility of each repository. It cites and quotes only public sources.
- All prose in the cheatsheet is in ASD-STE100 Simplified Technical English (P-8).

## Change Log
- **2026-06-05** — Initial draft.
- **2026-06-05** — Added a required current reference code snippet to the cheatsheet, and a concise-point-form invariant that filters detail to future-use must-knows/tips or learning value. Reason: make cheatsheets quicker to scan and ground a "what does it look like today" snippet in current practice.
- **2026-06-05** — Made cheatsheets AI-agent-friendly: added an outcome requiring an "Agent rules" section of imperative ALWAYS/NEVER point-form guardrails (Claude Code research shows imperative rules are load-bearing, frontmatter is not), plus non-goals excluding cargo-cult metadata and auto-wiring into consuming repos. Reason: let a coding agent apply a cheatsheet's corrections directly, not just a human scanning it.
- **2026-06-05** — Added a no-private-repo-leak outcome and constraint: the cheatsheet must exclude any private repo's name/slug/URL and verbatim content, citing only public sources. Reason: enforce Constitution P-7 at the feature level after the principle was ratified.
- **2026-06-05** — Added a top-3 invariant: the "Typical usage patterns" and "Learnings" sections each carry only the 3 highest-value points, with a strong-justification exception for going beyond. Reason: force ruthless curation so the highest-leverage points aren't diluted by marginal ones.
- **2026-10-15** — Rewrote the Problem, Outcome, Non-Goals, and Constraints sections in ASD-STE100 Simplified Technical English. The meaning did not change. Added an outcome that makes the skill write cheatsheet prose in STE. Reason: Constitution P-8, added on 2026-10-15.
- **2026-10-15** — Added pytest citations to O-9 and O-10. The O-9 test uses `gh` to read the visibility of each cited repository. The O-10 test checks the STE sentence length. The agent checks stay for the rules that a test cannot measure. Reason: the agent check for O-9 could not run `gh`, and a test gives a stronger signal.
- **2026-10-15** — Added a pytest citation to O-4. The test checks that each section has only bullets and that each bullet has one or two sentences. The agent check stays for the value of the detail. Reason: a test gives a stronger signal for the structure of the point form.
- **2026-10-15** — Replaced the last words and passive forms that are not STE, for example "idiom", "signal", and "pinned to". The meaning did not change. Reason: Constitution P-8.
- **2026-10-15** — Added a second pytest citation to O-10. The test finds words that STE does not approve, for example "once" and "via". Reason: the agent check found these words again after each rewrite, and a test stops them for good.
