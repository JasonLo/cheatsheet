---
id: I-3
title: Delete a cheatsheet
slug: delete-a-cheatsheet
status: complete
opened: 2026-06-05
closed: 2026-06-06
superseded_by: null
verdict_outcomes_passed: 6
verdict_outcomes_passed_by_test: 6
verdict_outcomes_total: 6
verdict_checked_at: 2026-10-16T04:39:17Z
---

# Intent: Delete a cheatsheet

- **Author:** Jason Lo
- **Last updated:** 2026-10-15 (refined — STE rewrite)

## Problem
The collection only gets larger. I-1 generates cheatsheets, and I-2 refreshes and recommends them. But no process removes them. Today, a person must delete `cheatsheets/<name>.md` manually. Then the person must run `register_cheatsheet.py` again, or `index.md` is not current. There is no standard delete operation. Also, no signal shows that a cheatsheet is old because the owner's repositories do not use its target now.

## Outcome
- **WHEN** the user runs the delete script with the name of a cheatsheet **THE SYSTEM SHALL** delete `cheatsheets/<name>.md` and update `index.md`. After this, the cheatsheet is not in the folder and not in the index.
  - [test: pytest:tests/test_delete_cheatsheet.py::test_delete_removes_file_and_reindexes]
- **WHEN** the delete script gets an unknown name **THE SYSTEM SHALL** exit non-zero with an error that shows the name. The script does not change `cheatsheets/` or `index.md`.
  - [test: pytest:tests/test_delete_cheatsheet.py::test_unknown_name_errors_and_leaves_repo_unchanged]
- **WHEN** the scheduled staleness workflow runs **THE SYSTEM SHALL** open one issue with a markdown table of the old cheatsheets. A cheatsheet is old when its target is not in the owner's GitHub activity for more than one year. The workflow gets this activity history with the `gh` CLI. If all targets had use in the last year, the workflow opens no issue.
  - [test: agent:specs/INTENT/I-3-delete-a-cheatsheet/checks/stale-deletion-proposal-issue.md]
  - [test: shell:test -f .github/workflows/cheatsheet-prune.yml && grep -ql 'workflow_dispatch' .github/workflows/cheatsheet-prune.yml && grep -ql 'concurrency' .github/workflows/cheatsheet-prune.yml && grep -ql 'timeout-minutes' .github/workflows/cheatsheet-prune.yml && ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/cheatsheet-prune.yml]
- **WHEN** the owner comments a selection on an open staleness issue **THE SYSTEM SHALL** open exactly one pull request for the run. An example of a selection is "1 and 3". The workflow deletes each selected cheatsheet with the deterministic delete script, and it updates `index.md`. The pull request contains all deletions and the index update. The loop needs no local step, and the pull request never merges automatically. The user can do the propose → select → delete → review loop in the GitHub web interface.
  - [test: agent:specs/INTENT/I-3-delete-a-cheatsheet/checks/web-end-to-end-delete-from-selection.md]
  - [test: shell:test -f .github/workflows/cheatsheet-delete.yml && grep -ql 'issue_comment' .github/workflows/cheatsheet-delete.yml && grep -ql 'concurrency' .github/workflows/cheatsheet-delete.yml && grep -ql 'timeout-minutes' .github/workflows/cheatsheet-delete.yml && ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/cheatsheet-delete.yml]
- **WHEN** a person merges the pull request of a delete run into the default branch **THE SYSTEM SHALL** close the source staleness issue automatically. The pull-request body contains `Closes #<issue-number>` for this purpose.
  - [test: shell:grep -qE 'Closes #\$\{?ISSUE_NUMBER' .github/workflows/cheatsheet-delete.yml]
- **WHILE** a staleness workflow or a delete workflow runs **THE SYSTEM SHALL** read cross-repository GitHub data only with a read-only token through the `gh` CLI. The workflow writes the issue and the pull request only in this repository, with the default `GITHUB_TOKEN`. Issues and pull requests do not show the name, slug, URL, code, or text of a private repository (Constitution P-5, P-7).
  - [test: pytest:tests/test_workflow_tools.py::test_cross_repo_reads_use_gh_scan]
  - [test: agent:specs/INTENT/I-3-delete-a-cheatsheet/checks/prune-token-split-and-privacy.md]

## Non-Goals
- Deletion without review. The scheduled job only opens an issue, and the selection job only opens a pull request. The default branch keeps each cheatsheet until a person merges a pull request. Pull requests never merge automatically.
- Separate review or merge for each cheatsheet. All cheatsheets from one selection comment are in the one pull request of the run. To keep a cheatsheet, edit the pull request. This is the same as the I-2 generate loop.
- Deletion of many cheatsheets in one CLI run, or interactive deletion. The script (O-1) deletes one named cheatsheet each time. Selection of many cheatsheets is in the web loop (O-4).
- A correctness score, a usage score, a dashboard, or metrics for the owner's repositories. The staleness job opens one issue and gives no analytics.
- An undo command. To restore a deleted cheatsheet, use the git history.
- A staleness limit for each cheatsheet, or a limit that the user can change. The limit is always one year.
- A meaning of "usage" other than GitHub activity that `gh` can read. Local usage and usage outside GitHub do not count.

## Constraints
- Deletion is concrete and deterministic, so code does it. The code is a self-contained uv script (PEP 723) that runs with `uv run` (P-1, P-2, P-3, P-6). It uses the same `index.md` update as the other scripts, so the index stays correct (P-4).
- The decision that a cheatsheet is old is not clear, so the agent of the scheduled workflow makes it from `gh` data (P-6). This decision is not in code. The deterministic delete stays in code, and the selection workflow runs it for each cheatsheet.
- An event starts the select → delete → pull request → close loop. This is the same as the I-2 generate handoff.
- A `cheatsheet-delete.yml` workflow starts on `issue_comment`, and it also has `workflow_dispatch:`. It runs only for comments from the repository owner, and only on staleness issues.
- The delete workflow runs the deterministic delete for each selected cheatsheet. It opens exactly one pull request with all deletions and the index update. The pull request never merges automatically. It contains `Closes #<issue-number>`, so the merge closes the issue.
- The delete workflow has the same hardening, two-token rule, and privacy rule as I-2.
- GitHub data comes only through `gh` (P-5). Reads from other repositories use a read-only PAT secret. Writes to this repository use the default `GITHUB_TOKEN`. This is the same two-token rule as I-2.
- Workflows use `anthropics/claude-code-action`, and they pin it to a SHA. They have the standard hardening of the repository: least privilege, `concurrency`, a timeout, and `schedule:` with `workflow_dispatch:`.
- No issue or pull request shows or copies a private repository (P-7).

## Change Log
- **2026-06-05** — Initial draft.
- **2026-10-15** — Rewrote the Problem, Outcome, Non-Goals, and Constraints sections in ASD-STE100 Simplified Technical English. The meaning and the test citations did not change. Reason: Constitution P-8, added on 2026-10-15.
- **2026-10-15** — Replaced the last words and passive forms that are not STE, for example "idiom", "signal", and "pinned to". The meaning did not change. Reason: Constitution P-8.
- **2026-10-15** — Added a pytest citation to O-6. The test checks that each workflow reads other repos through `scripts/gh_scan.py`. Reason: a test showed that the agent tool rules deny a command with `$`, so the old `GH_TOKEN=$GH_SCAN_TOKEN gh` reads could not run.
