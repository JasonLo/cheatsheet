# Self-maintenance with anthropics/claude-code-action

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from Claude Code Action docs (context7 `/anthropics/claude-code-action`, v1)._

## Reference snippet

```yaml
# .github/workflows/doc-cleaner-claude.yml: agent that runs on a schedule to maintain the repo
on:
  schedule: [{ cron: "23 1 * * 0" }]  # one time each week, on Sunday
  workflow_dispatch:          # always add this with schedule. Then you can start a test run manually.
permissions: { contents: write, pull-requests: write, id-token: write }  # least privilege. The action needs id-token.
concurrency: { group: doc-cleaner }  # only one run at a time
jobs:
  clean:
    runs-on: ubuntu-latest
    timeout-minutes: 20       # stop an agent that does not respond
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10  # v6
      - uses: anthropics/claude-code-action@41ea7642c1436fa0ee57aae58347904b71a5af27  # v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          claude_args: --max-turns 20 --allowedTools "Read,Glob,Edit,Write,Bash(gh pr:*)"
          prompt: |
            Audit README.md, CLAUDE.md, and docs/ against the codebase. Read CLAUDE.md first.
            Fix only what you can verify is wrong, and open a PR. If all is accurate, do nothing.
---
# .github/workflows/claude.yml: bot that answers @claude mentions
on:
  issue_comment: { types: [created] }
  issues: { types: [opened, assigned] }
jobs:
  claude:
    if: |                     # run only on an explicit mention, not on every comment
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
    runs-on: ubuntu-latest
    permissions: { contents: read, pull-requests: read, issues: read, id-token: write, actions: read }  # read-only bot
    steps:
      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10  # v6
      - uses: anthropics/claude-code-action@41ea7642c1436fa0ee57aae58347904b71a5af27  # v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          additional_permissions: |  # lets Claude read CI results on the PR
            actions: read
          # no prompt: Claude does the instruction in the comment that mentions it
```

## Typical usage patterns

- The same action has two separate modes: **scheduled maintenance agents** and an **interactive `@claude` responder**. One workflow never does both. (seen in `JasonLo/jasonlo.dev`, `JasonLo/skill-sommelier`, `JasonLo/uw-s3`)
- Scheduled agents trigger on an `on: schedule` cron and `workflow_dispatch`, and they contain the full task in a fixed `prompt:`. They limit work with `claude_args: --max-turns N`, a `concurrency` group, and `timeout-minutes`. (seen in `JasonLo/jasonlo.dev:.github/workflows/doc-cleaner-claude.yml`, `JasonLo/jasonlo.dev:.github/workflows/wcag-audit-claude.yml`)
- Interactive workflows trigger on `issue_comment` / `pull_request_review` events, and a long `if:` guard runs the job only when the body contains `@claude`. They pass no `prompt`, so Claude acts on the comment that triggered it. (seen in `JasonLo/skill-sommelier:.github/workflows/claude.yml`, `JasonLo/uw-s3:.github/workflows/claude.yml`)

## Learnings

- **A floating tag, for example `@v1`, is a stable, safe pin** → **A floating tag runs the code that someone last pushed to it**. A changed or compromised action then runs with your `contents: write` token. The full commit SHA is the trust boundary, so pin third-party actions to it. (seen in every workflow)
- **The prompt is the safety boundary** → **`permissions:` and `--allowedTools` are the boundary, and the prompt only states intent**. An agent with `contents: write` and the default tools can do anything that the token permits, for all prompt text. Limit both settings to the task. (seen in `JasonLo/jasonlo.dev:.github/workflows/doc-cleaner-claude.yml` and `JasonLo/uw-s3:.github/workflows/claude.yml`)
- **Grant the usual write scopes** → **Grant only the scopes that the job uses**. The doc and WCAG agents request `issues: write` but only open PRs, so the unused grant adds risk and gives no advantage. (seen in `JasonLo/jasonlo.dev:.github/workflows/wcag-audit-claude.yml`)

## Agent rules

- ALWAYS pin `anthropics/claude-code-action` and `actions/checkout` to a full commit SHA in production workflows.
- NEVER trust a floating tag, for example `@v1`, for a job that holds a write token.
- ALWAYS set `permissions:` to the minimum scopes that the task uses.
- ALWAYS give a Q&A or review bot only read scopes and `id-token: write`.
- NEVER give `contents: write` and `pull-requests: write` to a job that does not fix code and open PRs.
- NEVER grant a write scope, for example `issues: write`, that the task does not use.
- ALWAYS limit the tools with `--allowedTools` in `claude_args`.
- ALWAYS treat `permissions:` and the allowed tools as the security boundary.
- NEVER treat the prompt text as a security boundary.
- ALWAYS restrict interactive workflows to a direct `@claude` mention in the `if:` condition.
- ALWAYS add `additional_permissions: actions: read` when Claude must read CI results on a PR.
- ALWAYS put the permanent guidance for the codebase in `CLAUDE.md`.
- ALWAYS limit the workflow `prompt:` to the trigger and the task.
- ALWAYS set `timeout-minutes` and a `concurrency` group on scheduled agents.
- ALWAYS pair `schedule:` with `workflow_dispatch:`.
- ALWAYS tell a scheduled agent to open no PR when it finds nothing to change.
- ALWAYS use `fetch-depth: 0` when the agent examines git history.
- ALWAYS authenticate with `claude_code_oauth_token` or an API key from a GitHub secret.
- NEVER hardcode credentials in a workflow.
