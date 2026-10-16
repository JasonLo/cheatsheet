# Agent check: The staleness workflow opens one issue that lists only cheatsheets not used for more than one year.

## SHALL

**WHEN** the scheduled staleness workflow runs **THE SYSTEM SHALL** open one issue with a markdown table of the old cheatsheets. A cheatsheet is old when its target is not in the owner's GitHub activity for more than one year. The workflow gets this activity history with the `gh` CLI. If all targets had use in the last year, the workflow opens no issue. [test: agent:specs/INTENT/I-3-delete-a-cheatsheet/checks/stale-deletion-proposal-issue.md]

## Success criteria

- Read `.github/workflows/cheatsheet-prune.yml`. Use Glob to list `cheatsheets/*.md`.
- PASS: the workflow has a `schedule:` cron and a `workflow_dispatch:` trigger.
- PASS: the prompt gets the owner's GitHub activity with `gh`, through `uv run scripts/gh_scan.py`. Examples are `gh search code` and `gh search commits` with a cutoff date.
- PASS: the cutoff is exactly one year before the run date.
- PASS: the prompt marks a cheatsheet as old only when its target has no activity after the cutoff.
- PASS: the prompt opens exactly one issue with a markdown table of the old cheatsheets.
- PASS: the issue title starts with `Cheatsheet staleness`, so `.github/workflows/cheatsheet-delete.yml` accepts a selection on it.
- PASS: the prompt opens no issue when all targets had use in the last year.
- FAIL: the job deletes files, pushes a branch, or opens a pull request.
- FAIL: the limit is not one year, or the table can list a cheatsheet with recent use.
- Cite the file:line of the trigger, the activity commands, the cutoff, the "no issue" rule, and the `gh issue create` step.
