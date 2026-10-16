# cheatsheet

This repo is a personal collection of cheatsheets that maintains itself. Each
cheatsheet gives a coding agent current context for a tool. Each cheatsheet
comes from how *you* use the tool.

A Claude Code skill makes each cheatsheet. The skill mines your GitHub repos for
real usage. It compares this usage with the current official docs of the tool.
Then it writes a short cheatsheet. The **Learnings** section corrects the usage
that is not current. Scheduled GitHub Actions keep the collection current.

All prose in this repo is in ASD-STE100 Simplified Technical English
(Constitution P-8).

See [`index.md`](index.md) for the current collection.

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/JasonLo/cheatsheet/main/scripts/install.sh | sh
```

This command clones the repo to `~/.cheatsheet`. It also adds an
[`@` import](https://code.claude.com/docs/en/memory) of `index.md` to your
user-level `~/.claude/CLAUDE.md`.

The import loads the index **into the context of your agent** when a session
starts. A URL in `CLAUDE.md` does not do this, because Claude Code does not get
URLs automatically. With the index in its context, the agent knows the
cheatsheets. It reads the related `cheatsheets/<slug>.md` before it acts.

To get the latest cheatsheets, run the same command again. The command runs
`git pull` and updates the block in `CLAUDE.md`. To remove all parts, run
`~/.cheatsheet/scripts/uninstall.sh`.

To change the install location, set `CHEATSHEET_DIR`. To change the target file,
set `CLAUDE_MD`.

## Make a cheatsheet

In Claude Code, start the `cheatsheet` skill with a use case and a named
target:

```
/cheatsheet outbound HTTP clients --target httpx
```

The skill does these steps:

1. It gets your GitHub identity with `gh`.
2. It collects the files where you use the target.
3. It finds the current best practice in context7 or in the official docs.
4. It writes `cheatsheets/<slug>.md`. This file has a reference snippet, your
   typical usage patterns, Learnings about concepts, and **Agent rules**. A
   coding agent can apply the Agent rules directly.
5. It updates the root `index.md` automatically.

The skill never shows a private repo. It does not write the name, slug, URL, or
text of a private repo. It gives patterns from private repos only in a general
form (Constitution P-7).

## Self-maintenance (GitHub Actions)

Workflows with
[`anthropics/claude-code-action`](cheatsheets/self-maintenance-claude-code-action.md)
keep the collection current. The scheduled workflows open only issues. You
select items in an issue with a comment, for example "1 and 3". Then a workflow
opens one pull request for your review. No workflow merges a pull request
automatically.

- **Monthly refresh.**
  [`.github/workflows/cheatsheet-refresh.yml`](.github/workflows/cheatsheet-refresh.yml)
  mines your repos again and compares each cheatsheet with the current docs. It
  opens **one issue with a table** of the cheatsheets whose meaning changed.
  Changes in wording or in the date do not count. If no meaning changed, it
  opens no issue.
- **Weekly recommender.**
  [`.github/workflows/cheatsheet-recommend.yml`](.github/workflows/cheatsheet-recommend.yml)
  scans your GitHub activity of the last 7 days. It compares the activity with
  the current cheatsheets. It opens **one issue with a table** of not more than 3
  new frameworks that no cheatsheet covers.
- **Generate from a selection.**
  [`.github/workflows/cheatsheet-generate.yml`](.github/workflows/cheatsheet-generate.yml)
  starts when you comment a selection on a recommendations issue or a refresh
  issue. It makes the selected cheatsheets with the skill. It opens one pull
  request with all of them. The merge closes the issue.
- **Staleness prune.**
  [`.github/workflows/cheatsheet-prune.yml`](.github/workflows/cheatsheet-prune.yml)
  finds the cheatsheets whose target you did not use for more than one year. It
  opens **one issue with a table** of these cheatsheets.
- **Delete from a selection.**
  [`.github/workflows/cheatsheet-delete.yml`](.github/workflows/cheatsheet-delete.yml)
  starts when you comment a selection on a staleness issue. It deletes the
  selected cheatsheets and opens one pull request. The merge closes the issue.

To delete one cheatsheet locally, run `uv run scripts/delete_cheatsheet.py <name>`.

### Setup

Add two repository secrets (Settings → Secrets and variables → Actions):

| Secret | Purpose | How to get it |
|---|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | Claude authentication for the action | Run `claude setup-token` locally. |
| `GH_SCAN_TOKEN` | **Read-only** fine-grained PAT to mine your repos | Give Contents: Read and Metadata: Read for all your repos. |

The workflows use `GH_SCAN_TOKEN` only to read data from your other repos. They
use the default `GITHUB_TOKEN` to write issues and pull requests in this repo.
If `GH_SCAN_TOKEN` is missing, each workflow stops at the start with a clear
message.

The workflows pin the third-party actions to commit SHAs. A comment such as `# v1` or
`# v6` shows the tag. Update these pins carefully.

## How the repo works

- The repo is spec-driven. The principles are in
  [`specs/CONSTITUTION.md`](specs/CONSTITUTION.md). The scope is in
  [`specs/INTENT/`](specs/INTENT/). I-1 covers the generation of cheatsheets. I-2
  covers the self-maintenance. I-3 covers the deletion of cheatsheets.
- `uv` manages the Python tools. The only executable code is in deterministic
  scripts:
  [`scripts/register_cheatsheet.py`](scripts/register_cheatsheet.py) makes the
  index, and [`scripts/delete_cheatsheet.py`](scripts/delete_cheatsheet.py)
  deletes a cheatsheet.
  [`scripts/gh_scan.py`](scripts/gh_scan.py) runs `gh` with the read-only scan
  token for the workflow agents.
- To run the tests, use `uv run --with pytest pytest`.
- The skill and the scheduled agents do all the work that needs judgment.
