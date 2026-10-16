# Agent check: An owner comment on a staleness issue deletes the selected cheatsheets in one pull request.

## SHALL

**WHEN** the owner comments a selection on an open staleness issue **THE SYSTEM SHALL** open exactly one pull request for the run. An example of a selection is "1 and 3". The workflow deletes each selected cheatsheet with the deterministic delete script, and it updates `index.md`. The pull request contains all deletions and the index update. The loop needs no local step, and the pull request never merges automatically. The user can do the propose → select → delete → review loop in the GitHub web interface. [test: agent:specs/INTENT/I-3-delete-a-cheatsheet/checks/web-end-to-end-delete-from-selection.md]

## Success criteria

- Read `.github/workflows/cheatsheet-delete.yml`, `.github/workflows/cheatsheet-prune.yml`, and `scripts/delete_cheatsheet.py`.
- PASS: the workflow has `on: issue_comment: types: [created]` and `workflow_dispatch` with an issue number and a selection.
- PASS: the job `if:` accepts a comment only from the repo owner, only on an open issue, and only when the title starts with `Cheatsheet staleness`. It rejects a comment on a pull request.
- PASS: the prompt reads the issue with `gh issue view`, parses the table, and maps each selected number to a row. It skips a number with no row.
- PASS: the workflow passes the selection text through `env`, not directly in the prompt string.
- PASS: the agent removes each sheet only with `uv run scripts/delete_cheatsheet.py <slug>`. This script deletes the file and updates `index.md`.
- PASS: one run branch `auto/delete/from-issue-<N>` holds all deletions. A guard with `gh pr list --head <branch>` stops a second pull request.
- PASS: the agent runs `gh pr create` exactly one time. The last line of the body is `Closes #<N>`.
- PASS: `--allowedTools` does not include `gh pr merge`, `gh pr review`, or a wildcard `gh pr:*`.
- PASS: the issue from `cheatsheet-prune.yml` tells the user to comment numbers. It does not tell the user to run a local step.
- FAIL: one condition is missing, or the workflow can merge a pull request automatically.
- Cite the file:line of the trigger, the guard, the delete command, the run branch, the `gh pr create` step, `Closes`, and `--allowedTools`.
