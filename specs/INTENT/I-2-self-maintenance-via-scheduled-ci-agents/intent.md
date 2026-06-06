---
id: I-2
title: Self-maintenance via scheduled CI agents
slug: self-maintenance-via-scheduled-ci-agents
status: in_progress
opened: 2026-06-05
closed: null
superseded_by: null
verdict_outcomes_passed: 6
verdict_outcomes_passed_by_test: 2
verdict_outcomes_total: 7
verdict_checked_at: 2026-06-06T00:08:25Z
---

# Intent: Self-maintenance via scheduled CI agents

- **Author:** Jason Lo
- **Last updated:** 2026-06-05 (refined — selection-triggered generate now opens ONE run-scoped PR bundling all selected sheets, and that PR auto-closes its originating issue on merge)

## Problem
The README promises a cheatsheet that "maintains itself" and "proactively proposes new cheatsheets," but today every cheatsheet is produced by a one-shot, manually-invoked skill (I-1). Nothing re-mines the user's repos as their code drifts, nothing detects newly-adopted frameworks the collection doesn't yet cover, and there is no CI. The self-maintenance the product describes does not exist.

## Outcome
- **WHEN** the monthly scheduled workflow runs **THE SYSTEM SHALL** re-mine the user's repositories via the `gh` CLI, regenerate each existing cheatsheet against current documentation, and open a single issue presenting as a markdown table only those cheatsheets whose content changed in meaning — a conceptual or semantic shift in an idiom, Learning, or Agent rule (e.g. an obsolete API pattern or a changed best practice) — ignoring wording, reordering, and cosmetic edits, and opening no issue when no cheatsheet changed meaningfully.
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/monthly-refresh-meaningful-drift-issue.md]
- **WHEN** the weekly scheduled workflow runs **THE SYSTEM SHALL** scan the user's GitHub activity from the past 7 days, cross-reference existing cheatsheets, and open a single issue presenting at most the top 3 highest-value newly-adopted frameworks not already covered as a markdown table for the user to choose from — opening no issue when no new topic surfaces.
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/weekly-top3-recommendation-issue.md]
- **WHILE** a self-maintenance workflow runs **THE SYSTEM SHALL** read cross-repository GitHub data only through a read-only token via the `gh` CLI, and perform writes (commits, pull requests, and issues) only within this repository via the default `GITHUB_TOKEN`.
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/least-privilege-token-split.md]
- **WHILE** producing any pull-request content **THE SYSTEM SHALL** exclude every private repository's name/slug/URL and verbatim content, conveying private-sourced patterns in generalized form (Constitution P-7).
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/no-private-repo-leak-in-prs.md]
- **WHEN** a self-maintenance workflow file is defined **THE SYSTEM SHALL** pin every third-party action to a full commit SHA, set least-privilege `permissions:`, a `concurrency` group, a `timeout-minutes` bound, and pair `schedule:` with `workflow_dispatch:`.
  - [test: shell:test -d .github/workflows && ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/ && grep -ql 'workflow_dispatch' .github/workflows/cheatsheet-refresh.yml .github/workflows/cheatsheet-recommend.yml && grep -ql 'concurrency' .github/workflows/cheatsheet-refresh.yml .github/workflows/cheatsheet-recommend.yml && grep -ql 'timeout-minutes' .github/workflows/cheatsheet-refresh.yml .github/workflows/cheatsheet-recommend.yml]
- **WHEN** the repository owner comments a topic selection (e.g. "1 and 3") on an open cheatsheet recommendations issue or monthly-refresh issue **THE SYSTEM SHALL** generate (for a recommendations issue) or regenerate (for a refresh issue) every selected cheatsheet via the I-1 skill and open exactly one human-reviewed pull request for that run — bundling all selected sheets and their `index.md` update into the single PR — requiring no local execution, so both the recommend → select → generate → review loop and the refresh → select → regenerate → review loop complete entirely within the GitHub web interface.
  - [test: shell:test -f .github/workflows/cheatsheet-generate.yml && grep -ql 'issue_comment' .github/workflows/cheatsheet-generate.yml && grep -ql 'concurrency' .github/workflows/cheatsheet-generate.yml && grep -ql 'timeout-minutes' .github/workflows/cheatsheet-generate.yml && ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/cheatsheet-generate.yml]
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/web-end-to-end-generate-from-selection.md]
- **WHEN** the single pull request opened by a selection-triggered generate run is merged into the default branch **THE SYSTEM SHALL** close the originating recommendations or monthly-refresh issue automatically, by carrying a GitHub closing keyword (`Closes #<issue-number>`) in the pull-request body.
  - [test: shell:grep -qE 'Closes #\$\{?ISSUE_NUMBER' .github/workflows/cheatsheet-generate.yml]

## Non-Goals
- Auto-merging PRs — every change is human-reviewed.
- The weekly *recommender* job generating cheatsheets — it only recommends; generation runs in a separate selection-triggered workflow (O-6) that reuses the I-1 skill.
- A correctness score, dashboard, or metrics over the user's repos.
- Replacing the I-1 generation engine — I-2 only automates its invocation and adds gap detection.
- The weekly recommender writing files or creating any branch/PR — it opens one issue for the user to choose from; files/PRs land only via the selection-triggered generate workflow (O-6), and never auto-merge.
- The monthly *refresh* job writing files or creating any branch/PR — like the recommender it only opens one issue (flagging cheatsheets with meaningful drift); regeneration and PRs land only via the selection-triggered generate workflow (O-6), and never auto-merge.
- The refresh issue flagging cosmetic drift — wording tweaks, reordering, or a changed `_Grounded in … as of <date>_` line never qualify; only a conceptual/semantic shift in an idiom, Learning, or Agent rule is listed.
- Independent per-sheet review or merge — every sheet chosen in one selection comment shares the run's single PR, so a run's sheets land or are dropped together (drop an unwanted sheet by editing the one PR); the workflow never opens a separate PR per topic.
- Preserving an issue as a reusable multi-comment menu — because the run's PR carries `Closes #N`, merging it closes the originating issue; picking further topics afterward means a later scheduled issue (or manually reopening), not re-selecting from the closed one.

## Constraints
- GitHub data via `gh` CLI only (P-5); cross-repo reads use a read-only PAT secret, repo writes use the default `GITHUB_TOKEN`.
- Workflows use `anthropics/claude-code-action`, SHA-pinned, following the repo's `self-maintenance-claude-code-action.md` hardening (least-privilege, `--allowedTools` boundary, concurrency, timeout, schedule+dispatch, no-op when clean).
- The agent reuses the I-1 `cheatsheet` skill as the generation procedure; deterministic index regen stays in `register_cheatsheet.py` (P-6).
- No private repo disclosed or reproduced in any PR (P-7).
- The select → generate handoff is event-driven: a single `cheatsheet-generate.yml` workflow triggers on `issue_comment` (paired with `workflow_dispatch:`), guarded to the repository owner and to both cheatsheet recommendations issues (new sheets) and monthly-refresh issues (existing sheets), so both loops are completable in the web UI with no local step. For a recommendations issue it generates new sheets; for a refresh issue it regenerates the selected existing sheets (the "already covered → skip" guard applies only to recommendations issues). It carries the same hardening as the scheduled workflows (SHA-pinned, least-privilege `permissions:`, `concurrency`, `timeout-minutes`) and the same two-token (O-3) and privacy (O-4) boundaries, and opens exactly one human-reviewed PR per run bundling all selected sheets (no auto-merge), whose body carries a `Closes #<issue-number>` keyword so merging it closes the originating issue (O-7). Each issue's selection instruction MUST reflect this comment-to-generate path rather than a local command.

## Change Log
- **2026-06-05** — Initial draft.
- **2026-06-05** — Refined O-2: the weekly recommender now opens a single issue with a top-3 markdown table for the user to choose from, instead of one proposal-stub PR per topic (capped at 3, mirroring I-1's top-3 curation). Reworded O-3 so "writes" covers issues; replaced the proposals-indexing non-goal with a no-files/no-PR non-goal. Reason: per-suggestion PRs are overkill and unlimited recommendations dilute signal.
- **2026-06-05** — Added O-6: selecting a recommendation by commenting on the recommendations issue (e.g. "1 and 3") triggers a guarded `cheatsheet-generate.yml` workflow that generates each chosen sheet via the I-1 skill and opens one human-reviewed PR per topic — closing the recommend → select → generate → review loop entirely within the GitHub web UI with no local step. Reworded the two weekly non-goals to point generation at the new workflow (the recommender still only recommends) and added a constraint specifying the event-driven, owner-guarded handoff with the same hardening, two-token, and privacy boundaries. Reason: the recommender issue already promised "I'll generate those cheatsheets," but nothing fulfilled it without dropping to a local terminal.
- **2026-06-05** — Refined O-1 to mirror the weekly recommender: the monthly refresh now opens a single issue presenting (as a markdown table) only cheatsheets whose content changed in MEANING — a conceptual/semantic shift in an idiom, Learning, or Agent rule — explicitly ignoring wording, reordering, and cosmetic edits; it no longer opens PRs directly. Extended O-6 and the handoff constraint so the one `cheatsheet-generate.yml` workflow serves both recommendations issues (generate new sheets) and refresh issues (regenerate existing sheets, lifting the "already covered → skip" guard for the refresh path), and added two non-goals scoping the refresh job to issue-only output and to meaningful-drift-only flagging. Swapped O-1's check to `monthly-refresh-meaningful-drift-issue.md`. Reason: per-sheet refresh PRs are noisy and surface cosmetic churn; routing through select→generate keeps review in the web UI and limits delta to changes that actually matter.
- **2026-06-05** — Refined O-6 from "one PR per selected topic" to "exactly one run-scoped PR bundling all selected sheets (plus the `index.md` update)," and added O-7: that single PR carries a `Closes #<issue-number>` keyword so merging it auto-closes the originating recommendations/refresh issue. Updated the handoff constraint to match and added two non-goals (no independent per-sheet review/merge; the issue is not a reusable multi-comment menu once its PR merges). Reason: one issue → one PR per run keeps review and merge to a single unit and makes issue closure automatic, replacing the manual close step — at the accepted cost of per-sheet merge granularity.
