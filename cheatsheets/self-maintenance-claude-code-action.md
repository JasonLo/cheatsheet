# Self-maintenance with anthropics/claude-code-action

_Grounded in JasonLo's repos as of 2026-06-05; current practice per Claude Code Action docs (context7 `/anthropics/claude-code-action`, v1)._

## Reference snippet

```yaml
# .github/workflows/doc-cleaner-claude.yml — scheduled self-maintenance agent
name: "Documentation Cleaner"

on:
  schedule:
    - cron: "23 1 * * 0"   # weekly, Sunday
  workflow_dispatch:        # always pair with schedule so you can test on demand

permissions:                # least privilege: this job only opens PRs
  contents: write
  pull-requests: write
  id-token: write           # OIDC — required by the action

concurrency:
  group: "doc-cleaner"      # one run at a time; no pile-ups

jobs:
  clean:
    runs-on: ubuntu-latest
    timeout-minutes: 20     # bound a hung agent
    steps:
      - uses: actions/checkout@v6   # pin to a full commit SHA in production
        # with: { fetch-depth: 0 }  # only if the prompt reasons about git history

      - uses: anthropics/claude-code-action@v1   # pin to a commit SHA, not @v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          claude_args: |
            --max-turns 20
            --allowedTools "Read,Glob,Edit,Write,Bash(gh pr:*)"
          prompt: |
            Audit README.md, CLAUDE.md, and docs/ against the codebase.
            Project orientation lives in CLAUDE.md — read it first.
            Fix only what you can verify is wrong. Open a PR if you changed
            anything; if everything is accurate, do nothing and say so.
```

```yaml
# .github/workflows/claude.yml — interactive @claude responder
on:
  issue_comment: { types: [created] }
  pull_request_review_comment: { types: [created] }
  issues: { types: [opened, assigned] }
  pull_request_review: { types: [submitted] }

jobs:
  claude:
    if: |                   # gate on an explicit mention — don't run on every comment
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@claude')) ||
      (github.event_name == 'issues' && contains(github.event.issue.body, '@claude'))
    runs-on: ubuntu-latest
    permissions:            # a Q&A/review bot can be read-only
      contents: read
      pull-requests: read
      issues: read
      id-token: write
      actions: read         # so Claude can read CI results on the PR
    steps:
      - uses: actions/checkout@v6
        with: { fetch-depth: 1 }
      - uses: anthropics/claude-code-action@v1
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          additional_permissions: |
            actions: read
          # no prompt: Claude follows the instruction in the comment that tagged it
```

## Typical usage patterns

- Two distinct modes of the same action: **scheduled autonomous maintenance agents** and an **interactive `@claude` responder** — never one workflow trying to be both. (`JasonLo/jasonlo.dev`, `JasonLo/skill-sommelier`, `JasonLo/uw-s3`)
- Scheduled agents trigger on `on: schedule` cron + `workflow_dispatch`, carry the whole task as a baked-in `prompt:`, cap work with `claude_args: --max-turns N`, and add a `concurrency` group + `timeout-minutes`. (`JasonLo/jasonlo.dev:.github/workflows/doc-cleaner-claude.yml`, `JasonLo/jasonlo.dev:.github/workflows/wcag-audit-claude.yml`)
- Interactive workflows fire on `issue_comment` / `pull_request_review` events and use a long `if:` guard so the job only runs when the body contains `@claude`; they pass no `prompt`, letting Claude act on the triggering comment. (`JasonLo/skill-sommelier:.github/workflows/claude.yml`, `JasonLo/uw-s3:.github/workflows/claude.yml`)

## Learnings

- **"`@v1` is a stable, safe pin"** → **a floating tag re-pulls whatever was last pushed to it.** Every run re-fetches that tag, so a compromised or changed action executes with your `contents: write` token. Pin third-party actions (`claude-code-action`, `actions/checkout`) to a full commit SHA and bump deliberately; the tag is convenience, the SHA is the trust boundary. (seen in every workflow)
- **"The prompt is the safety boundary"** → **the workflow's `permissions:` and `--allowedTools` are the boundary; the prompt is intent, not enforcement.** A scheduled agent with `contents: write` and the default toolset can do anything the token permits no matter how firmly the prose says "be conservative, don't delete." Constrain both dials to the task; the read-only Q&A bot is the right instinct, the broad-write agent leaning on prose is the risk. (`JasonLo/jasonlo.dev:.github/workflows/doc-cleaner-claude.yml` vs `JasonLo/uw-s3:.github/workflows/claude.yml`)
- **"Grant the action the usual write scopes"** → **grant exactly the scopes the job exercises.** The doc and WCAG agents request `issues: write` but only ever open PRs — an unused write grant is standing blast radius for no benefit. Match `permissions:` to what the task actually performs (PRs → `contents`+`pull-requests`; comments-only → read + `id-token`). (`JasonLo/jasonlo.dev:.github/workflows/wcag-audit-claude.yml`)

## Agent rules

- ALWAYS pin `anthropics/claude-code-action` and `actions/checkout` to a full commit SHA in production workflows; NEVER trust a floating tag like `@v1` for a job that holds a write token.
- ALWAYS set `permissions:` to the minimum the task exercises: a Q&A/review bot is read-only + `id-token: write`; only a fix-and-PR agent needs `contents: write` + `pull-requests: write`.
- NEVER grant a write scope (e.g. `issues: write`) the prompt never uses.
- ALWAYS constrain tools with `--allowedTools` in `claude_args`; treat `permissions:` + allowed tools as the security boundary, NEVER the prompt prose.
- ALWAYS gate interactive workflows on an explicit `@claude` mention via the `if:` condition so the job doesn't run on every comment.
- ALWAYS add `additional_permissions: actions: read` when Claude needs to read CI results on a PR.
- ALWAYS put durable codebase orientation in `CLAUDE.md` (the action reads it automatically); keep the workflow `prompt:` to the trigger and the task.
- ALWAYS set `timeout-minutes` and a `concurrency` group on scheduled agents so a hung or overlapping run can't pile up.
- ALWAYS pair `schedule:` with `workflow_dispatch:` so the agent can be triggered manually for testing.
- ALWAYS instruct a scheduled agent to no-op (open no PR) when it finds nothing to change.
- ALWAYS use `fetch-depth: 0` when the agent reasons about git history (dependency drift, recent commits, changelog accuracy); a shallow checkout hides the past.
- ALWAYS authenticate via `claude_code_oauth_token` (or an API key) from a GitHub secret; NEVER hardcode credentials.
