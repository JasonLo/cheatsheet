# CI/CD workflow hardening with github-actions

_Grounded in JasonLo's repos as of 2026-08-31. Current practice is from docs.github.com/en/actions._

## Reference snippet

```yaml
# Minimal hardened CI. It checks PRs before merge and stops at the first failure.
name: CI

on:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read          # Give only the permissions that the job needs

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
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262  # v4
      - uses: astral-sh/setup-uv@37802adc94f370d6bfd71619e3f0bf239e1f3b78  # v7
        with:
          enable-cache: true
      - run: uv sync --frozen
      - run: uv run pytest -q
```

## Typical usage patterns

- **Minimal `permissions` block for each workflow.** Declare only the permissions that the job uses, for example `contents: read` for CI. A Pages deploy needs `pages: write` and `id-token: write`. (seen in `JasonLo/jasonlo.dev:.github/workflows/ci.yml`, `JasonLo/jasonlo.dev:.github/workflows/publish.yml`)

- **Start the deploy with `workflow_run`.** A push by `GITHUB_TOKEN` does not start other workflows, so the deploy workflow starts on `workflow_run`. It deploys only when `github.event.workflow_run.conclusion == 'success'`, and it runs separately from untrusted CI code. (seen in `JasonLo/jasonlo.dev:.github/workflows/publish.yml`)

- **Dependabot for monthly action updates.** Set `package-ecosystem: github-actions` with `commit-message.prefix: "chore(ci)"`. Dependabot then keeps the action SHAs current without manual work. (seen in `JasonLo/jasonlo.dev:.github/dependabot.yml`)

## Learnings

- **One cancel setting for all jobs** → **Cancel old CI runs, never a deploy.** A cancelled deploy can leave infrastructure in a partial state. CI groups use `cancel-in-progress: ${{ github.event_name == 'pull_request' }}`, and deploy groups use `cancel-in-progress: false`. (seen in `JasonLo/jasonlo.dev:.github/workflows/publish.yml`)

- **The default job timeout is a safe limit** → **Each job declares its own time limit.** A job that stops responding can block a runner for 6 hours. A specified `timeout-minutes` makes the job fail quickly and shows the problem. (seen in `simulation-based-inference/simulation-based-inference.github.io:.github/workflows/ci.yml`, which has no timeout)

- **`defaults: run: shell: bash` is optional** → **Each job sets its shell.** Without this setting, the runner OS selects the shell. Then `[[ ]]` and `set -euo pipefail` behave differently on Windows and show no error. (seen in `JasonLo/jasonlo.dev:.github/workflows/ci.yml`)

## Agent rules

- ALWAYS declare a `permissions` block on every workflow.
- NEVER use the repository default permissions.
- ALWAYS set `timeout-minutes` on every job.
- NEVER let a job use the 360-minute default timeout.
- ALWAYS set `cancel-in-progress` to true or to a condition for CI jobs.
- ALWAYS set `cancel-in-progress: false` for deploy jobs.
- ALWAYS add `defaults: run: shell: bash` to get the same shell behavior on all runners.
- NEVER trigger a write-privileged deploy step from the job that runs untrusted PR code.
- ALWAYS use `workflow_run` to start a privileged deploy after the CI workflow.
