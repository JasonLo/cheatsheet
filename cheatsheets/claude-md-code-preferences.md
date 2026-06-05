# Code preferences with CLAUDE.md

_Grounded in JasonLo's repos as of 2026-06-05; current practice per uv official docs (context7 `/astral-sh/uv`)._

## Reference snippet

```markdown
## Code Preferences
- Run Python with `uv run`; manage deps with `uv add` / `uv sync` (never pip directly)
- Python 3.14+, always statically typed; no `from __future__ import annotations`
- `typer` for CLIs; Pydantic v2 for data that crosses a boundary (API, disk, config)
- `ruff` for lint + format, `ty` for type-checking
- One-line docstrings for simple functions; avoid unnecessary comments
- Guard clauses over deep nesting; principle of parsimony; flat layout over `src/`
- Check context7 MCP / official docs for current syntax before using a library
- Inside a worktree, "merge" means the full ritual: commit → rebase onto `main` → `--ff-only` merge into `main` → remove the worktree and delete the branch → push `main`
```

## Typical usage patterns

How you actually encode preferences in CLAUDE.md today, distilled to the recurring shapes:

- **A dedicated preferences section near the top** — a short bullet list of cross-cutting style rules, placed before project-specific architecture. You reach for it to set defaults an agent should carry into every file. The header drifts in name across repos (`Code Preferences`, `Code Preference`, `Use preferences`, `Code preferences`) but the intent is identical. (seen in `JasonLo/uw-s3:CLAUDE.md`, and several private repos)
- **A uv-first toolchain mandate** — `uv run` to execute, `uv sync` to install, `ruff` + `ty` for quality. The recurring instinct is "never touch pip directly," delegating environment management to one tool. (seen in `JasonLo/undock:CLAUDE.md`, and several private repos)
- **A "verify before you write" research rule** — instruct the agent to check context7 / official docs for current syntax rather than trusting training memory. This is a meta-preference about *how* the agent should work, not what the code looks like. (seen in `JasonLo/uw-s3:CLAUDE.md`, `JasonLo/sound-trim:CLAUDE.md`, and a private repo)

## Learnings

Each correction names an obsolete or drifted pattern in your CLAUDE.md files, the conceptual reason it changed, and what to do instead:

- **"Each repo restates the full preference block"** → **"Universal preferences live once, at the user level."** The same ~6-bullet block is hand-copied into 7+ repos and has visibly drifted — three different Python floors (`3.12+`, `3.13+`, `3.14+`), four different section titles, typer mandated in some and silently dropped for argparse in one. Drift is the symptom of the wrong altitude: cross-cutting style is a *you* preference, so it belongs in global `~/.claude/CLAUDE.md`; per-repo files should hold only what's genuinely project-specific. (seen across `JasonLo/uw-s3`, `JasonLo/sound-trim`, and several private repos)
- **"Bootstrap a project with `uv pip install -e .`"** → **"`uv sync` installs the project for you."** Older repos still reach for the pip-emulation mental model — manually editable-installing the package into a venv. In a uv-managed project, `uv sync` / `uv run` install the project automatically; the editable install is implicit. The shift is from "install my package into an environment" to "sync the environment to the lockfile." Reserve `uv pip install -e .` for the one place it still earns its keep: Docker layer caching. (seen in `JasonLo/sound-trim:CLAUDE.md`, and a private repo)
- **"Use Pydantic for objects with 7+ attributes"** → **"Use Pydantic when data crosses a boundary, not by attribute count."** The count is a proxy for the real trigger: does this data come from / go to an untrusted edge (an API response, a config file, JSON on disk) and need validation or serialization? A 3-field API payload wants Pydantic; a 10-field internal-only struct is happier as a dataclass. Decide on *boundary crossing and validation need*, not field arithmetic. (seen in `JasonLo/uw-s3:CLAUDE.md`)

## Agent rules

- ALWAYS run Python via `uv run`; manage dependencies with `uv add` / `uv sync`. NEVER invoke pip directly.
- ALWAYS set up a project with `uv sync` — it installs the project automatically. NEVER `uv pip install -e .` for local dev; reserve it for Docker layer caching.
- NEVER add `from __future__ import annotations` — target Python 3.14, where deferred annotations and `X | Y` unions are native.
- ALWAYS use static typing; lint + format with `ruff` and type-check with `ty`.
- ALWAYS prefer `typer` for CLIs and Pydantic v2 for data that crosses a boundary (API, disk, config); use a dataclass for internal-only structs.
- ALWAYS write one-line docstrings for simple functions, avoid unnecessary comments, and use guard clauses over deep nesting.
- ALWAYS check context7 / official docs for current syntax before using a library API — don't trust training memory.
- NEVER copy a full preference block into a new repo's CLAUDE.md — keep universal preferences in global `~/.claude/CLAUDE.md`; per-repo files hold only project-specific guidance.
- ALWAYS restate an inverted preference explicitly when the target platform can't support a default (e.g. CircuitPython: no typing, no f-strings, `%` formatting only).
- ALWAYS expand a "merge" request inside a worktree into the full ritual: commit → rebase `main` → `git merge --ff-only` → remove the worktree and delete the branch → push. NEVER run a bare `git merge` and stop.
