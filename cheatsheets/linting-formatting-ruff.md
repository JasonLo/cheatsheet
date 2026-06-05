# Linting & formatting with Ruff

_Grounded in JasonLo's repos as of 2026-06-05; current practice per Ruff official docs (context7 `/astral-sh/ruff`)._

## Reference snippet

```toml
# pyproject.toml — one block does linting AND formatting.
[tool.ruff]
target-version = "py314"     # match the project's requires-python
line-length = 100            # the formatter owns wrapping

[tool.ruff.lint]             # lint settings live UNDER .lint, not top-level
select = ["E", "F", "I", "B", "UP", "SIM", "RUF"]  # allowlist; grow it over time
ignore = ["E501"]            # line-length is the formatter's job, not the linter's

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]         # allow asserts in tests

[tool.ruff.format]
quote-style = "double"
```

```sh
uv run ruff check --fix .    # lint + auto-fix
uv run ruff format .         # format (write)
uv run ruff check .          # CI: lint, fail on findings
uv run ruff format --check . # CI: fail if not formatted
```

## Typical usage patterns

- **Single `[tool.ruff]` block in `pyproject.toml`** — no separate `ruff.toml`, no per-tool config files; ruff replaces black + isort + flake8 + pyupgrade at once. Reach for it on every Python project. (`JasonLo/best-in-slot:pyproject.toml`, `JasonLo/best-in-slot:slots/python-tooling/ruff/README.md`)
- **Curated `select` allowlist, not "all"** — `["E", "F", "I", "B", "UP", "SIM"]` (+`RUF` on the reference slot). You opt rules in deliberately; `I` gives import-sorting (isort), `UP` gives pyupgrade. (`JasonLo/best-in-slot:pyproject.toml`, `JasonLo/best-in-slot:slots/python-tooling/ruff/example/pyproject.toml`)
- **`target-version` tracks the project's Python** — e.g. `py314`, so `UP` rewrites to syntax the project actually supports. (`JasonLo/best-in-slot:pyproject.toml`)
- **`ignore = ["E501"]`** — line length is delegated to `ruff format`; the linter shouldn't double-flag it. (`JasonLo/best-in-slot:pyproject.toml`)
- **`ruff` + `ty` together in the dev dependency group** — linter/formatter and type-checker pinned as dev deps, run via `uv run`. (`JasonLo/uw-s3:pyproject.toml`, `JasonLo/undock:pyproject.toml`)
- **Documented two-command workflow in CLAUDE.md** — `uv run ruff check .` then `uv run ruff format .` (often with `uv run ty check`) as the project's standing lint/format contract. (`JasonLo/uw-s3:CLAUDE.md`, `JasonLo/undock:CLAUDE.md`)
- **Narrow escapes, not global disables** — `# noqa: F401` at the call site and `per-file-ignores` for `tests/*`, rather than removing a rule from `select`. (`JasonLo/best-in-slot:slots/python-tooling/ruff/CHEATSHEET.md`)
- **`ruff-pre-commit` with both hooks** — `ruff` (`--fix`) and `ruff-format` pinned by `rev`, run together. (`JasonLo/best-in-slot:slots/python-tooling/ruff/CHEATSHEET.md`)
- **New Python projects scaffold ruff by default** — `ruff` (with `ty`) is a default dev dependency in the project template. (`JasonLo/code-template:cookiecutter.json`)

## Learnings

- **"Lint config goes at the top of `[tool.ruff]`"** → **"Lint rules live under `[tool.ruff.lint]`; format under `[tool.ruff.format]`."** Early ruff put `select`/`ignore` at the top level; they were split into `.lint` and `.format` namespaces once ruff became both linter and formatter. The mental shift: ruff is two tools sharing one config tree, so each setting names which half it configures — top-level keys (`line-length`, `target-version`) are the shared ones. Your repos already use the split form; treat top-level `select` as legacy.
- **"Stack black + isort + flake8 (+ pyupgrade) and wire them together"** → **"One tool is linter and formatter; rule *families* stand in for the old tools."** The old model was an orchestra of single-purpose tools to install, pin, and reconcile. Ruff's model: `ruff format` is the formatter (black's role) and `select` rule families replace the linters — `I` = isort, `UP` = pyupgrade, `B` = bugbear. Nothing to reconcile between tools because there's only one. (`JasonLo/best-in-slot:slots/python-tooling/ruff/README.md`)
- **"The linter enforces line length (E501)"** → **"The formatter owns line length; the linter steps aside."** Treating E501 as a lint failure double-governs wrapping and fights the formatter on edge cases. Ruff's model: `ruff format` decides wrapping (set `line-length` once at top level), so E501 is ignored by default — only re-enable it (via `extend-select`) for strings/comments the formatter can't reflow. (`JasonLo/best-in-slot:pyproject.toml`)
- **"`select` should approximate 'all the rules'"** → **"`select` is an opt-in allowlist you grow deliberately."** Chasing `ALL` and then subtracting noise inverts the intent and breaks on every ruff release that adds rules. The model: start from a small curated family set and add codes when you want them — additive, predictable, no surprise churn. (`JasonLo/best-in-slot:slots/python-tooling/ruff/README.md`)
- **"Silence a noisy rule by dropping it from `select`"** → **"Scope the exception as narrowly as the violation."** Removing a rule globally to quiet one file loses its coverage everywhere. The model: keep the rule on, and localize the exception — `# noqa: <code>` at the offending line, or `per-file-ignores` for a directory like `tests/*`. (`JasonLo/best-in-slot:slots/python-tooling/ruff/CHEATSHEET.md`)

## Agent rules

- ALWAYS put lint settings under `[tool.ruff.lint]` and format settings under `[tool.ruff.format]`; keep only shared keys (`line-length`, `target-version`) at the top of `[tool.ruff]`.
- ALWAYS configure ruff in `pyproject.toml` as the single linter+formatter; NEVER add black, isort, flake8, or pyupgrade alongside it.
- ALWAYS set `target-version` to match the project's `requires-python`.
- ALWAYS define `select` as an explicit allowlist (e.g. `["E","F","I","B","UP","SIM"]`) and grow it additively; NEVER select `ALL` and subtract.
- ALWAYS let `ruff format` own line length; keep `E501` ignored unless deliberately re-enabling via `extend-select`.
- ALWAYS run `uv run ruff check --fix .` and `uv run ruff format .` together; in CI use `ruff check .` and `ruff format --check .`.
- ALWAYS scope a rule exception narrowly with `# noqa: <code>` at the call site or `per-file-ignores`; NEVER drop a rule from `select` to silence one occurrence.
- ALWAYS pin `ruff` (and `ty`) in the dev dependency group and invoke via `uv run`.
- ALWAYS wire both `ruff` (`--fix`) and `ruff-format` hooks when using `ruff-pre-commit`, pinned by `rev`.
