# Type checking with ty

_Grounded in JasonLo's repos as of 2026-07-03. Current practice is from ty official docs (astral-sh/ty) and ty 0.0.52 release notes._

## Reference snippet

```toml
# pyproject.toml: ty finds the config automatically. Keep the config small.
[dependency-groups]
dev = ["ty"]               # PEP 735 dev group, not optional-dependencies

[tool.ty.environment]
python-version = "3.13"    # pin only if the target is not your interpreter version

[tool.ty.rules]
# change the level of one rule. Do not ignore a full file.
possibly-unresolved-reference = "warn"

[tool.ty.terminal]
error-on-warning = false   # ty ≥ 0.0.52: warn rules exit 1 by default. Set false to make them non-fatal.
```

## Typical usage patterns

- Add ty as a `[dependency-groups].dev` dependency (PEP 735), not as an optional dependency. Run it with `uv run ty check` locally and in CI, or with `uvx ty check` without an install. (seen in `JasonLo/best-in-slot:slots/python-tooling/ty/README.md`, `JasonLo/skill-sommelier:skills/ss-modern-python/SKILL.md`)
- Where ty cannot resolve something, add a rule-coded `# ty: ignore[<rule>]` with a one-line reason. For example, the project checker cannot resolve the script-level dependency of a PEP 723 script. (seen in `JasonLo/uw-s3:scripts/release.py`)
- A migration from mypy runs `uv remove mypy` and deletes `[tool.mypy]`/`mypy.ini`. Then it runs `uv add --group dev ty` and `uv run ty check src/`. (seen in `JasonLo/skill-sommelier:skills/ss-modern-python/SKILL.md`)

## Learnings

- **mypy needs plugins and a large config** → **ty infers from the type system with almost no config.** The value of ty is a checker that finds its config automatically. Do not port old `[tool.mypy]` settings to it.
- **A bare `# type: ignore` is the answer to any error** → **Each suppression is a targeted record with a reason.** The bare form suppresses all checks on the whole line. A coded `# ty: ignore[rule]` names the check, and `unused-ignore-comment` reports it after the cause no longer exists.
- **The `warn` level stops a rule from failing CI** → **Rule severity and exit status are separate settings.** Since ty 0.0.52, a `warn` rule also exits with code 1. To keep a rule visible but not a failure, also set `[tool.ty.terminal] error-on-warning = false`.

## Agent rules

- ALWAYS add ty under `[dependency-groups].dev`.
- ALWAYS run ty as `uv run ty check`.
- ALWAYS keep the `[tool.ty]` config minimal.
- ALWAYS use the auto-discovery of ty.
- ALWAYS add a config key only for a concrete need.
- ALWAYS fix or narrow the type at the boundary before you add a suppression.
- ALWAYS write suppressions as rule-coded `# ty: ignore[<rule>]` with a short inline reason.
- ALWAYS pair `[tool.ty.rules].<rule> = "warn"` with `[tool.ty.terminal] error-on-warning = false` for a rule that must not fail CI.
- ALWAYS pin a known-good ty version in lockfiles for shared or published projects.
- NEVER use bare `# type: ignore` or `# ty: ignore` when a specific rule code applies.
- NEVER port `[tool.mypy]`/`mypy.ini` settings or mypy plugins into a ty setup.
- ALWAYS delete the mypy settings and plugins when you migrate to ty.
- NEVER put ty in `[project.optional-dependencies]`.
- NEVER use ignores to hide a real gap in ty coverage.
- ALWAYS use pyright for a project where ty has a real coverage gap.
