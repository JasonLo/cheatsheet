---
id: I-2
title: Self-maintenance via scheduled CI agents
slug: self-maintenance-via-scheduled-ci-agents
status: complete
opened: 2026-06-05
closed: 2026-06-05
superseded_by: null
verdict_outcomes_passed: 5
verdict_outcomes_passed_by_test: 1
verdict_outcomes_total: 5
verdict_checked_at: 2026-06-05T21:15:00Z
---

# Intent: Self-maintenance via scheduled CI agents

- **Author:** Jason Lo
- **Last updated:** 2026-06-05 (refined — weekly recommender opens one top-3 issue instead of per-suggestion PRs)

## Problem
The README promises a cheatsheet that "maintains itself" and "proactively proposes new cheatsheets," but today every cheatsheet is produced by a one-shot, manually-invoked skill (I-1). Nothing re-mines the user's repos as their code drifts, nothing detects newly-adopted frameworks the collection doesn't yet cover, and there is no CI. The self-maintenance the product describes does not exist.

## Outcome
- **WHEN** the monthly scheduled workflow runs **THE SYSTEM SHALL** re-mine the user's repositories via the `gh` CLI, regenerate each existing cheatsheet against current documentation, and open exactly one pull request per materially-changed cheatsheet — opening no PR for a cheatsheet whose content is unchanged.
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/monthly-refresh-pr-per-sheet.md]
- **WHEN** the weekly scheduled workflow runs **THE SYSTEM SHALL** scan the user's GitHub activity from the past 7 days, cross-reference existing cheatsheets, and open a single issue presenting at most the top 3 highest-value newly-adopted frameworks not already covered as a markdown table for the user to choose from — opening no issue when no new topic surfaces.
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/weekly-top3-recommendation-issue.md]
- **WHILE** a self-maintenance workflow runs **THE SYSTEM SHALL** read cross-repository GitHub data only through a read-only token via the `gh` CLI, and perform writes (commits, pull requests, and issues) only within this repository via the default `GITHUB_TOKEN`.
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/least-privilege-token-split.md]
- **WHILE** producing any pull-request content **THE SYSTEM SHALL** exclude every private repository's name/slug/URL and verbatim content, conveying private-sourced patterns in generalized form (Constitution P-7).
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/no-private-repo-leak-in-prs.md]
- **WHEN** a self-maintenance workflow file is defined **THE SYSTEM SHALL** pin every third-party action to a full commit SHA, set least-privilege `permissions:`, a `concurrency` group, a `timeout-minutes` bound, and pair `schedule:` with `workflow_dispatch:`.
  - [test: shell:test -d .github/workflows && ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/ && grep -ql 'workflow_dispatch' .github/workflows/cheatsheet-refresh.yml .github/workflows/cheatsheet-recommend.yml && grep -ql 'concurrency' .github/workflows/cheatsheet-refresh.yml .github/workflows/cheatsheet-recommend.yml && grep -ql 'timeout-minutes' .github/workflows/cheatsheet-refresh.yml .github/workflows/cheatsheet-recommend.yml]

## Non-Goals
- Auto-merging PRs — every change is human-reviewed.
- The weekly job generating *full* cheatsheets — it only recommends; full generation is the existing I-1 skill, run after the user picks from the issue.
- A correctness score, dashboard, or metrics over the user's repos.
- Replacing the I-1 generation engine — I-2 only automates its invocation and adds gap detection.
- The weekly job writing files or creating any branch/PR — it opens one issue for the user to choose from; nothing lands until the user runs the I-1 skill.

## Constraints
- GitHub data via `gh` CLI only (P-5); cross-repo reads use a read-only PAT secret, repo writes use the default `GITHUB_TOKEN`.
- Workflows use `anthropics/claude-code-action`, SHA-pinned, following the repo's `self-maintenance-claude-code-action.md` hardening (least-privilege, `--allowedTools` boundary, concurrency, timeout, schedule+dispatch, no-op when clean).
- The agent reuses the I-1 `cheatsheet` skill as the generation procedure; deterministic index regen stays in `register_cheatsheet.py` (P-6).
- No private repo disclosed or reproduced in any PR (P-7).

## Change Log
- **2026-06-05** — Initial draft.
- **2026-06-05** — Refined O-2: the weekly recommender now opens a single issue with a top-3 markdown table for the user to choose from, instead of one proposal-stub PR per topic (capped at 3, mirroring I-1's top-3 curation). Reworded O-3 so "writes" covers issues; replaced the proposals-indexing non-goal with a no-files/no-PR non-goal. Reason: per-suggestion PRs are overkill and unlimited recommendations dilute signal.
