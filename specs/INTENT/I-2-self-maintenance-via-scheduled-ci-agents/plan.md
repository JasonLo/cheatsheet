# Implementation Plan — I-2 O-6: Comment-to-generate workflow (`cheatsheet-generate.yml`)

> This file is an agent-writable working doc that an agent can generate again. The source of truth is `intent.md`. Scope: this plan covers only outcome **O-6**. The other five outcomes already pass.

## Goal

Complete the loop of recommend, select, generate, and review fully in the GitHub web UI.
The repository owner comments a topic selection on an open cheatsheet-recommendations issue, for example "1 and 3".
Then a guarded workflow generates each selected sheet with the I-1 `cheatsheet` skill.
The workflow opens exactly one PR for each selected topic, and a human reviews each PR. There is no local step and no auto-merge.

This work needs these changes:
1. Add a new workflow file `.github/workflows/cheatsheet-generate.yml`.
2. Make a related edit to `.github/workflows/cheatsheet-recommend.yml`. The edit changes the "Generate with" column of the table.
3. Add concrete success criteria to `specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/web-end-to-end-generate-from-selection.md`.

The intent sets these exact requirements: `intent.md` O-6, its two tests, and the locked event-driven constraint.
The `shell:` test checks the filename `cheatsheet-generate.yml` and the tokens `issue_comment`, `concurrency`, and `timeout-minutes`.
It also checks that no floating `@vN` tag is present. For this reason, the filename and those four facts are fixed.

---

## 1. Trigger + guard conditions

### Triggers

```yaml
on:
  issue_comment:
    types: [created]
  workflow_dispatch:
    inputs:
      issue_number:
        description: "Recommendations issue number to read the table from"
        required: true
      selection:
        description: 'Topic numbers to generate, e.g. "1 and 3"'
        required: true
```

`workflow_dispatch` has two inputs because manual mode has no `github.event.comment` to read. The agent must get the issue and the numbers from the inputs.
The two current workflows use an empty `workflow_dispatch: {}`. This workflow needs inputs, so that manual tests can run the real generate path.

### The job-level `if:` guard

The `issue_comment` path runs only when ALL the conditions below are true. The dispatch path always runs:

```yaml
jobs:
  generate:
    if: >
      github.event_name == 'workflow_dispatch' ||
      (github.event_name == 'issue_comment' &&
       github.event.issue.pull_request == null &&
       github.event.issue.state == 'open' &&
       github.event.comment.user.login == github.repository_owner &&
       startsWith(github.event.issue.title, 'Cheatsheet recommendations'))
```

Reasons for each guard:

- **Owner-only**: `github.event.comment.user.login == github.repository_owner`. This value is the repo owner. It is portable and is not a hardcoded login.
- **Recommendations-issue marker**: `startsWith(github.event.issue.title, 'Cheatsheet recommendations')`. This matches the title that the recommender writes (`Cheatsheet recommendations — week of <YYYY-MM-DD>`).
  The title IS the marker, so the issue does not need an extra label.
- **Open issue only**: `github.event.issue.state == 'open'`.
- **Not a PR comment**: `github.event.issue.pull_request == null`. This is necessary because `issue_comment` also runs for PR comments.

The prompt adds a second check. Before any write, it uses `gh issue view` to confirm again that the issue is open and the title matches.
The `if:` is the real security boundary. The permissions and allowedTools enforce the intent, and the prose only states it.

### CRITICAL implication: `issue_comment` runs from the default branch

A workflow that `issue_comment` starts always runs the version on the **default branch** (`main`). Open PRs have no effect on this.
Write these results in a comment at the top of the file:

1. **This workflow works only after you merge it to `main`.** You cannot test the `issue_comment` path from a feature branch. For this reason, the `workflow_dispatch` path has inputs.
2. You must also merge the related edit to `cheatsheet-recommend.yml` to `main`. Before that merge, new recommendations do not have the correct instruction.

---

## 2. Map "1 and 3" → use-case + target

The numbers are row indices into the markdown table that the recommender wrote. The table has these columns:

```
| # | Topic (use case) | Target | Why now | Evidence | Generate with |
```

To resolve a selection, the agent reads the issue body and parses the table. For each selected `#`, it gets **Topic (use case)** (col 2) and **Target** (col 3, in backticks).
These values are the inputs of the I-1 skill. The use case is free text, and `--target` is the library or tool.

This parsing needs judgment, because the comment is free-form ("1 and 3", "1,3", or "1 & 3") and the table is natural-language markdown.
For this reason, P-6 puts the parsing in the agent prompt, not in a rigid parser. The agent does these steps:

1. Run `gh issue view <n> --json title,body,state` with the default token on THIS repo to get the table.
2. Parse the comment body for the selected integers. Accept "1 and 3", "1,3", "1 & 3", and "1 3".
3. For each selected number, read that table row → `(use_case, target)`.
4. If a number has no matching row, skip it and report it. Never invent a topic.

In `workflow_dispatch` mode, the issue number and selection come from `inputs.issue_number` / `inputs.selection`. All the later steps are the same.

The workflow gives the comment body and event fields to the agent through `env:`. As a result, the prompt stays static.
The workflow never puts untrusted comment text into the prompt string. This prevents prompt injection through YAML interpolation.
For example: `SELECTION_COMMENT: ${{ github.event.comment.body }}`, `ISSUE_NUMBER: ${{ github.event.issue.number || inputs.issue_number }}`, `DISPATCH_SELECTION: ${{ inputs.selection }}`.

---

## 3. The `claude-code-action` invocation

Copy the structure of `cheatsheet-refresh.yml`. It is the closest example because it generates sheets, makes branches, and opens one PR for each sheet.

### Pins + auth

Use the same SHA pins as the two current workflows:
- `actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10  # v6`
- `anthropics/claude-code-action@41ea7642c1436fa0ee57aae58347904b71a5af27  # v1`
- `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}`, `github_token: ${{ github.token }}`.

Check out with `fetch-depth: 0`, so that each topic branch starts cleanly from `main`.

### `permissions:` (least privilege)

The job opens PRs and pushes branches in THIS repo. It does NOT write issues:

```yaml
permissions:
  contents: write        # push branches, commit generated sheet
  pull-requests: write   # gh pr create
  id-token: write        # OIDC, required by the action
```

Do NOT add `issues: write` unless you adopt the optional ack-comment feature. The default is to skip the ack.

### `concurrency` + `timeout-minutes`

```yaml
concurrency:
  group: "cheatsheet-generate-${{ github.event.issue.number || inputs.issue_number }}"
  cancel-in-progress: false
```

The group key is the issue number. Selections on different issues can then run in parallel.
Repeated comments on the same issue run one after the other. Then two runs cannot both try to create the same branch.
The setting `cancel-in-progress: false` puts a new run in a queue and does not stop the old run.
Use `timeout-minutes: 60`. This is between the 30 minutes of the recommender and the 90 minutes of refresh. A selection has a maximum of 3 sheets.

### `env`

Use the two-token rule from O-3:

```yaml
env:
  GH_TOKEN: ${{ github.token }}                 # writes (branch push, gh pr create) — THIS repo only
  GH_SCAN_TOKEN: ${{ secrets.GH_SCAN_TOKEN }}   # read-only cross-repo mining inside the skill
  ISSUE_NUMBER: ${{ github.event.issue.number || inputs.issue_number }}
  SELECTION_COMMENT: ${{ github.event.comment.body }}
  DISPATCH_SELECTION: ${{ inputs.selection }}
```

Keep the `GH_SCAN_TOKEN` preflight step that fails immediately if the token is missing. The skill mines the repos of the user, so the scan token is necessary.

### `--allowedTools` boundary

This is the security boundary. Start from the refresh toolset and ADD `gh issue view`.
Allow gh issue and PR reads, branch push, gh pr create, and uv run. The set **must NOT allow any merge**:

```
--max-turns 120
--allowedTools "Read,Glob,Grep,Edit,Write,WebSearch,WebFetch,Bash(date:*),Bash(gh api:*),Bash(gh search code:*),Bash(gh search commits:*),Bash(gh repo list:*),Bash(gh repo view:*),Bash(gh issue view:*),Bash(gh issue list:*),Bash(gh pr list:*),Bash(gh pr create:*),Bash(git status:*),Bash(git diff:*),Bash(git switch:*),Bash(git checkout:*),Bash(git restore:*),Bash(git add:*),Bash(git commit:*),Bash(git push:*),Bash(uv run:*)"
```

Notes about the boundary:
- **Allowed reads**: `gh issue view`, `gh issue list`, `gh pr list`, and the cross-repo reads with the scan token (`gh search code/commits`, `gh api`, `gh repo view`).
- **Allowed writes**: only `git push` and `gh pr create`.
- **Deliberate omissions**: no `gh pr merge`, no `gh pr review`, and no `Bash(gh pr:*)` wildcard, because the wildcard lets a merge occur.
  Also no `gh issue create/edit/comment` and no `gh api -X`/`--method` mutations. The narrow grants for each subcommand enforce "no auto-merge."
- `--max-turns 120`: a selection generates a maximum of 3 sheets from the start. Each sheet needs the full mine→ground→author sequence.
  For this reason, the value is more than the 60 of the recommender and less than the 150 of refresh.

### Prompt structure

Use the structure of the refresh prompt: Orientation → Two-token rule → Privacy → Task (loop for each topic) → Finish/report.

- **Orientation**: read `CLAUDE.md`, `specs/CONSTITUTION.md`, and `.claude/skills/cheatsheet/SKILL.md` ("SKILL.md is your generation procedure").
  Get the login with `gh api user --jq .login`. Record the date with `date -u +%Y-%m-%d`. Note that the run starts on the default branch.
- **Resolve the selection** (specific to O-6): use this prompt text.
  "Read `$ISSUE_NUMBER` with `gh issue view "$ISSUE_NUMBER" --json title,body,state`. Make sure that the issue is OPEN.
  Make sure that the title starts with `Cheatsheet recommendations`. If not, STOP and open no PR. Parse the markdown table of the issue.
  The selected numbers come from `$SELECTION_COMMENT` (issue_comment) or `$DISPATCH_SELECTION` (manual). Accept '1 and 3', '1,3', and '1 & 3'.
  For each selected #, get the Topic (col 2) and the Target (col 3). These are the I-1 inputs.
  Skip numbers that have no matching row and report them. Never invent a topic."
- **Two-token rule** (NON-NEGOTIABLE): run each cross-repo read through `uv run scripts/gh_scan.py`. Use plain `gh`/`git` for writes (branch push, `gh pr create`) and for the issue read.
  Never read other repos with the default token. Never write with the scan token. Add this text: "You may NEVER merge, approve, or close anything. You only open PRs."
- **Privacy P-7**: find the visibility of each mined repo. Never put the name, slug, URL, or exact code of a private repo in a committed file or in PR text.
  Make private patterns general. You can cite public repos.
- **Task — the loop for each topic** (§4).
- **Finish**: report the issue that the agent read, the parsed selection, the resolved topics, and the opened PRs with their branch names.
  Also report all numbers that the agent skipped, found as duplicates, or did not resolve. If the agent generated nothing, it opens zero PRs and says so.

---

## 4. Loop for each topic: branch, isolation, index, PR shape

Use the refresh pattern for each sheet again, but use the selected topics as the key. **For each selected `(use_case, target)`:**

1. **Dup-PR guard** (before any write): compute the slug, then run `gh pr list --state open --search "generate <slug>" --json headRefName`. If an open PR exists for this branch, SKIP the topic.
   Also, if the sheet already exists in `cheatsheets/<slug>.md` on main, skip it and report "already covered".
   This workflow generates NEW sheets. The monthly job refreshes the current sheets.

2. **Make a branch from the default branch**: use `auto/generate/<slug>`. `<slug>` is the `use case + target` in lowercase with hyphens, exactly as the skill computes it.
   Make one branch for each topic with `git switch -c auto/generate/<slug>`. Add `-<YYYY-MM>` only if a collision with an old closed branch is possible.

3. **Generate the sheet** with the I-1 skill workflow. Write `cheatsheets/<slug>.md` with the exact necessary structure.
   The structure is: H1 `# <use case> with <target>`, grounding line, Reference snippet, Typical usage patterns (max 3), Learnings (max 3), and Agent rules.

4. **Generate the index again deterministically** (P-6 / P-4): run `uv run scripts/register_cheatsheet.py` and stage `index.md`.
   Refresh stages the index again only if a title changed. But a NEW sheet always adds a row to `index.md`. For this reason, `index.md` always changes, and you must always stage it.

5. **Commit, push, and open ONE PR**:
   - Run `git add cheatsheets/<slug>.md index.md`, commit, and run `git push -u origin auto/generate/<slug>`.
   - Run `gh pr create` with the title `feat(cheatsheet): add <slug>`. The body gives a summary of the sheet (use case + target) and the doc source that grounds it.
     The body also has `Closes selection from #<ISSUE_NUMBER>`, which links to the recommendations issue.
     Do NOT put a raw diff in the body. NEVER put a private repo identifier or private content in it (P-7). There is no auto-merge, and a human reviews the PR.

6. **Isolate the next topic**: run `git switch <default-branch>` and `git restore .` before the next selected topic. Then each PR has only its own sheet and its own index.md row.

The structure enforces **one PR for each topic**. It uses one branch for each slug, a restore between topics, and the dup-guard.
Three selected numbers give a maximum of three PRs. The number is smaller if some topics are duplicates, already covered, or not resolved.

---

## 5. Companion change to `cheatsheet-recommend.yml`

The locked constraint has a requirement for the "Generate with" instruction in the recommendations issue. The instruction must show the comment-to-generate path, not a local `/cheatsheet` command.
At this time, the table template has a fixed local command:

```
| 1 | <use case> | `<target>` | <one line> | `owner/repo` (...) | `/cheatsheet <use case> --target <target>` |
```

That does not agree with the "no local execution" rule of O-6. Edit the table template in the prompt, so that the column does not tell the user to run a local command.

**Recommended: Option A, which removes the column** (P-3 simplicity). Remove the `| Generate with |` header, its separator cell, and the `/cheatsheet ...` cell.
Keep the current closing line `Reply with the numbers to add (e.g. "1 and 3"); I'll generate those cheatsheets.` A reply to this line now starts the generate workflow.
Make the closing request clearer: the **repository owner** must comment on **this open issue**. Do not change the permissions or tools of the recommender.

Option B is an alternative. It keeps the column but changes the cell to a text such as `Comment "1" on this issue`.

Note: the "(O-N)" markers inside `SKILL.md` are only cosmetic. They refer to the outcomes of the I-1 intent, not to this I-2 O-6. Do not change them.

---

## 6. Satisfy the two tests of O-6

### Test 1 — the `shell:` structural test

```
test -f .github/workflows/cheatsheet-generate.yml
&& grep -ql 'issue_comment' .github/workflows/cheatsheet-generate.yml
&& grep -ql 'concurrency' .github/workflows/cheatsheet-generate.yml
&& grep -ql 'timeout-minutes' .github/workflows/cheatsheet-generate.yml
&& ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/cheatsheet-generate.yml
```

The design satisfies each clause. It has the exact filename, `on: issue_comment:`, a `concurrency:` block, and `timeout-minutes: 60`.
Both `uses:` lines have SHA pins, and the version is only in a trailing `# v6`/`# v1` comment.
The regex requires `@vN` at the end of the line, so the comment does not cause a failure. The change must also not break the O-5 structural test for the full directory.

### Test 2 — the agent check (`checks/web-end-to-end-generate-from-selection.md`)

Add concrete pass conditions with file:line citations to its `## Success criteria`. Only this part is writable, because a human owns the SHALL:

Suggested text: examine `.github/workflows/cheatsheet-generate.yml` and cite file:line evidence for each item:
- **Trigger + guard**: `on: issue_comment: types: [created]` is present together with `workflow_dispatch`.
  The job `if:` limits the run to (a) the repository owner, (b) an OPEN issue, and (c) a recommendations issue (title-prefix `Cheatsheet recommendations`). It also (d) excludes PR comments.
  The path for `workflow_dispatch` accepts an issue number and a selection. Then you can test the path without a live comment.
- **Selection → inputs mapping**: the prompt tells the agent to read the issue body with `gh issue view` and to parse the markdown table.
  The agent maps each selected number to its (use case, target) row. It skips numbers that have no matching row and never invents topics.
- **Generation with the I-1 skill**: the prompt tells the agent to follow `.claude/skills/cheatsheet/SKILL.md` to write `cheatsheets/<slug>.md`.
  The prompt also tells it to run `uv run scripts/register_cheatsheet.py` to generate `index.md` again.
- **One human-reviewed PR for each topic, no auto-merge**: the workflow uses one branch for each topic (`auto/generate/<slug>`) and `git restore`/`git switch` isolation between topics.
  It has a dup-PR guard with `gh pr list` and one `gh pr create` for each topic. It has NO merge, approve, or close.
  `--allowedTools` has `gh pr create` and `git push`, but it does not have `gh pr merge`, `gh pr review`, or the wildcard `gh pr:*`.
  `permissions:` gives only `contents: write`, `pull-requests: write`, and `id-token: write` (no `issues: write`).
- **Hardening**: both third-party actions have SHA pins. A `concurrency` group is present, and the job sets `timeout-minutes`.
- **Two-token rule (O-3)**: each cross-repo read runs through `uv run scripts/gh_scan.py`. Writes use the default `github.token`. The `GH_SCAN_TOKEN` preflight is present.
- **Privacy (P-7)**: the prompt does not allow the name, slug, URL, or exact content of a private repo in committed files or PR text. It requires general descriptions.
- **Web-only loop**: make sure that the table in the related `cheatsheet-recommend.yml` does not tell the user to run a local `/cheatsheet` command.
  The only call to action is to comment the number(s). Then the loop completes in the web UI.

---

## 7. Step-by-step task list

1. **Create `.github/workflows/cheatsheet-generate.yml`** with these parts:
   - A comment at the top of the file. It gives the purpose and the caveat that "issue_comment runs from default branch".
   - `on: issue_comment.created` and `workflow_dispatch` with the `issue_number`/`selection` inputs.
   - The job `if:` guard (§1) and `permissions:` (contents/pull-requests/id-token write).
   - `concurrency` with the issue number as its key, and `timeout-minutes: 60`.
   - `env` with the two tokens and the three event/input variables, and the `GH_SCAN_TOKEN` preflight.
   - Checkout with a SHA pin and `fetch-depth: 0`.
   - `claude-code-action` with a SHA pin, `--max-turns 120`, the `--allowedTools` set without merge, and the prompt (§3–§4).
2. **Edit `.github/workflows/cheatsheet-recommend.yml`**: remove the "Generate with" column (header, separator, and the `/cheatsheet ...` cell). Keep the closing reply-to-generate line and make it clearer (Option A, §5).
3. **Edit `specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/web-end-to-end-generate-from-selection.md`**: replace the placeholder `## Success criteria` with the new criteria (§6).
   Change only the section that is not the SHALL.
4. **Verify the `shell:` test locally**: run the exact command from the O-6 citation. It uses only read-only grep and test. Also run the floating-tag scan for the full directory from O-5.
5. **(Operational, out of code scope)** Make sure that the secrets `GH_SCAN_TOKEN` and `CLAUDE_CODE_OAUTH_TOKEN` exist.
   Merge to `main`. The `issue_comment` trigger works only after this merge.

## Risks / edge cases

- **Comment on a closed issue** → `state == 'open'` and the check again in the prompt block it.
- **Non-owner comment** → `comment.user.login == repository_owner` blocks it.
- **Unrelated issue** → the title-prefix marker blocks it. For a comment that is not a selection, the agent finds no valid numbers.
  Then it opens zero PRs and reports "no valid selection."
- **Ambiguous or no-match selection** ("5" with 3 rows, or "all") → skip the numbers that the agent cannot resolve and report them.
  For "all", the agent can map to all rows, but it must report its interpretation. Never invent a topic.
- **Topic already covered** → the dup-PR guard and the check for a current file skip it. No duplicate occurs.
- **Repeated comments at the same time** → the `concurrency` group for each issue runs them one after the other. The setting `cancel-in-progress: false` puts them in a queue.
  The deterministic branch name and the dup-guard prevent double PRs.
- **Concurrency with the weekly recommender** → the two workflows use different groups and make different artifacts (an issue, or a branch and a PR). They do not conflict.
- **Prompt injection through the comment or issue body** → the workflow gives untrusted text through `env` and does not put it into the prompt. The prompt treats it as data.
  The real protection is `--allowedTools` (no merge) and least-privilege `permissions:`.
- **The issue_comment-from-default-branch problem** → the file documents it. `workflow_dispatch` covers tests before the merge.
- **No `GH_SCAN_TOKEN`** → the preflight fails immediately with an error that tells the user what to do.

## Manual end-to-end verification procedure

1. **Before the merge (branch), dispatch path**: create a temporary test issue with the title `Cheatsheet recommendations — week of <today>`.
   Give it a table of 2–3 rows in the same shape as the recommender table. Run it with `workflow_dispatch`, `issue_number=<that issue>`, and `selection="1 and 3"`.
   Expect two `auto/generate/<slug>` branches and exactly two PRs. Each PR has one new sheet and one `index.md` row.
   The PR text has no private identifiers, and no merge occurs. The `issue_comment` trigger does not run from a branch, so dispatch is the only test before the merge.
2. **Edge checks with dispatch**: run with `selection="5"` (out of range). Expect zero PRs and a report of the number as not resolved.
   Run two times with the same selection. Expect that the second run opens no duplicate.
3. **After the merge (main), real comment path**: merge both file changes to `main`. Let the recommender open a real issue, or use a test issue with the correct title again.
   Then, as the owner, comment `1 and 3`. Make sure that the workflow starts, the guards pass, and the same PRs for each topic appear.
   Make sure that a comment from a different user does NOT start the workflow. A comment on a closed or renamed issue must also NOT start it.

---

## Critical files
- `.github/workflows/cheatsheet-generate.yml` — **new**, the O-6 workflow
- `.github/workflows/cheatsheet-recommend.yml` — **edit**, "Generate with" column → comment-to-generate
- `specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/web-end-to-end-generate-from-selection.md` — **edit**, improve `## Success criteria`
- `.github/workflows/cheatsheet-refresh.yml` — reference (for each sheet: branch/PR/restore/dup-guard pattern)
- `.claude/skills/cheatsheet/SKILL.md` — reference (generation procedure, input shape, slug rule)
