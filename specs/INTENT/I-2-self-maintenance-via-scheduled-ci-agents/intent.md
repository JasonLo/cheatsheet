---
id: I-2
title: Self-maintenance with scheduled CI agents
slug: self-maintenance-via-scheduled-ci-agents
status: complete
opened: 2026-06-05
closed: 2026-06-06
superseded_by: null
verdict_outcomes_passed: 7
verdict_outcomes_passed_by_test: 4
verdict_outcomes_total: 7
verdict_checked_at: 2026-10-16T04:39:17Z
---

# Intent: Self-maintenance with scheduled CI agents

- **Author:** Jason Lo
- **Last updated:** 2026-10-15 (refined — STE rewrite)

## Problem
The README says that the cheatsheet "maintains itself" and "proactively proposes new cheatsheets". But a person must start the I-1 skill manually to make each cheatsheet. No process mines the repositories again when the code changes. No process finds new frameworks that the collection does not cover. The repository has no CI. As a result, the self-maintenance that the product describes does not exist.

## Outcome
- **WHEN** the monthly scheduled workflow runs **THE SYSTEM SHALL** open one issue with a markdown table of the cheatsheets whose meaning changed. The workflow mines the user's repositories again with the `gh` CLI. It makes each cheatsheet again with the current documentation. A change in meaning is a change in the concept of a usage pattern, a Learning, or an Agent rule. An old API pattern and a new best practice are examples. The workflow ignores changes in wording, changes in order, and cosmetic changes. If no cheatsheet changed in meaning, the workflow opens no issue.
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/monthly-refresh-meaningful-drift-issue.md]
- **WHEN** the weekly scheduled workflow runs **THE SYSTEM SHALL** open one issue that shows the top 3 new frameworks in a markdown table. The workflow scans the user's GitHub activity of the last 7 days. It compares this activity with the current cheatsheets. The table shows only frameworks that no cheatsheet covers, and not more than 3. The user selects frameworks from this table. If the workflow finds no new topic, it opens no issue.
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/weekly-top3-recommendation-issue.md]
- **WHILE** a self-maintenance workflow runs **THE SYSTEM SHALL** read cross-repository GitHub data only with a read-only token through the `gh` CLI. The workflow writes commits, pull requests, and issues only in this repository, with the default `GITHUB_TOKEN`.
  - [test: pytest:tests/test_workflow_tools.py::test_cross_repo_reads_use_gh_scan]
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/least-privilege-token-split.md]
- **WHILE** the system writes pull-request content **THE SYSTEM SHALL** not show the name, slug, URL, code, or text of a private repository (Constitution P-7). It gives patterns from private repositories only in a general form.
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/no-private-repo-leak-in-prs.md]
- **WHEN** a person defines a self-maintenance workflow file **THE SYSTEM SHALL** pin each third-party action to a full commit SHA. The file also sets least-privilege `permissions:`, a `concurrency` group, and a `timeout-minutes` limit. The file pairs `schedule:` with `workflow_dispatch:`.
  - [test: shell:test -d .github/workflows && ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/ && grep -ql 'workflow_dispatch' .github/workflows/cheatsheet-refresh.yml .github/workflows/cheatsheet-recommend.yml && grep -ql 'concurrency' .github/workflows/cheatsheet-refresh.yml .github/workflows/cheatsheet-recommend.yml && grep -ql 'timeout-minutes' .github/workflows/cheatsheet-refresh.yml .github/workflows/cheatsheet-recommend.yml]
- **WHEN** the owner comments a selection on an open recommendations or refresh issue **THE SYSTEM SHALL** open exactly one pull request for the run. An example of a selection is "1 and 3". For a recommendations issue, the workflow makes each selected cheatsheet with the I-1 skill. For a refresh issue, the workflow makes each selected cheatsheet again. The pull request contains all selected cheatsheets and the `index.md` update. A person reviews the pull request. The loop needs no local step. The user can do the recommend → select → generate → review loop in the GitHub web interface. The same applies to the refresh → select → regenerate → review loop.
  - [test: shell:test -f .github/workflows/cheatsheet-generate.yml && grep -ql 'issue_comment' .github/workflows/cheatsheet-generate.yml && grep -ql 'concurrency' .github/workflows/cheatsheet-generate.yml && grep -ql 'timeout-minutes' .github/workflows/cheatsheet-generate.yml && ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/cheatsheet-generate.yml]
  - [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/web-end-to-end-generate-from-selection.md]
- **WHEN** a person merges the pull request of a selection run into the default branch **THE SYSTEM SHALL** close the source issue automatically. The pull-request body contains the GitHub closing keyword `Closes #<issue-number>` for this purpose.
  - [test: shell:grep -qE 'Closes #\$\{?ISSUE_NUMBER' .github/workflows/cheatsheet-generate.yml]

## Non-Goals
- Automatic merge of pull requests. A person reviews each change.
- Generation of cheatsheets by the weekly recommender job. This job only recommends. A separate workflow uses the I-1 skill to generate cheatsheets after a selection (O-6).
- A correctness score, a dashboard, or metrics for the user's repositories.
- A replacement for the I-1 generation skill. I-2 only starts I-1 automatically and finds topics that no cheatsheet covers.
- Files, branches, or pull requests from the weekly recommender. It opens one issue for the user. Files and pull requests come only from the selection workflow (O-6), and they never merge automatically.
- Files, branches, or pull requests from the monthly refresh job. It opens only one issue that lists cheatsheets with a change in meaning. New versions and pull requests come only from the selection workflow (O-6), and they never merge automatically.
- Cosmetic changes in the refresh issue. Changes in wording, changes in order, and a new date in the `_Grounded in …_` line do not count. Only a change in the concept of a usage pattern, a Learning, or an Agent rule counts.
- Separate review or merge for each cheatsheet. All cheatsheets from one selection comment are in the one pull request of the run. To remove a cheatsheet, edit that pull request. The workflow never opens one pull request for each topic.
- An issue that the user can use again for more selections. The pull request contains `Closes #N`, so the merge closes the issue. For more topics, use a later scheduled issue, or open the issue again manually.

## Constraints
- GitHub data comes only through the `gh` CLI (P-5). Reads from other repositories use a read-only PAT secret. Writes to this repository use the default `GITHUB_TOKEN`.
- Workflows use `anthropics/claude-code-action`, and they pin it to a SHA. They follow the hardening in `self-maintenance-claude-code-action.md`. This hardening includes least privilege, an `--allowedTools` limit, `concurrency`, a timeout, and `schedule:` with `workflow_dispatch:`. It also includes no action when there is no change.
- The agent uses the I-1 `cheatsheet` skill to generate cheatsheets. The deterministic index update stays in `register_cheatsheet.py` (P-6).
- No pull request shows or copies a private repository (P-7).
- An event starts the select → generate step. One `cheatsheet-generate.yml` workflow starts on `issue_comment`, and it also has `workflow_dispatch:`.
- The generate workflow runs only for comments from the repository owner. It runs only on recommendations issues (new cheatsheets) and monthly-refresh issues (current cheatsheets).
- For a recommendations issue, the workflow generates new cheatsheets. For a refresh issue, it generates the selected current cheatsheets again. The "already covered → skip" guard applies only to recommendations issues.
- The generate workflow has the same hardening as the scheduled workflows. This includes SHA pins, least-privilege `permissions:`, `concurrency`, and `timeout-minutes`. It also has the same two-token rule (O-3) and privacy rule (O-4).
- Each run opens exactly one pull request with all selected cheatsheets. A person reviews it, and it never merges automatically. Its body contains `Closes #<issue-number>`, so the merge closes the source issue (O-7).
- The selection instruction in each issue MUST tell the user to write a comment. It MUST NOT tell the user to run a local command.

## Change Log
- **2026-06-05** — Initial draft.
- **2026-06-05** — Refined O-2: the weekly recommender now opens a single issue with a top-3 markdown table for the user to choose from, instead of one proposal-stub PR per topic (capped at 3, mirroring I-1's top-3 curation). Reworded O-3 so "writes" covers issues; replaced the proposals-indexing non-goal with a no-files/no-PR non-goal. Reason: per-suggestion PRs are overkill and unlimited recommendations dilute signal.
- **2026-06-05** — Added O-6: selecting a recommendation by commenting on the recommendations issue (e.g. "1 and 3") triggers a guarded `cheatsheet-generate.yml` workflow that generates each chosen sheet via the I-1 skill and opens one human-reviewed PR per topic — closing the recommend → select → generate → review loop entirely within the GitHub web UI with no local step. Reworded the two weekly non-goals to point generation at the new workflow (the recommender still only recommends) and added a constraint specifying the event-driven, owner-guarded handoff with the same hardening, two-token, and privacy boundaries. Reason: the recommender issue already promised "I'll generate those cheatsheets," but nothing fulfilled it without dropping to a local terminal.
- **2026-06-05** — Refined O-1 to mirror the weekly recommender: the monthly refresh now opens a single issue presenting (as a markdown table) only cheatsheets whose content changed in MEANING — a conceptual/semantic shift in an idiom, Learning, or Agent rule — explicitly ignoring wording, reordering, and cosmetic edits; it no longer opens PRs directly. Extended O-6 and the handoff constraint so the one `cheatsheet-generate.yml` workflow serves both recommendations issues (generate new sheets) and refresh issues (regenerate existing sheets, lifting the "already covered → skip" guard for the refresh path), and added two non-goals scoping the refresh job to issue-only output and to meaningful-drift-only flagging. Swapped O-1's check to `monthly-refresh-meaningful-drift-issue.md`. Reason: per-sheet refresh PRs are noisy and surface cosmetic churn; routing through select→generate keeps review in the web UI and limits delta to changes that actually matter.
- **2026-06-05** — Refined O-6 from "one PR per selected topic" to "exactly one run-scoped PR bundling all selected sheets (plus the `index.md` update)," and added O-7: that single PR carries a `Closes #<issue-number>` keyword so merging it auto-closes the originating recommendations/refresh issue. Updated the handoff constraint to match and added two non-goals (no independent per-sheet review/merge; the issue is not a reusable multi-comment menu once its PR merges). Reason: one issue → one PR per run keeps review and merge to a single unit and makes issue closure automatic, replacing the manual close step — at the accepted cost of per-sheet merge granularity.
- **2026-10-15** — Rewrote the Problem, Outcome, Non-Goals, and Constraints sections in ASD-STE100 Simplified Technical English. The title changed from "via" to "with". The meaning and the test citations did not change. Reason: Constitution P-8, added on 2026-10-15.
- **2026-10-15** — Replaced the last words and passive forms that are not STE, for example "idiom", "signal", and "pinned to". The meaning did not change. Reason: Constitution P-8.
- **2026-10-15** — Added a pytest citation to O-3. The test checks that each workflow reads other repos through `scripts/gh_scan.py`. Reason: a test showed that the agent tool rules deny a command with `$`, so the old `GH_TOKEN=$GH_SCAN_TOKEN gh` reads could not run.
