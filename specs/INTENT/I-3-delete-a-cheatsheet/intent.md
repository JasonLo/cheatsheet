---
id: I-3
title: Delete a cheatsheet
slug: delete-a-cheatsheet
status: complete
opened: 2026-06-05
closed: 2026-06-06
superseded_by: null
verdict_outcomes_passed: 6
verdict_outcomes_passed_by_test: 5
verdict_outcomes_total: 6
verdict_checked_at: 2026-06-06T01:10:13Z
---

# Intent: Delete a cheatsheet

- **Author:** Jason Lo
- **Last updated:** 2026-06-05

## Problem
The collection only grows. I-1 generates sheets and I-2 refreshes/recommends them,
but nothing prunes. Removing a sheet today means hand-deleting `cheatsheets/<name>.md`
and remembering to re-run `register_cheatsheet.py` so `index.md` doesn't drift — there
is no first-class delete. There is also no signal that a sheet has gone stale because
its target is no longer used in the owner's own repos.

## Outcome
- **WHEN** the user runs the deletion script with the name of an existing cheatsheet **THE SYSTEM SHALL** delete the corresponding `cheatsheets/<name>.md` file and regenerate `index.md` so the sheet no longer appears in either location.
  - [test: pytest:tests/test_delete_cheatsheet.py::test_delete_removes_file_and_reindexes]
- **WHEN** the user runs the deletion script with a name matching no existing cheatsheet **THE SYSTEM SHALL** exit non-zero with an error identifying the unknown name and leave `cheatsheets/` and `index.md` unmodified.
  - [test: pytest:tests/test_delete_cheatsheet.py::test_unknown_name_errors_and_leaves_repo_unchanged]
- **WHEN** the scheduled staleness workflow runs **THE SYSTEM SHALL** inspect the owner's GitHub usage history via the `gh` CLI and open a single issue presenting, as a markdown table, only those cheatsheets whose target has not appeared in the owner's activity for more than one year — opening no issue when every cheatsheet's target was used within the past year.
  - [test: agent:specs/INTENT/I-3-delete-a-cheatsheet/checks/stale-deletion-proposal-issue.md]
  - [test: shell:test -f .github/workflows/cheatsheet-prune.yml && grep -ql 'workflow_dispatch' .github/workflows/cheatsheet-prune.yml && grep -ql 'concurrency' .github/workflows/cheatsheet-prune.yml && grep -ql 'timeout-minutes' .github/workflows/cheatsheet-prune.yml && ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/cheatsheet-prune.yml]
- **WHEN** the repository owner comments a selection (e.g. "1 and 3") on an open staleness proposal issue **THE SYSTEM SHALL** delete every selected cheatsheet via the deterministic deletion path (removing each file and updating `index.md`) and open exactly one run-scoped pull request bundling all selected deletions and the index update — requiring no local execution and never auto-merging — so the propose → select → delete → review loop completes entirely within the GitHub web interface.
  - [test: agent:specs/INTENT/I-3-delete-a-cheatsheet/checks/web-end-to-end-delete-from-selection.md]
  - [test: shell:test -f .github/workflows/cheatsheet-delete.yml && grep -ql 'issue_comment' .github/workflows/cheatsheet-delete.yml && grep -ql 'concurrency' .github/workflows/cheatsheet-delete.yml && grep -ql 'timeout-minutes' .github/workflows/cheatsheet-delete.yml && ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/cheatsheet-delete.yml]
- **WHEN** the single pull request opened by a selection-triggered delete run is merged into the default branch **THE SYSTEM SHALL** close the originating staleness proposal issue automatically by carrying a `Closes #<issue-number>` keyword in the pull-request body.
  - [test: shell:grep -qE 'Closes #\$\{?ISSUE_NUMBER' .github/workflows/cheatsheet-delete.yml]
- **WHILE** a staleness or selection-triggered delete workflow runs **THE SYSTEM SHALL** read cross-repository GitHub data only through a read-only token via the `gh` CLI, perform writes (the proposal issue, the deletion PR) only within this repository via the default `GITHUB_TOKEN`, and exclude every private repository's name/slug/URL and verbatim content from issue and PR content (Constitution P-5, P-7).
  - [test: agent:specs/INTENT/I-3-delete-a-cheatsheet/checks/prune-token-split-and-privacy.md]

## Non-Goals
- Auto-deletion without review — the scheduled job only opens an issue; the selection job only opens a PR. Nothing is deleted on the default branch without a human-merged PR (no auto-merge).
- Independent per-sheet review or merge — every sheet chosen in one selection comment shares the run's single PR (drop one by editing the PR), mirroring I-2's generate loop.
- Bulk or interactive multi-sheet deletion in one CLI run — the manual script (O-1) deletes one named sheet per invocation; multi-sheet selection lives in the web loop (O-4).
- A correctness/usage score, dashboard, or metrics over the owner's repos — the staleness job emits one issue, not analytics.
- A built-in undo — recovering a deleted sheet is done through git history.
- Per-sheet or configurable staleness windows — the threshold is a fixed one year.
- Defining "usage" beyond GitHub activity reachable via `gh` — local-only or non-GitHub usage is not considered.

## Constraints
- Deletion is concrete and deterministic → code: a self-contained uv script (PEP 723, run via `uv run`) that reuses the existing `index.md` regeneration so the index stays authoritative (P-1, P-2, P-3, P-4, P-6).
- Staleness judgment is ambiguous → handled by the scheduled workflow's agent over `gh` data, not hard-coded (P-6); the deterministic delete stays in code and is what the selection workflow invokes per sheet.
- The select → delete → PR → close loop is event-driven, mirroring I-2's generate handoff: a `cheatsheet-delete.yml` workflow triggers on `issue_comment` (paired with `workflow_dispatch:`), guarded to the repository owner and to staleness proposal issues; it runs the deterministic delete for each selected sheet, opens exactly one run-scoped PR bundling all deletions plus the index update (no auto-merge), and carries `Closes #<issue-number>` so merging it closes the issue. Same hardening, two-token, and privacy boundaries as I-2.
- GitHub data via `gh` only (P-5); cross-repo reads use a read-only PAT secret, repo writes use the default `GITHUB_TOKEN` — the same two-token split as I-2.
- Workflows use `anthropics/claude-code-action`, SHA-pinned, with the repo's standard hardening (least-privilege, concurrency, timeout, schedule+dispatch).
- No private repository disclosed or reproduced in any issue or PR (P-7).

## Change Log
- **2026-06-05** — Initial draft.
