# Agent check: Prune and delete workflows use a read-only token for other repos and hide private repos.

## SHALL

**WHILE** a staleness workflow or a delete workflow runs **THE SYSTEM SHALL** read cross-repository GitHub data only with a read-only token through the `gh` CLI. The workflow writes the issue and the pull request only in this repository, with the default `GITHUB_TOKEN`. Issues and pull requests do not show the name, slug, URL, code, or text of a private repository (Constitution P-5, P-7). [test: agent:specs/INTENT/I-3-delete-a-cheatsheet/checks/prune-token-split-and-privacy.md]

## Success criteria

- Read `.github/workflows/cheatsheet-prune.yml` and `.github/workflows/cheatsheet-delete.yml`.
- PASS: each workflow sets `GH_TOKEN` to `${{ github.token }}` for writes to this repo.
- PASS: each workflow sets `GH_SCAN_TOKEN` from `secrets.GH_SCAN_TOKEN`. A preflight step stops the run if this secret is empty.
- PASS: the prompt runs each cross-repo `gh` read through `uv run scripts/gh_scan.py`, which uses `GH_SCAN_TOKEN`.
- PASS: the prune workflow writes only the proposal issue. The delete workflow writes only the run branch and the deletion pull request. The two write only to this repo.
- PASS: the `permissions:` block of each workflow gives only the scopes that the job needs.
- PASS: each prompt has a privacy section (P-7). It does not allow the name, slug, URL, code, or text of a private repo in the issue or pull request text.
- PASS: each prompt gets the visibility of a repo with `gh repo view ... --json visibility` before it names the repo.
- FAIL: a cross-repo read uses the default token, or a write uses `GH_SCAN_TOKEN`.
- FAIL: a workflow reads GitHub data with a tool other than the `gh` CLI.
- FAIL: a prompt has no privacy rule, or the rule does not cover the full title and body.
- Cite the file:line of the token settings, the preflight step, the `permissions:` block, one prefixed read, and the privacy section in each workflow.
