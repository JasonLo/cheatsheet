---
name: cheatsheet
description: Generate a self-maintaining personal cheatsheet from a use case + explicit target. Mines the user's OWN GitHub repos (via gh) for how they actually use the target, grounds it in current official docs (context7 + web), and writes a cheatsheet whose Learnings section corrects obsolete patterns at the conceptual level. Triggers on "make a cheatsheet", "cheatsheet for X", "/cheatsheet", "how do I use X in my repos".
---

# cheatsheet

Produce a human-facing cheatsheet for a **use case** anchored to an explicit
**target** (a library, tool, repo, or path). The cheatsheet captures how the
user *actually* uses the target today and corrects where that usage has gone
stale — focused on concepts and intent. One small reference snippet shows the
current shape; the prose stays conceptual, never syntax-diff trivia.

## Inputs

- **Use case** (free text) — e.g. "data fetching", "config loading".
- **`--target`** (required) — the library/tool/repo/path to anchor on, e.g.
  `httpx`, `pydantic`, `owner/repo`, `src/db/`.

If `--target` is missing, ask for it once before proceeding.

## Workflow

1. **Resolve the GitHub identity.** Run `gh api user --jq .login` to get the
   authenticated login (e.g. `jasonlo`). All GitHub access in this skill uses
   the `gh` CLI only — never a direct API call or SDK (Constitution P-5).

2. **Collect the user's real usage across their repos.** Search the user's own
   code for the target and gather the most relevant files:
   - `gh search code --owner <login> "<target>" --limit 50 --json repository,path`
   - When useful, enumerate repos first: `gh repo list <login> --limit 200 --json name,pushedAt`
   - Fetch candidate file contents:
     `gh api repos/<login>/<repo>/contents/<path> --jq .content | base64 -d`
   Judge which files genuinely show the use case; keep the handful that best
   represent the user's idioms, imports, and conventions. Note the file paths —
   you will cite them in the cheatsheet.

3. **Establish current best practice.** Pull the target's current official
   documentation via context7: `resolve-library-id` then `query-docs` scoped to
   the use case. If context7 has no entry for the target, fall back to
   WebSearch + WebFetch of the official docs, changelog, or migration guide.
   Prefer the most recent stable guidance.

4. **Classify each observed pattern as current or obsolete.** For every usage
   you pulled from the user's repos, compare it against the current guidance and
   label it: still idiomatic, or superseded. For superseded ones, identify the
   *mental-model shift* behind the change — not just the new function name.

5. **Author the cheatsheet** to `cheatsheets/<slug>.md`, where `<slug>` is the
   lowercased, hyphenated use case + target.

   **Write every section in concise point form (O-4).** Short bullets, not
   paragraphs. Keep a detail only if it is a future-use must-know/tip or carries
   the conceptual learning; cut incidental narration, restatement, and backstory.
   One idea per bullet; prefer a clause over a sentence.

   Use this structure exactly:

   ````markdown
   # <Use case> with <target>

   _Grounded in <login>'s repos as of <today>; current practice per <doc source>._

   ## Reference snippet

   ```<lang>
   # One minimal, idiomatic block showing present-day usage of <target>,
   # grounded in the current docs from step 3 — NOT copied from the user's
   # (possibly obsolete) repo code. Smallest snippet that conveys the shape.
   ```

   One small block: the "what does correct usage look like today" anchor,
   derived from the step-3 docs, not the mined repo files. A single illustrative
   block — not an API listing. The no-syntax-dump rule below governs the prose,
   not this anchor.

   ## Typical usage patterns

   - Recurring shapes of how you use <target> today — one bullet each: the
     pattern, when you reach for it, and a real-file cite (`owner/repo:path`).
     One line per bullet where you can. Conceptual, not a syntax dump.

   ## Learnings

   Each bullet names an obsolete pattern/misconception found in your code and
   its replacement, framed at the level of *intent and mental model*, not API
   signatures — terse, one to two lines:

   - **<Old mental model>** → **<New mental model>.** The why + what now
     expresses the same intent. (seen in `owner/repo:path`)
   ````

6. **Author the Learnings section at conceptual altitude (O-5).** Every entry
   must explain a *why* — the shift in intent or model. Reject syntax-only diffs
   ("`x()` is now `y()`") unless paired with the conceptual reason. If a change
   is purely cosmetic syntax, leave it out.

7. **Register the cheatsheet.** Run `uv run scripts/register_cheatsheet.py` to
   regenerate the root `index.md` (Constitution P-4). Do not hand-edit
   `index.md`.

8. **Report** the path written, the files mined, the doc source used, and the
   number of learnings surfaced.

## Constraints

- GitHub access via `gh` CLI only (P-5).
- Any deterministic helper is a self-contained `uv`/PEP-723 script (P-1/P-2);
  this skill currently shells out only to `scripts/register_cheatsheet.py`.
- Favor the simplest path that yields a useful cheatsheet (P-3).
