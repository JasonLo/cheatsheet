# Code preferences with CLAUDE.md

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from the Claude Code memory docs (code.claude.com/docs/en/memory) and the uv official docs (context7 `/astral-sh/uv`)._

## Reference snippet

```markdown
## Code Preferences
- Run Python with `uv run`; manage deps with `uv add` / `uv sync` (never pip directly)
- Python 3.14+, always statically typed; no `from __future__ import annotations`
- `typer` for CLIs; Pydantic v2 for data that crosses a boundary (API, disk, config)
- `ruff` for lint + format, `ty` for type-checking
- One-line docstrings for simple functions; avoid unnecessary comments
- All docs follow progressive disclosure: lead with the essential, defer detail — short overview first, specifics on demand
- Guard clauses over deep nesting; principle of parsimony; flat layout over `src/`
- Check context7 MCP / official docs for current syntax before using a library
- Inside a worktree, "merge" means the full ritual: commit → rebase onto `main` → `--ff-only` merge into `main` → remove the worktree and delete the branch → push `main`
```

## Typical usage patterns

- A **preferences section near the top** of CLAUDE.md holds short style rules that apply to every file. The title differs between repos, for example `Code Preferences`, `Code Preference`, `Use preferences`, and `Code preferences`. (seen in `JasonLo/uw-s3:CLAUDE.md`, and several private repos)
- A **uv-first toolchain rule** tells the agent to run code with `uv run` and to install with `uv sync`. The rule also sets `ruff` and `ty` for quality and does not allow direct use of pip. (seen in `JasonLo/undock:CLAUDE.md`, and several private repos)
- A **research rule** tells the agent to check context7 or the official docs for current syntax. This rule controls how the agent works, not how the code looks. (seen in `JasonLo/uw-s3:CLAUDE.md`, `JasonLo/sound-trim:CLAUDE.md`, and a private repo)

## Learnings

- **Restate the preferences in each repo** → **Keep universal preferences one time, at the user level.** General style belongs in global `~/.claude/CLAUDE.md`, and each repo keeps only project-specific guidance. (seen across `JasonLo/uw-s3`, `JasonLo/sound-trim`, and several private repos)
- **Install the package with `uv pip install -e .`** → **Sync the environment to the lockfile.** In a uv project, `uv sync` and `uv run` install the project automatically. Keep `uv pip install -e .` only for Docker layer caching. (seen in `JasonLo/sound-trim:CLAUDE.md`, and a private repo)
- **Use Pydantic for objects with 7+ attributes** → **Use Pydantic when data crosses a boundary.** The trigger is validation of API, config, or disk data. An internal-only struct is a dataclass for all field counts. (seen in `JasonLo/uw-s3:CLAUDE.md`)

## Agent rules

- ALWAYS run Python with `uv run`.
- ALWAYS manage dependencies with `uv add` and `uv sync`.
- NEVER invoke pip directly.
- ALWAYS prepare a project with `uv sync`.
- NEVER use `uv pip install -e .` except for Docker layer caching.
- NEVER add `from __future__ import annotations`.
- ALWAYS use static typing.
- ALWAYS lint and format with `ruff`.
- ALWAYS type-check with `ty`.
- ALWAYS use `typer` for CLIs.
- ALWAYS use Pydantic v2 for data that crosses a boundary, for example an API, disk, or config.
- ALWAYS use a dataclass for internal-only structs.
- ALWAYS write one-line docstrings for simple functions.
- NEVER add unnecessary comments.
- ALWAYS use guard clauses instead of deep nesting.
- ALWAYS check context7 or the official docs for current syntax before you use a library API.
- NEVER copy a full preference block into the CLAUDE.md of a new repo.
- ALWAYS keep universal preferences in global `~/.claude/CLAUDE.md`.
- ALWAYS limit the CLAUDE.md of each repo to project-specific guidance.
- ALWAYS state the opposite defaults for limited platforms, for example no typing, no f-strings, and `%` formatting on CircuitPython.
- ALWAYS treat a "merge" request in a worktree as this sequence: commit, rebase onto `main`, `git merge --ff-only`, remove the worktree and branch, and push.
- NEVER run a bare `git merge` and stop.
