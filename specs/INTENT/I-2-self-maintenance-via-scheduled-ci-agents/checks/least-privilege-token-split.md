# Agent check: Workflows read other repos with a read-only token and write only to this repo.

## SHALL

**WHILE** a self-maintenance workflow runs **THE SYSTEM SHALL** read cross-repository GitHub data only with a read-only token through the `gh` CLI. The workflow writes commits, pull requests, and issues only in this repository, with the default `GITHUB_TOKEN`. [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/least-privilege-token-split.md]

## Success criteria

- Read `.github/workflows/cheatsheet-recommend.yml`, `.github/workflows/cheatsheet-refresh.yml`, and `.github/workflows/cheatsheet-generate.yml`.
- PASS: each workflow sets `GH_TOKEN` to `${{ github.token }}` for writes to this repo.
- PASS: each workflow sets `GH_SCAN_TOKEN` from `secrets.GH_SCAN_TOKEN`. A preflight step stops the run if this secret is empty.
- PASS: the prompt runs each cross-repo `gh` read through `uv run scripts/gh_scan.py`, which uses `GH_SCAN_TOKEN`.
- PASS: issue writes, commits, pushes, and pull requests use the default token and target only this repo.
- PASS: the `permissions:` block of each workflow gives only the scopes that the job needs.
- FAIL: a cross-repo read uses the default token, or a write uses `GH_SCAN_TOKEN`.
- FAIL: a workflow reads GitHub data with a tool other than the `gh` CLI, for example `curl` or an SDK.
- FAIL: a workflow writes to a repo other than this repo.
- Cite the file:line of the `GH_TOKEN` and `GH_SCAN_TOKEN` settings, the preflight step, the `permissions:` block, and one prefixed read in each workflow.
