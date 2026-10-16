# Implementation Plan — I-3: Delete a cheatsheet

> Source of truth: `specs/INTENT/I-3-delete-a-cheatsheet/intent.md` (outcomes O-1..O-6). This plan copies the I-2 pattern (`cheatsheet-refresh.yml`, `cheatsheet-recommend.yml`, `cheatsheet-generate.yml`, `register_cheatsheet.py`). It obeys `specs/CONSTITUTION.md` (P-1..P-7). All parts are read-only and have no auto-merge.

## Outcome → artifact map

| Outcome | Artifact(s) |
|---|---|
| O-1 (delete + reindex) | `scripts/delete_cheatsheet.py` and `tests/test_delete_cheatsheet.py::test_delete_removes_file_and_reindexes` |
| O-2 (unknown name gives an error, no change) | `scripts/delete_cheatsheet.py` and `tests/test_delete_cheatsheet.py::test_unknown_name_errors_and_leaves_repo_unchanged` |
| O-3 (scheduled staleness issue) | `.github/workflows/cheatsheet-prune.yml` and `checks/stale-deletion-proposal-issue.md` |
| O-4 (select → delete → one PR) | `.github/workflows/cheatsheet-delete.yml` and `checks/web-end-to-end-delete-from-selection.md` |
| O-5 (`Closes #N` auto-close) | `.github/workflows/cheatsheet-delete.yml` (PR body) |
| O-6 (two-token split + P-7 privacy) | both new workflows and `checks/prune-token-split-and-privacy.md` |

---

## Step 1 — `scripts/delete_cheatsheet.py` (O-1, O-2)

**Create:** `scripts/delete_cheatsheet.py`

Make a self-contained PEP-723 uv script with a `# /// script` block, `requires-python = ">=3.14"`, and `dependencies = []`.
It must match `register_cheatsheet.py` exactly: `from __future__ import annotations`, `argparse`, `--root` default `.`, `main(argv)` that returns an int, and `raise SystemExit(main(sys.argv[1:]))`.

**Key decision — code reuse (P-3, the central trade-off):**
- **Chosen approach: import and use the code again with `importlib`. Do not run it as a subprocess and do not copy the code.**
  `delete_cheatsheet.py` loads `register_cheatsheet.py` as a sibling module. It calls `discover_cheatsheets` + `render_index` from that module to write `index.md` again.
  This keeps one source of truth for index rendering, so P-4 stays authoritative in one location. It adds no duplication.
- Load it the same way that the test harness does:
```python
import importlib.util
_REG = Path(__file__).resolve().parent / "register_cheatsheet.py"
spec = importlib.util.spec_from_file_location("register_cheatsheet", _REG)
register = importlib.util.module_from_spec(spec); spec.loader.exec_module(register)
```
- **Rejected alternatives:**
  (a) Run `uv run scripts/register_cheatsheet.py` as a subprocess. This adds a subprocess and a runtime uv dependency inside a script that uv already runs.
  It is fragile and slower, and it violates P-3 simplicity.
  (b) Copy `_HEADER`/`render_index`/`discover_cheatsheets`. Then two copies of the index format exist, and they become different over time.
  Import is the best choice because it has the least duplication.
  Note for the implementer: an import runs only the top-level defs in `register_cheatsheet.py`.
  Its `main()` is behind `if __name__ == "__main__"`, so the import has no side effects. It is safe.

**Behavior:**
- The positional argument `name` is the cheatsheet name. The target file is `root/cheatsheets/<name>.md`. Decide the name normalization and document it.
  Accept the bare slug, for example `http-client-httpx`. Also accept a trailing `.md` and a leading `cheatsheets/`, and remove them.
  Then the delete workflow can give the slug from the issue table and does not have to guess. Keep this logic minimal.
- **O-1 normal case:** if the file exists, call `path.unlink()`. Then call `(root/"index.md").write_text(register.render_index(register.discover_cheatsheets(root)))`.
  This write works the same as `register_cheatsheet.main`. Print a confirmation (`deleted cheatsheets/<name>.md; index.md updated: N cheatsheet(s).`). Return `0`.
- **O-2 unknown name:** if the file does not exist, print an error to **stderr** that gives the unknown name.
  For example: `error: no cheatsheet named '<name>' (cheatsheets/<name>.md not found)`. Do **no unlink and no index write**, and return non-zero (`return 2`).
  This makes sure that `cheatsheets/` and `index.md` stay byte-for-byte the same.

**Verification (O-1/O-2):** `uv run --with pytest pytest tests/test_delete_cheatsheet.py`

---

## Step 2 — `tests/test_delete_cheatsheet.py` (O-1, O-2)

**Create:** `tests/test_delete_cheatsheet.py`

Copy the structure of `tests/test_register_cheatsheet.py`. Use a top-level `importlib.util.spec_from_file_location` loader.
The `_load()` function returns the `delete_cheatsheet` module, and a module-level `dele` holds it. Use `tmp_path` fixtures and no external dependencies.
The `[test:]` citations of the intent need both of these named tests:

- **`test_delete_removes_file_and_reindexes`** — make a `tmp_path/cheatsheets/` with two sheets (`a.md` `# Alpha`, `b.md` `# Beta`). Run `dele.main(["--root", str(tmp_path), "a"])`.
  Assert that the return is `0`, `a.md` is gone, and `b.md` stays. Assert that `tmp_path/index.md` contains `- [Beta](cheatsheets/b.md)` and does **not** contain `Alpha`/`cheatsheets/a.md`.
  This proves both the file removal and the reindex.
- **`test_unknown_name_errors_and_leaves_repo_unchanged`** — make a `cheatsheets/` with one sheet and an `index.md` that already exists.
  Record the list of the cheatsheets directory and the bytes of `index.md`. Run `dele.main(["--root", str(tmp_path), "does-not-exist"])`.
  Assert that the return is non-zero, the directory list does not change, and the `index.md` bytes are the same as the record.
  Also capture stderr with `capsys` and assert that the unknown name is in it.

**Trade-off note:** test against `main(argv)` in the same process, not in a subprocess. This matches `test_register_cheatsheet.py::test_main_writes_index`.
It also keeps the suite fast and without dependencies.

**Verification:** `uv run --with pytest pytest tests/test_delete_cheatsheet.py -q`

---

## Step 3 — `.github/workflows/cheatsheet-prune.yml` (O-3, O-6)

**Create:** `.github/workflows/cheatsheet-prune.yml`. Copy the structure of `cheatsheet-recommend.yml`, which is the scheduled producer that only opens issues. Do not copy `generate.yml`.

- `name: "Cheatsheet staleness prune"`.
- **Triggers:** use `on: schedule:` with a monthly or about yearly cron, for example `"37 5 1 * *"`. Use it **together with** `workflow_dispatch: {}`.
- **`permissions:` (least privilege, issue only, the same as recommend):** `contents: read`, `issues: write`, `id-token: write`. Do not give `contents: write` or `pull-requests`.
- **`concurrency:`** use the group `"cheatsheet-prune"` and `cancel-in-progress: false`.
- **`timeout-minutes:`** about 30.
- **`env:`** use `GH_TOKEN: ${{ github.token }}` for the issue write in this repo.
  Also use `GH_SCAN_TOKEN: ${{ secrets.GH_SCAN_TOKEN }}`, the read-only PAT for the cross-repo usage history.
- **Preflight step** that requires `GH_SCAN_TOKEN`. Copy the current `::error::` block exactly.
- **Pin the actions** to the SHAs that the repo already uses: `actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10`, `anthropics/claude-code-action@41ea7642c1436fa0ee57aae58347904b71a5af27`.
  The job does not need `setup-uv`, because no script runs in the prune job. It only opens an issue.
- **`--allowedTools`** is read-only plus issue create, the same as recommend:
  `Read,Glob,Grep,WebSearch,WebFetch,Bash(date:*),Bash(gh api:*),Bash(gh search code:*),Bash(gh search commits:*),Bash(gh repo list:*),Bash(gh repo view:*),Bash(gh issue list:*),Bash(gh issue create:*)`.
  Do not give `Edit`/`Write`/`git`/`gh pr`.

**Prompt — key design decision: how the agent uses `gh` to decide "used in the last year" (O-3).**

Write a concrete procedure that uses only gh (P-5, P-6). The agent makes the *judgment* about staleness, and deterministic gh data gives the *signal*:
1. Get the login one time: `gh api user --jq .login`.
2. Compute the cutoff: `date -u -d '1 year ago' +%Y-%m-%d`.
3. For each `cheatsheets/*.md`, get its **target** from the H1 (`# <use case> with <target>`) or from the italic source line.
4. A target is **used within the past year** if it is in the activity of the owner after the cutoff. The agent finds this with cross-repo reads.
   One example is `uv run scripts/gh_scan.py search code --owner <login> "<target>" --json repository,path` that returns any hit.
   Another example is `uv run scripts/gh_scan.py search commits --author <login> --committer-date '>=<cutoff>'` that touches a repo where the target is present.
   Tell the agent that any hit after the cutoff means "used". A sheet is **stale** only when it has **zero** signal after the cutoff.
5. Keep only stale sheets. **Open no issue if no sheet is stale.** All I-2 producers do nothing when the result is empty.
6. Make sure that no open issue already exists (`gh issue list --state open --search "Cheatsheet staleness"`).
7. Open exactly **one** issue with `gh issue create`:
   - **Title:** `Cheatsheet staleness — <Month YYYY>`. The `if:` guard of the delete workflow uses this stable prefix. Choose the exact prefix now and use the same prefix in Step 4.
   - **Body:** an introduction, one markdown table, and a one-line request. Define the columns so that the delete workflow can parse them:
     `| # | Cheatsheet (use case) | Target | Cheatsheet file | Last seen | Evidence |`.
     **Column 4 contains the exact `cheatsheets/<slug>.md` path or slug** that the delete script uses.
     This is the simplest mapping from selection to file. Do not make the delete agent find a slug again.
     The request: "As the repo owner, reply on THIS open issue with the number(s) to delete, for example '1 and 3'. Your comment starts the delete workflow. The workflow opens one PR that removes them. You do not need a local command."
     This keeps the loop web-only and mentions no local `/` command.

**Two-token + privacy block (O-6, P-5, P-7):** copy the NON-NEGOTIABLE two-token rule from recommend:
- Each cross-repo read always runs through `uv run scripts/gh_scan.py`. The issue write uses plain `gh`.
- Never read other repos with the default token. Never write with the scan token.
- The job has no contents-write permission and cannot open PRs.

Also copy the P-7 privacy block:
- Find the visibility of each mined repo with `gh repo view … --json visibility`.
- Never put the name, slug, URL, or exact content of a private repo in the issue.
- Make evidence from private sources general. You can cite public repos.

**Verification (O-3):**
```
test -f .github/workflows/cheatsheet-prune.yml \
 && grep -ql 'workflow_dispatch' .github/workflows/cheatsheet-prune.yml \
 && grep -ql 'concurrency' .github/workflows/cheatsheet-prune.yml \
 && grep -ql 'timeout-minutes' .github/workflows/cheatsheet-prune.yml \
 && ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/cheatsheet-prune.yml
```

---

## Step 4 — `.github/workflows/cheatsheet-delete.yml` (O-4, O-5, O-6)

**Create:** `.github/workflows/cheatsheet-delete.yml`. Copy the structure of `cheatsheet-generate.yml`, which is the event-driven workflow from selection to PR.
Change it from "generate sheets with the skill" to "delete sheets with the deterministic script".

**The delete loop runs `scripts/delete_cheatsheet.py`, NOT the cheatsheet skill.** The prompt says this directly, and P-6 agrees, because deletion is concrete and deterministic.

- `name: "Cheatsheet delete from selection"`.
- **Triggers:** use `on: issue_comment: types: [created]` **together with** `workflow_dispatch:` with the `issue_number` + `selection` inputs.
  Then you can test the workflow without a live comment. Copy the inputs block from generate.
- **Job `if:` guard** — change the guard from generate so that it uses only the staleness issue prefix:
```
github.event_name == 'workflow_dispatch' ||
(github.event_name == 'issue_comment' &&
 github.event.issue.pull_request == null &&
 github.event.issue.state == 'open' &&
 github.event.comment.user.login == github.repository_owner &&
 startsWith(github.event.issue.title, 'Cheatsheet staleness'))
```

- The guard limits the run to (a) the repo owner, (b) an open issue, (c) not a PR comment, and (d) a **staleness proposal** issue. The prefix is the exact prefix from Step 3.
- **`permissions:`** `contents: write`, `pull-requests: write`, `issues: write` (only for the 👀 ack reaction), `id-token: write`. These are the same as generate.
- **`concurrency:`** use a group for each issue, `"cheatsheet-delete-${{ github.event.issue.number || inputs.issue_number }}"`, and `cancel-in-progress: false`.
  Repeated comments on the same issue then run one after the other, so two runs cannot both try to create the branch.
- **`timeout-minutes:`** about 20. Deletion is fast, because it has no mining and no doc grounding.
- **`env:`** use `GH_TOKEN: ${{ github.token }}` and `GH_SCAN_TOKEN: ${{ secrets.GH_SCAN_TOKEN }}`.
  Also use the three env variables for untrusted data: `ISSUE_NUMBER`, `SELECTION_COMMENT: ${{ github.event.comment.body }}`, `DISPATCH_SELECTION: ${{ inputs.selection }}`.
  Never put event text into the prompt string.
- **Steps:** 👀-ack step (issue_comment path only) → `GH_SCAN_TOKEN` preflight → `actions/checkout@<SHA>` with `fetch-depth: 0` → **`astral-sh/setup-uv@fac544c07dec837d0ccb6301d7b5580bf5edae39`** → `anthropics/claude-code-action@<SHA>`.
  The `setup-uv` step is REQUIRED. The delete run calls `uv run scripts/delete_cheatsheet.py`, and the runner has neither uv nor Python.
- **`--allowedTools`** — give read, git, `gh pr create`, and **`uv run`**. Give **no `Edit`/`Write`**, because the script removes the file and the agent must not delete files manually.
  Give **no `gh pr merge`/`gh pr review`/wildcard `gh pr:*`**, so that there is no auto-merge:
  `Read,Glob,Grep,Bash(date:*),Bash(gh api:*),Bash(gh repo view:*),Bash(gh issue view:*),Bash(gh issue list:*),Bash(gh pr list:*),Bash(gh pr create:*),Bash(git status:*),Bash(git diff:*),Bash(git switch:*),Bash(git checkout:*),Bash(git rm:*),Bash(git add:*),Bash(git commit:*),Bash(git push:*),Bash(uv run:*)`.

**Prompt task (copy the structure of generate):**
1. **Resolve the selection first:** read `$ISSUE_NUMBER` with `gh issue view "$ISSUE_NUMBER" --json title,body,state`.
   Make sure that the issue is OPEN and the title prefix is `Cheatsheet staleness`. If not, STOP and open no PR.
   Parse the table. The selected numbers come from `$SELECTION_COMMENT` or `$DISPATCH_SELECTION`. Accept "1 and 3", "1,3", "1 & 3", and "1 3".
   Map each selected number to its **cheatsheet file or slug from column 4**. Skip numbers that have no matching row. Never invent one.
2. **One run → one branch → one PR.** Make the branch `auto/delete/from-issue-$ISSUE_NUMBER` from the default branch.
   Use a dup guard for the run: run `gh pr list --state open --head <branch> --json number`. STOP if a PR already uses this branch. Then run `git switch -c <branch>`.
3. **For each selected sheet, run the deterministic delete:** `uv run scripts/delete_cheatsheet.py <slug>`.
   If the script exits non-zero (unknown name, O-2 behavior), report that number as skipped and continue. Do not fail the full run.
   The script removes the file and writes `index.md` again on each call. This is correct, because the final `index.md` shows all deletions.
4. **Stage and commit one time** after all deletions. Run `git add -A`, which captures the removed `cheatsheets/*.md` files and the updated `index.md`.
   Then commit and run `git push -u origin <branch>`.
5. **Open exactly one PR** with `gh pr create`. Use the title `chore(cheatsheet): delete selected stale sheets from #$ISSUE_NUMBER`.
   The body is a short summary that lists each deleted sheet (use case + target, with **public** evidence only). The last line is exactly `Closes #$ISSUE_NUMBER` (O-5).
   There is no auto-merge. The agent has no merge tool and must not try to merge.
6. **Finish/no-op:** if the agent resolved nothing, it opens zero PRs and pushes no empty branch. It prints a one-line reason.

**Two-token + privacy block (O-6):** copy the block from generate:
- Each cross-repo read always runs through `uv run scripts/gh_scan.py`. The agent needs these reads only if it checks the evidence again.
- The issue read and all writes (branch push, `gh pr create`) use plain `gh`/`git`.
- Never read other repos with the default token. Never write with the scan token.
- Never put the name, slug, URL, or exact content of a private repo in the PR title or body. Make it general.

**Verification (O-4 + O-5):**
```
test -f .github/workflows/cheatsheet-delete.yml \
 && grep -ql 'issue_comment' .github/workflows/cheatsheet-delete.yml \
 && grep -ql 'concurrency' .github/workflows/cheatsheet-delete.yml \
 && grep -ql 'timeout-minutes' .github/workflows/cheatsheet-delete.yml \
 && ! grep -REn 'uses:.*@v[0-9]+[[:space:]]*$' .github/workflows/cheatsheet-delete.yml
grep -qE 'Closes #\$\{?ISSUE_NUMBER' .github/workflows/cheatsheet-delete.yml
```

---

## Step 5 — Improve the Success criteria of the three agent checks (human-owned, report only)

These files are in `specs/INTENT/I-3-delete-a-cheatsheet/checks/`. They are HUMAN-OWNED, so change them only with `/spec-intent` (see CLAUDE.md).
This plan does **not** edit them. It gives the concrete pass conditions that the user can write into them.
These conditions use the I-2 checks as a model, mainly `web-end-to-end-generate-from-selection.md`:

- **`stale-deletion-proposal-issue.md` (O-3)** — to PASS, give file:line evidence for each item:
  - `cheatsheet-prune.yml` has `on: schedule` + `workflow_dispatch`.
  - `permissions:` is issue-only: `contents: read`, `issues: write`, `id-token: write`, with no `pull-requests` and no `contents: write`.
  - The workflow sets `concurrency` and `timeout-minutes`. Both actions have SHA pins, with no floating `@vN`.
  - The prompt defines "used within the past year" with a gh cutoff. It uses `date -u -d '1 year ago'` and cross-repo reads with `gh search code`/`gh search commits`.
    It lists **only** sheets with zero signal after the cutoff.
  - The workflow opens exactly ONE issue with the agreed title prefix. Column 4 of its table contains the file.
  - It is a **no-op (no issue) when no sheet is stale**. A dedup guard is present.
  - The request tells the user to comment on the issue (web-only), not to run a local command.
- **`web-end-to-end-delete-from-selection.md` (O-4)** — to PASS, the workflow must meet these items:
  - It has `on: issue_comment: [created]` + `workflow_dispatch` (issue_number + selection).
  - The `if:` guard checks the owner, an open issue, not a PR comment, and the `Cheatsheet staleness` title prefix.
  - The agent parses the selection from `env` (`SELECTION_COMMENT`/`DISPATCH_SELECTION`/`ISSUE_NUMBER`). The workflow never puts it into the prompt.
  - Deletion uses `uv run scripts/delete_cheatsheet.py`, not the skill, and the agent has no `Edit`/`Write`. `setup-uv` is present and has a SHA pin.
  - ONE run branch `auto/delete/from-issue-<N>` collects all deletions. The script handles `register` and the index.
    A dup-PR guard for the run is present, and there is exactly one `gh pr create`.
  - `--allowedTools` has `gh pr create`, `git push`, and `uv run`. It EXCLUDES `gh pr merge`/`gh pr review`/`gh pr:*`, so there is no auto-merge.
  - The PR body ends with `Closes #<N>`. The hardening (SHA pins, concurrency, timeout) is present.
- **`prune-token-split-and-privacy.md` (O-6)** — to PASS, BOTH new workflows must meet these items:
  - A `GH_SCAN_TOKEN` preflight is present. Each cross-repo read runs through `uv run scripts/gh_scan.py`.
  - Issue and PR writes in this repo use the default `github.token`. The prune job has no `contents: write` and cannot open PRs.
  - The prompt does not allow the name, slug, URL, or exact content of any private repo in issue or PR text. It requires general descriptions, and it allows citations of public repos.
  - The agent finds the visibility with `gh repo view … --json visibility` before any citation.

Also tell the user this: `spec-check` writes the `verdict_*`/`status` fields in the intent frontmatter. Do not edit them manually.

---

## Suggested commit / merge sequence

Work on the worktree branch. Commit in the order of the dependencies, so that each commit passes its checks alone:

1. **`feat(delete): deterministic delete_cheatsheet.py reusing register's index render (I-3 O-1/O-2)`** — Steps 1+2 (`scripts/delete_cheatsheet.py`, `tests/test_delete_cheatsheet.py`).
   Verify with `uv run --with pytest pytest tests/test_delete_cheatsheet.py -q`. Also run the full suite with `uv run --with pytest pytest -q`.
2. **`feat(prune): scheduled staleness issue over >1yr gh usage (I-3 O-3/O-6)`** — Step 3 (`cheatsheet-prune.yml`). Verify with the O-3 shell one-liner above.
3. **`feat(delete): issue-comment selection → one bundled deletion PR, Closes #N (I-3 O-4/O-5/O-6)`** — Step 4 (`cheatsheet-delete.yml`). Verify with the O-4 + O-5 shell one-liners above.
4. **(User, with `/spec-intent`)** add the Success criteria from Step 5 to the three `checks/*.md` files.
   Then run `/spec-check` to calculate the I-3 status and the `verdict_*` counts.

Then **merge** with the worktree sequence in CLAUDE.md: commit → rebase onto `main` → `--ff-only` merge → remove worktree + delete branch → push `main`.

> CI caveat (from `cheatsheet-generate.yml`): `issue_comment` and `schedule` workflows work only after they are on `main`. The `issue_comment` path always runs the copy on `main`. Before the merge, test them with the `workflow_dispatch` inputs, not with a live comment.
