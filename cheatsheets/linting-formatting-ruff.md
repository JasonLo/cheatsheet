# Linting & formatting with Ruff

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from Ruff official docs (context7 `/astral-sh/ruff`)._

## Reference snippet

```toml
# pyproject.toml. One block controls linting AND formatting.
[tool.ruff]
target-version = "py314"     # Use the same version as requires-python
line-length = 100            # The formatter controls line wrapping

[tool.ruff.lint]             # Put lint settings UNDER .lint, not at the top level
select = ["E", "F", "I", "B", "UP", "SIM", "RUF"]  # Allowlist. Add rules to it over time.
ignore = ["E501"]            # The formatter controls line length, not the linter

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]         # Allow asserts in tests

[tool.ruff.format]
quote-style = "double"
```

## Typical usage patterns

- **One `[tool.ruff]` block in `pyproject.toml`**. Do not add a separate `ruff.toml` or other config files for each tool. (seen in `JasonLo/best-in-slot:pyproject.toml`, `JasonLo/best-in-slot:slots/python-tooling/ruff/README.md`)
- **A short `select` allowlist**. The repos select `["E", "F", "I", "B", "UP", "SIM"]`, and the reference slot adds `RUF`. (seen in `JasonLo/best-in-slot:pyproject.toml`, `JasonLo/best-in-slot:slots/python-tooling/ruff/example/pyproject.toml`)
- **`target-version` follows the Python version of the project**. For example, `py314` makes `UP` rewrite code only to syntax that the project supports. (seen in `JasonLo/best-in-slot:pyproject.toml`)

## Learnings

- **Lint settings go at the top of `[tool.ruff]`** → **Lint settings go under `[tool.ruff.lint]`, and format settings go under `[tool.ruff.format]`**. Ruff is two tools that share one config tree, so each setting names the tool that it configures. Only shared keys, for example `line-length` and `target-version`, stay at the top level.
- **Black, isort, flake8, and pyupgrade run together and must agree** → **One tool lints and formats, and rule families replace the old tools**. The `ruff format` command replaces black. The `I`, `UP`, and `B` families replace isort, pyupgrade, and bugbear. (seen in `JasonLo/best-in-slot:slots/python-tooling/ruff/README.md`)
- **`select` means "all the rules"** → **`select` is a specified allowlist that you extend one rule family at a time**. If you select `ALL` and remove the unnecessary rules, each Ruff release that adds rules changes your results. A small, chosen set of rule families gives predictable results. (seen in `JasonLo/best-in-slot:slots/python-tooling/ruff/README.md`)

## Agent rules

- ALWAYS put lint settings under `[tool.ruff.lint]`.
- ALWAYS put format settings under `[tool.ruff.format]`.
- ALWAYS keep only shared keys, for example `line-length` and `target-version`, at the top of `[tool.ruff]`.
- ALWAYS configure ruff in `pyproject.toml` as the single linter and formatter.
- NEVER add black, isort, flake8, or pyupgrade next to ruff.
- ALWAYS set `target-version` to match the `requires-python` value of the project.
- ALWAYS define `select` as a specified allowlist, for example `["E","F","I","B","UP","SIM"]`.
- ALWAYS add new rule codes to the `select` allowlist over time.
- NEVER select `ALL` and then remove rules.
- ALWAYS let `ruff format` control line length.
- ALWAYS ignore `E501` unless you enable it again with `extend-select`.
- ALWAYS run `uv run ruff check --fix .` and `uv run ruff format .` together.
- ALWAYS use `ruff check .` and `ruff format --check .` in CI.
- ALWAYS limit a rule exception to a `# noqa: <code>` at the call site or to `per-file-ignores`.
- NEVER remove a rule from `select` to stop one warning.
- ALWAYS pin `ruff` and `ty` in the dev dependency group.
- ALWAYS run `ruff` and `ty` with `uv run`.
- ALWAYS add both the `ruff` hook with `--fix` and the `ruff-format` hook with a pinned `rev` when you use `ruff-pre-commit`.
