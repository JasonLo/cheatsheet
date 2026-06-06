# Implementation Plan — I-3: Delete a cheatsheet

> Source of truth: `specs/INTENT/I-3-delete-a-cheatsheet/intent.md` (outcomes O-1..O-6). This plan mirrors the I-2 pattern (`cheatsheet-refresh.yml`, `cheatsheet-recommend.yml`, `cheatsheet-generate.yml`, `register_cheatsheet.py`) and obeys `specs/CONSTITUTION.md` (P-1..P-7). Read-only/no-auto-merge throughout.

## Outcome → artifact map

| Outcome | Artifact(s) |
|---|---|
| O-1 (delete + reindex) | `scripts/delete_cheatsheet.py`; `tests/test_delete_cheatsheet.py::test_delete_removes_file_and_reindexes` |
| O-2 (unknown name errors, no mutation) | `scripts/delete_cheatsheet.py`; `tests/test_delete_cheatsheet.py::test_unknown_name_errors_and_leaves_repo_unchanged` |
| O-3 (scheduled staleness issue) | `.github/workflows/cheatsheet-prune.yml`; `checks/stale-deletion-proposal-issue.md` |
| O-4 (select → delete → one PR) | `.github/workflows/cheatsheet-delete.yml`; `checks/web-end-to-end-delete-from-selection.md` |
| O-5 (`Closes #N` auto-close) | `.github/workflows/cheatsheet-delete.yml` (PR body) |
| O-6 (two-token split + P-7 privacy) | both new workflows; `checks/prune-token-split-and-privacy.md` |

---

## Step 1 — `scripts/delete_cheatsheet.py` (O-1, O-2)

**Create:** `scripts/delete_cheatsheet.py`

A self-contained PEP-723 uv script (`# /// script` block, `requires-python = ">=3.14"`, `dependencies = []`) matching `register_cheatsheet.py` exactly: `from __future__ import annotations`, `argparse`, `--root` default `.`, `main(argv)` returning an int, `raise SystemExit(main(sys.argv[1:]))`.

**Key decision — code reuse (P-3, the central trade-off):**
- **Chosen approach: import-and-reuse via `importlib`, not shell-out and not copy-paste.** `delete_cheatsheet.py` loads `register_cheatsheet.py` as a sibling module and calls its `discover_cheatsheets` + `render_index` to rewrite `index.md`. This keeps a single source of truth for index rendering (P-4 stays authoritative in one place) and adds zero duplication.
- Load it the way the test harness already does:
  ```python
  import importlib.util
  _REG = Path(__file__).resolve().parent / "register_cheatsheet.py"
  spec = importlib.util.spec_from_file_location("register_cheatsheet", _REG)
  register = importlib.util.module_from_spec(spec); spec.loader.exec_module(register)
  ```
- **Rejected alternatives:** (a) shelling out `uv run scripts/register_cheatsheet.py` — adds a subprocess + uv dependency at runtime inside a script that's itself run by uv, brittle and slower, violates P-3 simplicity; (b) duplicating `_HEADER`/`render_index`/`discover_cheatsheets` — two copies of the index format drift apart. Import wins on minimal duplication. (Note for the implementer: importing executes only top-level defs in `register_cheatsheet.py` — its `main()` is guarded by `if __name__ == "__main__"`, so import has no side effects. Safe.)

**Behavior:**
- Positional arg `name` = the cheatsheet name. Resolve the target file as `root/cheatsheets/<name>.md`. Decide and document the name normalization: accept the bare slug (e.g. `http-client-httpx`) and tolerate a trailing `.md` and a leading `cheatsheets/` by stripping them, so the delete workflow can pass the slug derived from the issue table without guessing. Keep it minimal.
- **O-1 happy path:** if the file exists, `path.unlink()`, then `(root/"index.md").write_text(register.render_index(register.discover_cheatsheets(root)))` — identical write semantics to `register_cheatsheet.main`. Print a confirmation (`deleted cheatsheets/<name>.md; index.md updated: N cheatsheet(s).`). Return `0`.
- **O-2 unknown name:** if the file does not exist, print an error to **stderr** that names the unknown name (e.g. `error: no cheatsheet named '<name>' (cheatsheets/<name>.md not found)`), perform **no unlink and no index write**, return non-zero (`return 2`). This guarantees `cheatsheets/` and `index.md` are byte-for-byte untouched.

**Verification (O-1/O-2):** `uv run --with pytest pytest tests/test_delete_cheatsheet.py`

---

## Step 2 — `tests/test_delete_cheatsheet.py` (O-1, O-2)

**Create:** `tests/test_delete_cheatsheet.py`

Mirror `tests/test_register_cheatsheet.py`: top-level `importlib.util.spec_from_file_location` loader (`_load()` returning the `delete_cheatsheet` module, assigned to a module-level `dele`), `tmp_path` fixtures, no external deps. Both named tests required by the intent's `[test:]` citations:

- **`test_delete_removes_file_and_reindexes`** — build a `tmp_path/cheatsheets/` with two sheets (`a.md` `# Alpha`, `b.md` `# Beta`), run `dele.main(["--root", str(tmp_path), "a"])`; assert return `0`, `a.md` is gone, `b.md` remains, and `tmp_path/index.md` contains `- [Beta](cheatsheets/b.md)` and does **not** contain `Alpha`/`cheatsheets/a.md`. This proves both the file removal and the reindex.
- **`test_unknown_name_errors_and_leaves_repo_unchanged`** — build a `cheatsheets/` with one sheet and a pre-existing `index.md`; snapshot the cheatsheets dir listing and `index.md` bytes; run `dele.main(["--root", str(tmp_path), "does-not-exist"])`; assert return is non-zero, the dir listing is unchanged, and `index.md` bytes are identical to the snapshot. (Capture stderr via `capsys` and assert the unknown name appears in it.)

**Trade-off note:** test against `main(argv)` (in-process) rather than a subprocess — matches `test_register_cheatsheet.py::test_main_writes_index` and keeps the suite dependency-free and fast.

**Verification:** `uv run --with pytest pytest tests/test_delete_cheatsheet.py -q`

---

## Step 3 — `.github/workflows/cheatsheet-prune.yml` (O-3, O-6)

**Create:** `.github/workflows/cheatsheet-prune.yml`. Structurally clone `cheatsheet-recommend.yml` (the issue-only scheduled producer), not `generate.yml`.

- `name: "Cheatsheet staleness prune"`.
- **Triggers:** `on: schedule:` (a yearly-ish / monthly cron, e.g. `"37 5 1 * *"`) **paired with** `workflow_dispatch: {}`.
- **`permissions:` (least privilege — issue only, like recommend):** `contents: read`, `issues: write`, `id-token: write`. No `contents: write`, no `pull-requests`.
- **`concurrency:`** group `"cheatsheet-prune"`, `cancel-in-progress: false`.
- **`timeout-minutes:`** ~30.
- **`env:`** `GH_TOKEN: ${{ github.token }}` (the issue write, this repo) + `GH_SCAN_TOKEN: ${{ secrets.GH_SCAN_TOKEN }}` (read-only PAT, cross-repo usage history).
- **Preflight step** requiring `GH_SCAN_TOKEN` (copy the existing `::error::` block verbatim).
- **Actions SHA-pinned** to the same SHAs already used: `actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10`, `anthropics/claude-code-action@41ea7642c1436fa0ee57aae58347904b71a5af27`. No `setup-uv` needed (no script runs in the prune job — it only opens an issue).
- **`--allowedTools`** read-only + issue-create only, matching recommend: `Read,Glob,Grep,WebSearch,WebFetch,Bash(date:*),Bash(gh api:*),Bash(gh search code:*),Bash(gh search commits:*),Bash(gh repo list:*),Bash(gh repo view:*),Bash(gh issue list:*),Bash(gh issue create:*)`. No `Edit`/`Write`/`git`/`gh pr`.

**Prompt — key design decision: how the agent defines "used in the last year" via `gh` (O-3).** Spell out a concrete, gh-only procedure (P-5, P-6 — the *judgment* of staleness is the agent's, the *signal* is deterministic gh data):
1. Resolve login once: `gh api user --jq .login`.
2. Compute the cutoff: `date -u -d '1 year ago' +%Y-%m-%d`.
3. For each `cheatsheets/*.md`, recover its **target** from the H1 (`# <use case> with <target>`) / italic source line.
4. A target counts as **used within the past year** if it appears in the owner's activity since the cutoff via cross-repo reads, e.g. `GH_TOKEN=$GH_SCAN_TOKEN gh search code --owner <login> "<target>" --json repository,path` returning any hit, OR `GH_TOKEN=$GH_SCAN_TOKEN gh search commits --author <login> --committer-date '>=<cutoff>'` touching a repo where the target is present. Direct the agent to treat any post-cutoff hit as "used"; only when there is **zero** post-cutoff signal is the sheet **stale**.
5. Keep only stale sheets; **open no issue if none are stale** (no-op-when-clean, like every I-2 producer).
6. Dedup against an existing open issue (`gh issue list --state open --search "Cheatsheet staleness"`).
7. Open exactly **one** issue with `gh issue create`:
   - **Title:** `Cheatsheet staleness — <Month YYYY>` (a stable prefix the delete workflow's `if:` guard keys on — pick the exact prefix now and reuse it verbatim in Step 4).
   - **Body:** intro + one markdown table + one-line ask. Define the columns so the delete workflow can parse them: `| # | Cheatsheet (use case) | Target | Cheatsheet file | Last seen | Evidence |`, where **column 4 carries the exact `cheatsheets/<slug>.md` path / slug** the delete script consumes (this is the cleanest selection→file mapping — don't make the delete agent re-derive a slug). The ask: "Reply on THIS open issue (as the repo owner) with the number(s) to delete — e.g. '1 and 3'. Your comment triggers the delete workflow, which opens one PR removing them; no local command needed." (web-only loop, no local `/` command mentioned.)

**Two-token + privacy block (O-6, P-5, P-7):** copy recommend's NON-NEGOTIABLE two-token rule (cross-repo reads always prefixed `GH_TOKEN=$GH_SCAN_TOKEN`; the issue write is plain `gh`; never read other repos with the default token, never write with the scan token; the job has no contents-write and cannot open PRs) and the P-7 privacy block (resolve each mined repo's visibility with `gh repo view … --json visibility`; never put a private repo's name/slug/URL or verbatim content in the issue; generalize private-sourced evidence; public repos may be cited).

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

**Create:** `.github/workflows/cheatsheet-delete.yml`. Structurally clone `cheatsheet-generate.yml` (the event-driven select→PR workflow), adapting it from "generate sheets via the skill" to "delete sheets via the deterministic script." **The delete loop runs `scripts/delete_cheatsheet.py`, NOT the cheatsheet skill** (per the prompt's explicit note and P-6 — deletion is concrete/deterministic).

- `name: "Cheatsheet delete from selection"`.
- **Triggers:** `on: issue_comment: types: [created]` **paired with** `workflow_dispatch:` taking `issue_number` + `selection` inputs (testable without a live comment — copy generate's inputs block).
- **Job `if:` guard** — adapt generate's guard but key on the staleness issue prefix only:
  ```
  github.event_name == 'workflow_dispatch' ||
  (github.event_name == 'issue_comment' &&
   github.event.issue.pull_request == null &&
   github.event.issue.state == 'open' &&
   github.event.comment.user.login == github.repository_owner &&
   startsWith(github.event.issue.title, 'Cheatsheet staleness'))
  ```
  Guarded to (a) repo owner, (b) open issue, (c) not a PR comment, (d) a **staleness proposal** issue (the exact prefix chosen in Step 3).
- **`permissions:`** `contents: write`, `pull-requests: write`, `issues: write` (only to post the 👀 ack reaction), `id-token: write` — identical to generate.
- **`concurrency:`** per-issue group `"cheatsheet-delete-${{ github.event.issue.number || inputs.issue_number }}"`, `cancel-in-progress: false` (serialize repeat comments on the same issue so two runs can't race to create the branch).
- **`timeout-minutes:`** ~20 (deletion is cheap — no mining, no doc grounding).
- **`env:`** `GH_TOKEN: ${{ github.token }}`, `GH_SCAN_TOKEN: ${{ secrets.GH_SCAN_TOKEN }}`, and the untrusted-data-as-env trio `ISSUE_NUMBER`, `SELECTION_COMMENT: ${{ github.event.comment.body }}`, `DISPATCH_SELECTION: ${{ inputs.selection }}` (never interpolate event text into the prompt string).
- **Steps:** 👀-ack step (issue_comment path only) → `GH_SCAN_TOKEN` preflight → `actions/checkout@<SHA>` with `fetch-depth: 0` → **`astral-sh/setup-uv@fac544c07dec837d0ccb6301d7b5580bf5edae39`** (REQUIRED — the delete run calls `uv run scripts/delete_cheatsheet.py`; the runner ships neither uv nor Python) → `anthropics/claude-code-action@<SHA>`.
- **`--allowedTools`** — read + git + `gh pr create` + **`uv run`**, but **no `Edit`/`Write`** (the script does the file removal; the agent must not hand-delete) and **no `gh pr merge`/`gh pr review`/wildcard `gh pr:*`** (no auto-merge): `Read,Glob,Grep,Bash(date:*),Bash(gh api:*),Bash(gh repo view:*),Bash(gh issue view:*),Bash(gh issue list:*),Bash(gh pr list:*),Bash(gh pr create:*),Bash(git status:*),Bash(git diff:*),Bash(git switch:*),Bash(git checkout:*),Bash(git rm:*),Bash(git add:*),Bash(git commit:*),Bash(git push:*),Bash(uv run:*)`.

**Prompt task (mirror generate's structure):**
1. **Resolve selection first:** read `$ISSUE_NUMBER` via `gh issue view "$ISSUE_NUMBER" --json title,body,state`; confirm OPEN and title prefix `Cheatsheet staleness`, else STOP and open no PR. Parse the table; map each selected number (from `$SELECTION_COMMENT` or `$DISPATCH_SELECTION`, accepting "1 and 3" / "1,3" / "1 & 3" / "1 3") to its **cheatsheet file/slug from column 4**. Skip numbers with no matching row; never invent one.
2. **One run → one branch → one PR.** Branch `auto/delete/from-issue-$ISSUE_NUMBER` off the default branch. Run-level dup guard: `gh pr list --state open --head <branch> --json number` → STOP if a PR already targets it. `git switch -c <branch>`.
3. **For each selected sheet, run the deterministic delete:** `uv run scripts/delete_cheatsheet.py <slug>`. If the script exits non-zero (unknown name — O-2 wiring), report that number as skipped and continue; do not fail the whole run. The script removes the file and rewrites `index.md` each call — that's fine; the final `index.md` reflects all deletions.
4. **Stage + commit once** after all deletions: `git add -A` (captures the removed `cheatsheets/*.md` and the updated `index.md`), commit, `git push -u origin <branch>`.
5. **Open exactly one PR** (`gh pr create`) — title `chore(cheatsheet): delete selected stale sheets from #$ISSUE_NUMBER`; body = short summary listing each deleted sheet (use case + target, **public** evidence only), then a final line that is exactly `Closes #$ISSUE_NUMBER` (O-5). No auto-merge — the agent has no merge tool and must not attempt one.
6. **Finish/no-op:** if nothing resolved, open zero PRs, push no empty branch, print a one-line reason.

**Two-token + privacy block (O-6):** copy generate's block — cross-repo reads (only needed if the agent re-confirms evidence) always `GH_TOKEN=$GH_SCAN_TOKEN`; reading the issue + all writes (branch push, `gh pr create`) use plain `gh`/`git`; never read other repos with the default token, never write with the scan token; never put a private repo's name/slug/URL or verbatim content in PR title/body; generalize.

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

## Step 5 — Enrich the three agent-check Success criteria (human-owned; flag only)

These live under `specs/INTENT/I-3-delete-a-cheatsheet/checks/` and are HUMAN-OWNED (per CLAUDE.md, modify only via `/spec-intent`). This plan does **not** edit them; it states the concrete pass-conditions the user should encode, modeled on the I-2 checks (esp. `web-end-to-end-generate-from-selection.md`):

- **`stale-deletion-proposal-issue.md` (O-3)** — PASS requires file:line evidence that: `cheatsheet-prune.yml` has `on: schedule` + `workflow_dispatch`; `permissions:` is issue-only (`contents: read`, `issues: write`, `id-token: write`, no `pull-requests`/no `contents: write`); `concurrency` + `timeout-minutes` set; both actions SHA-pinned (no floating `@vN`); the prompt defines "used within the past year" via a gh cutoff (`date -u -d '1 year ago'` + `gh search code`/`gh search commits` cross-repo reads) and lists **only** zero-post-cutoff-signal sheets; opens exactly ONE issue with the agreed title prefix and the column-4-carries-the-file table; **no-op (no issue) when nothing is stale**; dedup guard present; the ask points to commenting on the issue (web-only), not a local command.
- **`web-end-to-end-delete-from-selection.md` (O-4)** — PASS requires: `on: issue_comment: [created]` + `workflow_dispatch` (issue_number + selection); `if:` guard = owner + open issue + not-a-PR-comment + `Cheatsheet staleness` title prefix; selection parsed from `env` (`SELECTION_COMMENT`/`DISPATCH_SELECTION`/`ISSUE_NUMBER`), never interpolated; deletion goes through `uv run scripts/delete_cheatsheet.py` (not the skill, no `Edit`/`Write`); `setup-uv` present and SHA-pinned; ONE run branch `auto/delete/from-issue-<N>` accumulating all deletions, `register`/index handled by the script, run-level dup-PR guard, exactly one `gh pr create`; `--allowedTools` includes `gh pr create`+`git push`+`uv run` but EXCLUDES `gh pr merge`/`gh pr review`/`gh pr:*` (no auto-merge); PR body ends `Closes #<N>`; hardening (SHA pins, concurrency, timeout) present.
- **`prune-token-split-and-privacy.md` (O-6)** — PASS requires, across BOTH new workflows: `GH_SCAN_TOKEN` preflight; cross-repo reads prefixed `GH_TOKEN=$GH_SCAN_TOKEN`; in-repo issue/PR writes via default `github.token`; prune job has no `contents: write` and cannot open PRs; the prompt forbids any private repo name/slug/URL or verbatim content in issue/PR text and requires generalization (public-repo citation allowed); visibility resolved via `gh repo view … --json visibility` before any citation.

(Also note for the user: the intent frontmatter `verdict_*`/`status` are skill-written by `spec-check` — do not hand-edit.)

---

## Suggested commit / merge sequencing

Work on the worktree branch; commit in dependency order so each commit is independently green:

1. **`feat(delete): deterministic delete_cheatsheet.py reusing register's index render (I-3 O-1/O-2)`** — Steps 1+2 (`scripts/delete_cheatsheet.py`, `tests/test_delete_cheatsheet.py`). Verify: `uv run --with pytest pytest tests/test_delete_cheatsheet.py -q` (and the full suite `uv run --with pytest pytest -q`).
2. **`feat(prune): scheduled staleness issue over >1yr gh usage (I-3 O-3/O-6)`** — Step 3 (`cheatsheet-prune.yml`). Verify: the O-3 shell one-liner above.
3. **`feat(delete): issue-comment selection → one bundled deletion PR, Closes #N (I-3 O-4/O-5/O-6)`** — Step 4 (`cheatsheet-delete.yml`). Verify: the O-4 + O-5 shell one-liners above.
4. **(User, via `/spec-intent`)** enrich the three `checks/*.md` Success criteria per Step 5, then run `/spec-check` to derive I-3 status and the `verdict_*` counts.

Then **merge** per CLAUDE.md's worktree sequence (commit → rebase onto `main` → `--ff-only` merge → remove worktree + delete branch → push `main`).

> CI caveat (carried from `cheatsheet-generate.yml`): both `issue_comment` and `schedule` workflows only take effect once on `main`, and the `issue_comment` path always runs the copy on `main` — pre-merge, exercise them via the `workflow_dispatch` inputs, not a live comment.
