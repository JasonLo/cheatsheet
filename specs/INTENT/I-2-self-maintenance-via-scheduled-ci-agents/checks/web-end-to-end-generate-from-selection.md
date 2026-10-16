# Agent check: An owner comment on an issue makes the selected cheatsheets and opens one pull request.

## SHALL

**WHEN** the owner comments a selection on an open recommendations or refresh issue **THE SYSTEM SHALL** open exactly one pull request for the run. An example of a selection is "1 and 3". For a recommendations issue, the workflow makes each selected cheatsheet with the I-1 skill. For a refresh issue, the workflow makes each selected cheatsheet again. The pull request contains all selected cheatsheets and the `index.md` update. A person reviews the pull request. The loop needs no local step. The user can do the recommend → select → generate → review loop in the GitHub web interface. The same applies to the refresh → select → regenerate → review loop. [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/web-end-to-end-generate-from-selection.md]

## Success criteria

- Inspect `.github/workflows/cheatsheet-generate.yml`. Also inspect `.github/workflows/cheatsheet-recommend.yml` and `.github/workflows/cheatsheet-refresh.yml`.
- Cite file:line evidence for each condition below.
- PASS only if all conditions are true. FAIL if one condition is missing or if the evidence contradicts it.
- **Trigger and guard for the two issue types.** The workflow has `on: issue_comment: types: [created]` and `workflow_dispatch`.
  - The job `if:` accepts a comment only from the repo owner (`github.event.comment.user.login == github.repository_owner`).
  - The job `if:` accepts a comment only on an open issue (`github.event.issue.state == 'open'`).
  - The job `if:` accepts a title that starts with `Cheatsheet recommendations` or `Cheatsheet refresh`. It must accept the two prefixes.
  - The job `if:` rejects a comment on a pull request (`github.event.issue.pull_request == null`).
  - The `workflow_dispatch` path accepts an issue number and a selection. Then a person can test the loop with no live comment.
- **Mode from the issue title.** A `Cheatsheet recommendations …` title sets **generate mode**. In this mode, the selected rows are new sheets.
  - A `Cheatsheet refresh …` title sets **refresh mode**. In this mode, the selected rows are current sheets to make again.
  - In the two issue types, column 2 is the use case and column 3 is the target in backticks.
- **Map the selection to inputs.** The prompt tells the agent to read the issue body with `gh issue view` and parse the markdown table.
  - The agent maps each selected number to its row of use case and target.
  - The agent skips a number with no row. It never invents a topic.
  - The workflow passes the selection text through `env` (`SELECTION_COMMENT`, `DISPATCH_SELECTION`, `ISSUE_NUMBER`). It does not put this text directly in the prompt string.
- **Generation with the I-1 skill.** The prompt tells the agent to follow `.claude/skills/cheatsheet/SKILL.md` to write `cheatsheets/<slug>.md`.
  - The agent runs `uv run scripts/register_cheatsheet.py` to update `index.md`.
  - In generate mode, the agent always stages `index.md`. In refresh mode, it stages `index.md` only when the title changed.
- **One pull request for the run, with no automatic merge.** One run branch holds all selected sheets.
  - The branch is `auto/generate/from-issue-<N>` in generate mode and `auto/refresh/from-issue-<N>` in refresh mode.
  - The agent does not change branches or run `git restore` between topics.
  - The agent runs `register_cheatsheet.py` one time, after it writes all sheets.
  - A guard runs `gh pr list --head <branch>` and stops if a pull request for the run branch exists.
  - The agent runs `gh pr create` exactly one time.
  - The title is `feat(cheatsheet): add selected sheets from #<N>` in generate mode. It is `chore(cheatsheet): refresh selected sheets from #<N>` in refresh mode.
  - Generate mode skips a slug that has a sheet. Refresh mode skips a slug that has no sheet, and it never makes a new sheet.
  - The last line of the pull request body is exactly `Closes #<N>`. Then the merge closes the source issue (O-7).
  - `--allowedTools` includes `gh pr create` and `git push`. It does not include `gh pr merge`, `gh pr review`, or a wildcard `gh pr:*`.
  - `permissions:` gives `contents: write`, `pull-requests: write`, `id-token: write`, and `issues: write`.
  - The workflow uses `issues: write` only to add the 👀 reaction to the comment that started the run.
- **Hardening.** The workflow pins `actions/checkout` and `anthropics/claude-code-action` to a full commit SHA, not to a tag such as `@vN`.
  - The workflow sets a `concurrency` group and `timeout-minutes`.
- **Two-token rule (O-3).** The prompt runs each cross-repo read through `uv run scripts/gh_scan.py`, which uses `GH_SCAN_TOKEN`.
  - Writes to this repo and the issue read use the default `github.token`.
  - A preflight step checks `GH_SCAN_TOKEN`.
- **Privacy (P-7).** The prompt does not allow the name, slug, URL, or text of a private repo in a committed file or in pull request text.
  - The prompt requires a general form for private patterns. It permits cites of public repos.
- **Web-only loop for the two issue sources.** The issues from `cheatsheet-recommend.yml` and from `cheatsheet-refresh.yml` do not tell the user to run a local `/cheatsheet` command.
  - The only request in each issue is to comment the numbers on the issue. This comment starts this workflow.
  - Then the two loops complete in the GitHub web interface with no local step.
