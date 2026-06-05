# Type checking with ty

_Grounded in JasonLo's repos as of 2026-06-05; current practice per ty official docs (astral-sh/ty, context7)._

## Reference snippet

```toml
# pyproject.toml — ty auto-discovers config; keep it minimal
[dependency-groups]
dev = ["ty"]               # PEP 735 dev group, not optional-dependencies

[tool.ty.environment]
python-version = "3.13"    # only pin if you target something other than your interpreter

[tool.ty.rules]
# raise/lower a single rule instead of blanket-ignoring a file
possibly-unresolved-reference = "warn"
```

```sh
uv run ty check            # check whole project (auto-discovers src/ + project)
uv run ty check src/       # scope to a path
uvx ty check               # run without installing
```

```python
import typer  # ty: ignore[unresolved-import]   # always code the specific rule, not bare ignore
```

## Typical usage patterns

- Add ty as a `[dependency-groups].dev` dep (PEP 735), never as an optional-dependency — run via `uv run ty check` locally and in CI. (`JasonLo/best-in-slot:slots/python-tooling/ty/README.md`, `JasonLo/skill-sommelier:skills/ss-modern-python/SKILL.md`)
- Single CI/release step is just `uv run ty check`; no separate config flags. (`JasonLo/undock:CLAUDE.md`)
- Scope checks to the package dir (`uv run ty check src/`) in new-project scaffolding. (`JasonLo/skill-sommelier:skills/ss-modern-python/SKILL.md`)
- Default mental model: fix or narrow the type at the boundary rather than sprinkling ignores. (`JasonLo/best-in-slot:slots/python-tooling/ty/README.md`)
- When an ignore is genuinely needed, use a rule-coded `# ty: ignore[<rule>]` with a one-line reason — e.g. a PEP 723 script-level dep the project checker can't resolve. (`JasonLo/uw-s3:scripts/release.py`)
- Migration recipe in scaffolding: `uv remove mypy` → delete `[tool.mypy]`/`mypy.ini` → `uv add --group dev ty` → `uv run ty check src/`. (`JasonLo/skill-sommelier:skills/ss-modern-python/SKILL.md`)
- ty is treated as the default checker, displacing mypy/pyright in the modern-python toolchain. (`JasonLo/skill-sommelier:skills/ss-modern-python/SKILL.md`)

## Learnings

- **mypy needs plugins + heavy config to understand your code** → **ty infers from the type system directly.** Drop the mypy plugin/ini scaffolding; ty's value is a near-zero-config, auto-discovering checker, so resist porting old `[tool.mypy]` knobs over.
- **`# type: ignore` as the reflex for any complaint** → **a coded `# ty: ignore[rule]` is a targeted, auditable suppression.** Bare/PEP-484 `# type: ignore` mutes the whole line; the rule-coded form documents *which* check and why, and lets `unused-ignore-comment` flag it once the cause is gone — treat each ignore as debt with a reason.
- **A red diagnostic = a hard build failure** → **ty has severity tiers (error / warn / ignore) tuned per rule.** Demote a noisy-but-not-fatal rule to `warn` in `[tool.ty.rules]` instead of blanket-ignoring a file; keep signal while unblocking.
- **Pin nothing / float the type checker like any stable tool** → **ty is pre-1.0; rules and behavior shift between releases.** Pin a known-good version in lockfiles for anything shared, so a checker update doesn't spontaneously fail CI.
- **One checker must handle 100% of the codebase** → **ty's plugin coverage is still maturing; a hard wall is a fallback signal, not a reason to paper over.** If a real gap appears, fall back to pyright for that one project rather than burying it under ignores.

## Agent rules

- ALWAYS add ty under `[dependency-groups].dev` and invoke it as `uv run ty check`.
- ALWAYS keep `[tool.ty]` config minimal and rely on auto-discovery; add keys only when a concrete need exists.
- ALWAYS prefer fixing or narrowing the type at the boundary over adding a suppression.
- ALWAYS write suppressions as rule-coded `# ty: ignore[<rule>]` with a short inline reason.
- ALWAYS demote a noisy rule via `[tool.ty.rules].<rule> = "warn"` instead of blanket-ignoring a whole file.
- ALWAYS pin a known-good ty version in lockfiles for shared/published projects (ty is pre-1.0).
- NEVER use bare `# type: ignore` or `# ty: ignore` to mute a whole line when a specific rule code applies.
- NEVER port `[tool.mypy]`/`mypy.ini` settings or mypy plugins into a ty setup; delete them on migration.
- NEVER place ty in `[project.optional-dependencies]`.
- NEVER bury a genuine ty coverage gap under ignores; fall back to pyright for that one project instead.
