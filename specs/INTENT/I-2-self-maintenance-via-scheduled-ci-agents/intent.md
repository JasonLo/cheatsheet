---
id: I-2
title: Self-maintenance via scheduled CI agents
slug: self-maintenance-via-scheduled-ci-agents
status: complete
opened: 2026-06-05
closed: 2026-06-05
superseded_by: null
verdict_outcomes_passed: 6
verdict_outcomes_passed_by_test: 2
verdict_outcomes_total: 6
verdict_checked_at: 2026-06-05T21:29:26Z
---

# Intent: Self-maintenance via scheduled CI agents

- **Author:** Jason Lo
- **Last updated:** 2026-06-05 (refined — selecting a recommendation by issue comment now generates the sheet, closing the loop end-to-end in the GitHub web UI)

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
- **WHEN** the repository owner comments a topic selection (e.g. "1 and 3") on an open cheatsheet-recommendations issue **THE SYSTEM SHALL** generate each selected cheatsheet via the I-1 skill and open exactly one human-reviewed pull request per selected topic, requiring no local execution — so the recommend → select → generate → review loop completes entirely within the GitHub web interface.
  - [test: shell:test -f .github/workflows/cheatsheet-generate.yml && grep -ql 'issue_comment' .github/workflows/cheatsheet-generate.yml && grep -ql 'concurrency' .github/workflows/cheatsheet-generate.yml && grep -ql 'timeout-minutes' .github/workflows/cheatsheet-generate.yml && ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/cheatsheet-generate.yml]
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/web-end-to-end-generate-from-selection.md]

## Non-Goals
- Auto-merging PRs — every change is human-reviewed.
- The weekly *recommender* job generating cheatsheets — it only recommends; generation runs in a separate selection-triggered workflow (O-6) that reuses the I-1 skill.
- A correctness score, dashboard, or metrics over the user's repos.
- Replacing the I-1 generation engine — I-2 only automates its invocation and adds gap detection.
- The weekly recommender writing files or creating any branch/PR — it opens one issue for the user to choose from; files/PRs land only via the selection-triggered generate workflow (O-6), and never auto-merge.

## Constraints
- GitHub data via `gh` CLI only (P-5); cross-repo reads use a read-only PAT secret, repo writes use the default `GITHUB_TOKEN`.
- Workflows use `anthropics/claude-code-action`, SHA-pinned, following the repo's `self-maintenance-claude-code-action.md` hardening (least-privilege, `--allowedTools` boundary, concurrency, timeout, schedule+dispatch, no-op when clean).
- The agent reuses the I-1 `cheatsheet` skill as the generation procedure; deterministic index regen stays in `register_cheatsheet.py` (P-6).
- No private repo disclosed or reproduced in any PR (P-7).
- The recommend → generate handoff is event-driven: a `cheatsheet-generate.yml` workflow triggers on `issue_comment` (paired with `workflow_dispatch:`), guarded to the repository owner and to cheatsheet-recommendations issues, so the loop is completable in the web UI with no local step. It carries the same hardening as the scheduled workflows (SHA-pinned, least-privilege `permissions:`, `concurrency`, `timeout-minutes`) and the same two-token (O-3) and privacy (O-4) boundaries, and opens one human-reviewed PR per selected sheet (no auto-merge). The recommendations issue's per-topic "Generate with" instruction MUST reflect this comment-to-generate path rather than a local command.

## Change Log
- **2026-06-05** — Initial draft.
- **2026-06-05** — Refined O-2: the weekly recommender now opens a single issue with a top-3 markdown table for the user to choose from, instead of one proposal-stub PR per topic (capped at 3, mirroring I-1's top-3 curation). Reworded O-3 so "writes" covers issues; replaced the proposals-indexing non-goal with a no-files/no-PR non-goal. Reason: per-suggestion PRs are overkill and unlimited recommendations dilute signal.
- **2026-06-05** — Added O-6: selecting a recommendation by commenting on the recommendations issue (e.g. "1 and 3") triggers a guarded `cheatsheet-generate.yml` workflow that generates each chosen sheet via the I-1 skill and opens one human-reviewed PR per topic — closing the recommend → select → generate → review loop entirely within the GitHub web UI with no local step. Reworded the two weekly non-goals to point generation at the new workflow (the recommender still only recommends) and added a constraint specifying the event-driven, owner-guarded handoff with the same hardening, two-token, and privacy boundaries. Reason: the recommender issue already promised "I'll generate those cheatsheets," but nothing fulfilled it without dropping to a local terminal.
