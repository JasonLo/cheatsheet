# Linting & formatting TypeScript/JavaScript with Biome

_Grounded in JasonLo's repos as of 2026-06-06; current practice per Biome official docs (biomejs.dev)._

## Reference snippet

```json
{
  "$schema": "https://biomejs.dev/schemas/2.4.16/schema.json",
  "vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true },
  "files": { "includes": ["**", "!dist"] },
  "formatter": { "indentStyle": "space", "indentWidth": 2, "lineWidth": 80 },
  "linter": { "enabled": true, "rules": { "recommended": true } },
  "assist": { "actions": { "source": { "organizeImports": "on" } } },
  "javascript": { "formatter": { "quoteStyle": "single", "semicolons": "asNeeded" } },
  "domains": { "react": "recommended" }
}
```

Canonical Biome 2.x `biome.json`: version-pinned schema, VCS integration, full unified pipeline.

## Typical usage patterns

- **Single check command for everything**: `biome check --write` runs the full pipeline — formatter, linter, and import organizer in one pass; `biome ci` is the read-only equivalent for CI pipelines. (seen in `JasonLo/skill-cellar:package.json`)
- **VCS-driven file exclusion**: `vcs.useIgnoreFile: true` derives Biome's ignore list directly from `.gitignore`; the `files.includes` negations only handle tracked files that should still be excluded from linting (e.g., auto-generated bindings). (seen in `JasonLo/skill-cellar:biome.json`)
- **Domain-based framework rules (Biome 2.x)**: `domains.react: "recommended"` enables the React rule set — replaces per-namespace rule toggling from Biome 1.x and the former `eslint-plugin-react` install. (seen in `JasonLo/skill-cellar:biome.json`)

## Learnings

- **Multi-tool pipeline (ESLint + Prettier + import-sorter) → single `biome check --write`**: Biome owns format, lint, and import organization under one config file; there is no separate `.prettierrc`, no import-sort plugin, no two-step `eslint . && prettier --write .` — `biome check --write` replaces the whole pipeline in one pass.
- **`eslint-plugin-react` install → `domains.react` key**: Biome 2.x introduces named domain scopes (`domains.react`, etc.) so framework-specific rules are toggled by a single config key, not by installing a separate npm package and wiring it as a plugin. The mental model shifts from "plugin ecosystem" to "built-in, toggleable rule sets."
- **Type-aware lint without TypeScript compiler overhead**: Biome 2.x added its own type-inference layer for rules like floating-promise detection — no `@typescript-eslint/parser` or `parserOptions.project` required. The analysis is scoped to rules that opt in to cross-file indexing, so the rest of the suite keeps its single-file speed.

## Agent rules

- ALWAYS run `biome check --write` for the combined format + lint + import-sort pass; use `biome ci` in CI (not `biome check`).
- ALWAYS pin the exact Biome version with `-E` (`npm i -D -E @biomejs/biome`) and reference that pinned version in `$schema`.
- ALWAYS set `vcs.useIgnoreFile: true` to inherit exclusions from `.gitignore` rather than duplicating them in `files.includes`.
- NEVER install `eslint-plugin-react` or a separate import-sort plugin when using Biome — use `domains.react: "recommended"` and `assist.actions.source.organizeImports: "on"` instead.
