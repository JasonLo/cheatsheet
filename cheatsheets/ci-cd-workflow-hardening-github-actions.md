# CI/CD workflow hardening with github-actions

_Grounded in JasonLo's repos as of 2026-08-31; current practice per docs.github.com/en/actions._

## Reference snippet

```yaml
# Minimal hardened CI: validates PRs before merge, fails fast
name: CI

on:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read          # never grant more than the job needs

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

defaults:
  run:
    shell: bash

jobs:
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v7
        with:
          enable-cache: true
      - run: uv sync --frozen
      - run: uv run pytest -q
```

## Typical usage patterns

- **Minimal `permissions` block per workflow**: declare only what the job writes (e.g., `pages: write` + `id-token: write` for Pages deploy; `contents: read` for CI). Absent field defaults to repo setting — which is often broader than needed. (`JasonLo/jasonlo.dev:.github/workflows/ci.yml`, `JasonLo/jasonlo.dev:.github/workflows/publish.yml`)

- **`workflow_run` to chain privileged steps off an unprivileged job**: when a `push` by `GITHUB_TOKEN` doesn't re-trigger a push event (GitHub's anti-recursion rule), a downstream workflow listens on `workflow_run: workflows: [<name>]` and only deploys when `github.event.workflow_run.conclusion == 'success'` — separating untrusted CI code from secret-bearing deploy steps. (`JasonLo/jasonlo.dev:.github/workflows/publish.yml` chains off `sync-publications-fused.yml`)

- **Dependabot for monthly action version bumps**: `package-ecosystem: github-actions` with `commit-message.prefix: "chore(ci)"` keeps action SHAs current without manual tracking. (`JasonLo/jasonlo.dev:.github/dependabot.yml`)

## Learnings

- **One cancel-in-progress setting for all jobs** → **context-sensitive cancel: fast-cancel PRs, preserve deploys.** A cancelled deploy can leave infra half-provisioned; use `cancel-in-progress: ${{ github.event_name == 'pull_request' }}` for CI groups and `cancel-in-progress: false` for deploy/publish groups. (seen in `JasonLo/jasonlo.dev:.github/workflows/publish.yml` vs. older workflows without this split)

- **Relying on the default 360-minute timeout** → **set explicit `timeout-minutes` per job.** A silent hang blocks runners for 6 hours and burns quota; an explicit limit fails fast and surfaces the problem. (seen in `simulation-based-inference/simulation-based-inference.github.io:.github/workflows/ci.yml` — no timeout — vs. JasonLo's newer workflows that always set it)

- **`defaults: run: shell: bash` is optional boilerplate** → **it's load-bearing on cross-platform runners.** Without it, shell selection falls to the runner OS default, making `[[ ]]` and `set -euo pipefail` silently behave differently on Windows. Always set it explicitly. (seen in `JasonLo/jasonlo.dev:.github/workflows/ci.yml`)

## Agent rules

- ALWAYS declare a `permissions` block on every workflow; never rely on the repository default.
- ALWAYS set `timeout-minutes` on every job; never let the 360-minute default silently burn quota.
- ALWAYS use context-sensitive `cancel-in-progress`: true (or conditional) for CI jobs, false for deploy jobs.
- ALWAYS add `defaults: run: shell: bash` for consistent shell behavior across runners.
- NEVER trigger a write-privileged deploy step from the same job that runs untrusted PR code — chain via `workflow_run` instead.
