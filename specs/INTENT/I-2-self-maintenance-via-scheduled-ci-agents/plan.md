# Implementation Plan — I-2 O-6: Comment-to-generate workflow (`cheatsheet-generate.yml`)

> Agent-writable, regenerable working doc. `intent.md` is the source of truth.
> Scope: outcome **O-6** only (the other five outcomes are already satisfied).

## Goal

Close the recommend → select → generate → review loop entirely in the GitHub web UI. When the repository owner comments a topic selection (e.g. "1 and 3") on an open cheatsheet-recommendations issue, a guarded workflow generates each selected sheet via the I-1 `cheatsheet` skill and opens exactly one human-reviewed PR per selected topic — no local step, no auto-merge.

This requires:
1. A new workflow file `.github/workflows/cheatsheet-generate.yml`.
2. A companion edit to `.github/workflows/cheatsheet-recommend.yml` (the table's "Generate with" column).
3. Enriching `specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/web-end-to-end-generate-from-selection.md` with concrete success criteria.

The intent mandates this exactly: `intent.md` O-6 + its two tests, and the locked event-driven constraint. The `shell:` test asserts the filename `cheatsheet-generate.yml` and the tokens `issue_comment`, `concurrency`, `timeout-minutes`, plus no floating `@vN` tag — so the filename and those four facts are non-negotiable.

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

`workflow_dispatch` carries two inputs because in manual mode there is no `github.event.comment` to read — the agent needs to be told which issue and which numbers. (The existing two workflows use empty `workflow_dispatch: {}`; here we need inputs so manual testing can exercise the real generate path.)

### The job-level `if:` guard

Three conditions must ALL hold for the `issue_comment` path; the dispatch path always runs:

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

Guard rationale:

- **Owner-only**: `github.event.comment.user.login == github.repository_owner` (resolves to the repo owner; portable, not a hardcoded login).
- **Recommendations-issue marker**: `startsWith(github.event.issue.title, 'Cheatsheet recommendations')` — matches the title the recommender writes (`Cheatsheet recommendations — week of <YYYY-MM-DD>`). The title IS the marker; no extra label needed.
- **Open issue only**: `github.event.issue.state == 'open'`.
- **Not a PR comment**: `github.event.issue.pull_request == null` (`issue_comment` fires for PR comments too).

Defense-in-depth in the prompt: re-confirm via `gh issue view` that the issue is open and the title matches before any write. The `if:` is the real boundary — permissions + allowedTools enforce intent, prose only states it.

### CRITICAL implication: `issue_comment` runs from the default branch

`issue_comment`-triggered workflows always execute the version on the **default branch** (`main`), regardless of any open PR. Consequences (document in a top-of-file comment):

1. **This workflow only takes effect after it is merged to `main`.** The `issue_comment` path cannot be tested from a feature branch — that's why the `workflow_dispatch` path with inputs exists.
2. The companion edit to `cheatsheet-recommend.yml` must also be merged to `main` before issued recommendations carry the correct instruction.

---

## 2. Mapping "1 and 3" → use-case + target

The numbers are row indices into the markdown table the recommender wrote. Its columns:

```
| # | Topic (use case) | Target | Why now | Evidence | Generate with |
```

Resolving a selection: read the issue body, parse the table, and for each selected `#` extract **Topic (use case)** (col 2) and **Target** (col 3, backtick-wrapped). Those map onto the I-1 skill's inputs: use case = free text, `--target` = the library/tool.

This parsing is judgment-laden (free-form comment "1 and 3" / "1,3" / "1 & 3"; natural-language markdown table) so per P-6 it belongs in the agent prompt, not a rigid parser. The agent:

1. `gh issue view <n> --json title,body,state` (default token, THIS repo) to fetch the table.
2. Parse the comment body for selected integers. Accept "1 and 3", "1,3", "1 & 3", "1 3".
3. For each selected number, read that table row → `(use_case, target)`.
4. If a number has no matching row, skip it and report; never invent a topic.

In `workflow_dispatch` mode, the issue number and selection come from `inputs.issue_number` / `inputs.selection`; everything downstream is identical.

The comment body and event fields are passed to the agent via `env:` (so the prompt stays static and untrusted comment text is never interpolated into the prompt string — avoids prompt-injection via YAML interpolation): e.g. `SELECTION_COMMENT: ${{ github.event.comment.body }}`, `ISSUE_NUMBER: ${{ github.event.issue.number || inputs.issue_number }}`, `DISPATCH_SELECTION: ${{ inputs.selection }}`.

---

## 3. The `claude-code-action` invocation

Mirror `cheatsheet-refresh.yml` (closest precedent: generates sheets, branches, one PR per sheet).

### Pinning + auth

Identical SHA pins to the existing two workflows:
- `actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10  # v6`
- `anthropics/claude-code-action@41ea7642c1436fa0ee57aae58347904b71a5af27  # v1`
- `claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}`, `github_token: ${{ github.token }}`.

Checkout with `fetch-depth: 0` so per-topic branches fork cleanly off `main`.

### `permissions:` (least privilege)

Opens PRs and pushes branches in THIS repo; does NOT write issues:

```yaml
permissions:
  contents: write        # push branches, commit generated sheet
  pull-requests: write   # gh pr create
  id-token: write        # OIDC, required by the action
```

Do NOT add `issues: write` unless the optional ack-comment feature is adopted (default: skip the ack).

### `concurrency` + `timeout-minutes`

```yaml
concurrency:
  group: "cheatsheet-generate-${{ github.event.issue.number || inputs.issue_number }}"
  cancel-in-progress: false
```

Keying on the issue number lets selections on different issues run in parallel while serializing repeated comments on the same issue (avoids two runs racing to create the same branch). `cancel-in-progress: false` queues rather than kills. `timeout-minutes: 60` (between recommender's 30 and refresh's 90; a selection is at most 3 sheets).

### `env`

Two-token rule per O-3:

```yaml
env:
  GH_TOKEN: ${{ github.token }}                 # writes (branch push, gh pr create) — THIS repo only
  GH_SCAN_TOKEN: ${{ secrets.GH_SCAN_TOKEN }}   # read-only cross-repo mining inside the skill
  ISSUE_NUMBER: ${{ github.event.issue.number || inputs.issue_number }}
  SELECTION_COMMENT: ${{ github.event.comment.body }}
  DISPATCH_SELECTION: ${{ inputs.selection }}
```

Keep the `GH_SCAN_TOKEN` preflight step that fails fast if the token is unset (the skill mines the user's repos, so the scan token is required).

### `--allowedTools` boundary

The security boundary. Take the refresh toolset and ADD `gh issue view`; allow gh issue/PR read, branch push, gh pr create, uv run; **must NOT allow any merge**:

```
--max-turns 120
--allowedTools "Read,Glob,Grep,Edit,Write,WebSearch,WebFetch,Bash(date:*),Bash(gh api:*),Bash(gh search code:*),Bash(gh search commits:*),Bash(gh repo list:*),Bash(gh repo view:*),Bash(gh issue view:*),Bash(gh issue list:*),Bash(gh pr list:*),Bash(gh pr create:*),Bash(git status:*),Bash(git diff:*),Bash(git switch:*),Bash(git checkout:*),Bash(git restore:*),Bash(git add:*),Bash(git commit:*),Bash(git push:*),Bash(uv run:*)"
```

Boundary notes:
- **Allowed reads**: `gh issue view`, `gh issue list`, `gh pr list`, plus scan-token cross-repo reads (`gh search code/commits`, `gh api`, `gh repo view`).
- **Allowed writes**: `git push`, `gh pr create` only.
- **Deliberate omissions**: no `gh pr merge`, no `gh pr review`, no `Bash(gh pr:*)` wildcard (would let merge through), no `gh issue create/edit/comment`, no `gh api -X`/`--method` mutations. The narrow per-subcommand grants are what enforce "no auto-merge."
- `--max-turns 120`: a selection generates up to 3 sheets from scratch (full mine→ground→author each), so more than the recommender's 60, less than refresh's 150.

### Prompt structure

Follow the refresh prompt skeleton: Orientation → Two-token rule → Privacy → Task (per-topic loop) → Finish/report.

- **Orientation**: read `CLAUDE.md`, `specs/CONSTITUTION.md`, `.claude/skills/cheatsheet/SKILL.md` ("SKILL.md is your generation procedure"). Resolve login `gh api user --jq .login`, capture `date -u +%Y-%m-%d`, note you start on the default branch.
- **Resolve the selection** (O-6-specific): "Read `$ISSUE_NUMBER` with `gh issue view "$ISSUE_NUMBER" --json title,body,state`. Confirm OPEN and title begins `Cheatsheet recommendations` — else STOP, open no PR. Parse its markdown table. Selected numbers come from `$SELECTION_COMMENT` (issue_comment) or `$DISPATCH_SELECTION` (manual). Accept '1 and 3', '1,3', '1 & 3'. For each selected #, extract Topic (col 2) + Target (col 3) — the I-1 inputs. Skip numbers with no matching row and report; never invent a topic."
- **Two-token rule** (NON-NEGOTIABLE): cross-repo reads prefix `GH_TOKEN=$GH_SCAN_TOKEN`; writes (branch push, `gh pr create`) and the issue read use plain `gh`/`git`; never read other repos with the default token; never write with the scan token. Add: "You may NEVER merge, approve, or close anything — you only open PRs."
- **Privacy P-7**: resolve each mined repo's visibility; never put a private repo's name/slug/URL or verbatim code in any committed file or PR text; generalize private patterns; public repos may be cited.
- **Task — the per-topic loop** (§4).
- **Finish**: report the issue read, the selection parsed, the topics resolved, the PRs opened (with branch names), any skipped/duplicate/unresolved numbers. If nothing generated, open zero PRs and say so.

---

## 4. Per-topic loop: branch, isolation, index, PR shape

Reuse the refresh per-sheet pattern, keyed on selected topics. **For each selected `(use_case, target)`:**

1. **Dup-PR guard** (before any write): compute the slug, then `gh pr list --state open --search "generate <slug>" --json headRefName`. If an open PR exists for this branch, SKIP. Also: if the sheet already exists in `cheatsheets/<slug>.md` on main, skip and report "already covered" (this workflow generates NEW sheets; refreshing existing ones is the monthly job's responsibility).

2. **Branch off the default branch**: `auto/generate/<slug>` where `<slug>` is the lowercased, hyphenated `use case + target` exactly as the skill computes it. One branch per topic. `git switch -c auto/generate/<slug>`. (Append `-<YYYY-MM>` only if collision with an old closed branch is a concern.)

3. **Generate the sheet** via the I-1 skill workflow: write `cheatsheets/<slug>.md` with the exact required structure (H1 `# <use case> with <target>`, grounding line, Reference snippet, Typical usage patterns capped at 3, Learnings capped at 3, Agent rules).

4. **Regenerate the index deterministically** (P-6 / P-4): `uv run scripts/register_cheatsheet.py` and stage `index.md`. Unlike refresh (which re-stages index only if a title changed), a NEW sheet always adds an `index.md` row, so `index.md` will always change and must always be staged.

5. **Commit, push, open ONE PR**:
   - `git add cheatsheets/<slug>.md index.md`, commit, `git push -u origin auto/generate/<slug>`.
   - `gh pr create` titled `feat(cheatsheet): add <slug>`. Body: summarize what the sheet covers (use case + target), the doc source it was grounded in, and `Closes selection from #<ISSUE_NUMBER>` linking back to the recommendations issue — NOT a raw diff, NEVER any private repo identifier/content (P-7). No auto-merge; human-reviewed.

6. **Isolate the next topic**: `git switch <default-branch>` and `git restore .` before the next selected topic so each PR contains only its own sheet + index.md row.

**One-PR-per-topic isolation** is enforced structurally: branch-per-slug + restore-between-topics + dup-guard. Three selected numbers → at most three PRs (fewer if duplicates/already-covered/unresolved).

---

## 5. Companion change to `cheatsheet-recommend.yml`

The locked constraint requires the recommendations issue's "Generate with" instruction to reflect the comment-to-generate path rather than a local `/cheatsheet` command. Today the table template hardcodes a local command:

```
| 1 | <use case> | `<target>` | <one line> | `owner/repo` (...) | `/cheatsheet <use case> --target <target>` |
```

That contradicts O-6's "no local execution." Edit the prompt's table template so the column no longer tells the user to run a local command.

**Recommended: Option A with the column removed** (P-3 simplicity). Drop the `| Generate with |` header, its separator cell, and the `/cheatsheet ...` cell. Rely on the existing closing line `Reply with the numbers to add (e.g. "1 and 3"); I'll generate those cheatsheets.` — which now actually resolves to the generate workflow. Strengthen the closing ask to make clear it must be the **repository owner** commenting on **this open issue**. Recommender permissions/tools unchanged.

(Alternative Option B: keep the column but change the cell to e.g. `Comment "1" on this issue`.)

(Note: cosmetic "(O-N)" markers inside `SKILL.md` refer to the I-1 intent's outcomes, not this I-2 O-6 — no change there.)

---

## 6. Satisfying O-6's two tests

### Test 1 — the `shell:` structural test

```
test -f .github/workflows/cheatsheet-generate.yml
&& grep -ql 'issue_comment' .github/workflows/cheatsheet-generate.yml
&& grep -ql 'concurrency' .github/workflows/cheatsheet-generate.yml
&& grep -ql 'timeout-minutes' .github/workflows/cheatsheet-generate.yml
&& ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/cheatsheet-generate.yml
```

The design satisfies every clause: exact filename; `on: issue_comment:` present; `concurrency:` block; `timeout-minutes: 60`; both `uses:` lines SHA-pinned with the version only in a trailing `# v6`/`# v1` comment (the regex anchors `@vN` to end-of-line, so the comment is fine). Must not regress the dir-wide O-5 structural test either.

### Test 2 — the agent check (`checks/web-end-to-end-generate-from-selection.md`)

Enrich its `## Success criteria` (the only writable part — the SHALL is human-owned) with concrete file:line-citable pass conditions:

> Inspect `.github/workflows/cheatsheet-generate.yml` and cite file:line evidence for each:
> - **Trigger + guard**: `on: issue_comment: types: [created]` present and paired with `workflow_dispatch`. The job `if:` restricts to (a) the repository owner, (b) an OPEN issue, (c) a recommendations issue (title-prefix `Cheatsheet recommendations`), (d) excludes PR comments. The `workflow_dispatch` path accepts an issue number + selection so the path is testable without a live comment.
> - **Selection → inputs mapping**: prompt instructs the agent to read the issue body via `gh issue view`, parse the markdown table, map each selected number to its (use case, target) row, skip numbers with no matching row, never invent topics.
> - **Generation via the I-1 skill**: prompt directs the agent to follow `.claude/skills/cheatsheet/SKILL.md` to author `cheatsheets/<slug>.md` and run `uv run scripts/register_cheatsheet.py` to regenerate `index.md`.
> - **One human-reviewed PR per topic, no auto-merge**: per-topic branch (`auto/generate/<slug>`), `git restore`/`git switch` isolation between topics, dup-PR guard via `gh pr list`, `gh pr create` per topic, NO merge/approve/close. `--allowedTools` includes `gh pr create` + `git push` but excludes any `gh pr merge`/`gh pr review`/wildcard `gh pr:*`. `permissions:` grants only `contents: write`, `pull-requests: write`, `id-token: write` (no `issues: write`).
> - **Hardening**: both third-party actions SHA-pinned, `concurrency` group present, `timeout-minutes` set.
> - **Two-token rule (O-3)**: cross-repo reads prefixed with `GH_TOKEN=$GH_SCAN_TOKEN`; writes use default `github.token`; `GH_SCAN_TOKEN` preflight present.
> - **Privacy (P-7)**: prompt forbids private repo name/slug/URL/verbatim content in committed files or PR text; requires generalization.
> - **Web-only loop**: confirm the companion `cheatsheet-recommend.yml` table no longer instructs a local `/cheatsheet` command — the only call to action is commenting the number(s), so the loop completes in the web UI.

---

## 7. Step-by-step task list

1. **Create `.github/workflows/cheatsheet-generate.yml`**: top-of-file comment (purpose + "issue_comment runs from default branch" caveat); `on: issue_comment.created` + `workflow_dispatch` with `issue_number`/`selection` inputs; the job `if:` guard (§1); `permissions:` (contents/pull-requests/id-token write); `concurrency` keyed on issue number; `timeout-minutes: 60`; `env` with two tokens + three event/input vars; `GH_SCAN_TOKEN` preflight; checkout (SHA-pinned, `fetch-depth: 0`); `claude-code-action` (SHA-pinned) with `--max-turns 120`, the `--allowedTools` set (no merge), and the prompt (§3–§4).
2. **Edit `.github/workflows/cheatsheet-recommend.yml`**: drop the "Generate with" column (header, separator, `/cheatsheet ...` cell); keep/strengthen the closing reply-to-generate line (Option A, §5).
3. **Edit `specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/web-end-to-end-generate-from-selection.md`**: replace the placeholder `## Success criteria` with the enriched criteria (§6). Only the non-SHALL section.
4. **Self-verify the `shell:` test locally**: run the exact command from the O-6 citation (read-only grep/test) and the dir-wide floating-tag scan from O-5.
5. **(Operational, out of code scope)** Confirm secrets `GH_SCAN_TOKEN` and `CLAUDE_CODE_OAUTH_TOKEN` exist; merge to `main` (required for the `issue_comment` trigger to take effect).

## Risks / edge cases

- **Comment on a closed issue** → blocked by `state == 'open'` + in-prompt re-check.
- **Non-owner comment** → blocked by `comment.user.login == repository_owner`.
- **Unrelated issue** → blocked by title-prefix marker. Non-selection chatter → agent parses no valid numbers, opens zero PRs, reports "no valid selection."
- **Ambiguous / no-match selection** ("5" with 3 rows, "all") → skip unresolved numbers and report; for "all", agent may map to all rows but must report its interpretation; never invent a topic.
- **Topic already covered** → dup-PR guard + existing-file check skip it; no duplicate.
- **Repeated comments racing** → `concurrency` group per issue serializes; `cancel-in-progress: false` queues; deterministic branch name + dup-guard prevent double PRs.
- **Concurrency with the weekly recommender** → different groups, different artifacts (issue vs branch/PR), no conflict.
- **Prompt injection via comment/issue body** → untrusted text passed via `env` (not interpolated into the prompt); prompt treats it as data; real safety net is `--allowedTools` (no merge) + least-privilege `permissions:`.
- **issue_comment-from-default-branch gotcha** → documented in-file; `workflow_dispatch` covers pre-merge testing.
- **No `GH_SCAN_TOKEN`** → preflight fails fast with an actionable error.

## Manual end-to-end verification recipe

1. **Pre-merge (branch), dispatch path**: create a throwaway test issue titled `Cheatsheet recommendations — week of <today>` with a 2–3 row table in the recommender's shape. Run via `workflow_dispatch` with `issue_number=<that issue>`, `selection="1 and 3"`. Expect two `auto/generate/<slug>` branches and exactly two PRs, each with one new sheet + an `index.md` row, no private identifiers in PR text, no merge. (The `issue_comment` trigger won't fire from a branch — dispatch is the only pre-merge test.)
2. **Edge checks via dispatch**: `selection="5"` (out of range) → zero PRs, reported unresolved. Run twice with the same selection → second opens no duplicate.
3. **Post-merge (main), real comment path**: after merging both file changes to `main`, let the recommender open a real issue (or reuse a correctly-titled test one), then as the owner comment `1 and 3`. Confirm the workflow triggers, guards pass, same per-topic PRs appear. Confirm a non-owner comment (or a comment on a closed/renamed issue) does NOT trigger.

---

## Critical files
- `.github/workflows/cheatsheet-generate.yml` — **new**, the O-6 workflow
- `.github/workflows/cheatsheet-recommend.yml` — **edit**, "Generate with" column → comment-to-generate
- `specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/web-end-to-end-generate-from-selection.md` — **edit**, enrich `## Success criteria`
- `.github/workflows/cheatsheet-refresh.yml` — reference (per-sheet branch/PR/restore/dup-guard pattern)
- `.claude/skills/cheatsheet/SKILL.md` — reference (generation procedure, input shape, slug rule)
