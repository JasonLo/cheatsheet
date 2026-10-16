# Linting & formatting TypeScript/JavaScript with Biome

_Grounded in JasonLo's repos as of 2026-06-06. Current practice is from Biome official docs (biomejs.dev)._

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

## Typical usage patterns

- **One check command for all tasks.** The `biome check --write` command runs the formatter, the linter, and the import organizer in one pass. For CI pipelines, `biome ci` is the read-only command. (seen in `JasonLo/skill-cellar:package.json`)
- **File exclusion from VCS.** The `vcs.useIgnoreFile: true` setting makes Biome use `.gitignore` as its ignore list. Use `files.includes` negations only for tracked files that Biome must not lint, for example generated bindings. (seen in `JasonLo/skill-cellar:biome.json`)
- **Framework rules by domain.** The `domains.react: "recommended"` setting adds the React rule set. (seen in `JasonLo/skill-cellar:biome.json`)

## Learnings

- **Separate tools format, lint, and sort imports** → **One tool runs the full pipeline.** Biome does all three tasks from one config file. The `biome check --write` command replaces `eslint . && prettier --write .`, `.prettierrc`, and the import-sort plugin.
- **Install `eslint-plugin-react` for framework rules** → **Framework rules are built-in sets.** One config key, for example `domains.react`, adds a rule set in Biome 2.x. No npm package or plugin setup is necessary.
- **Type-aware lint needs the TypeScript compiler** → **Biome infers types itself.** Rules, for example floating-promise detection, work without `@typescript-eslint/parser` or `parserOptions.project`. Only some rules use cross-file indexing, so the other rules stay fast.

## Agent rules

- ALWAYS run `biome check --write` for the combined format, lint, and import-sort pass.
- ALWAYS use `biome ci` in CI, not `biome check`.
- ALWAYS pin the exact Biome version with `-E`, for example `npm i -D -E @biomejs/biome`.
- ALWAYS reference the pinned Biome version in `$schema`.
- ALWAYS set `vcs.useIgnoreFile: true` to get the exclusions from `.gitignore`.
- NEVER copy the `.gitignore` exclusions into `files.includes`.
- NEVER install `eslint-plugin-react` when you use Biome.
- ALWAYS use `domains.react: "recommended"` for React rules.
- NEVER install a separate import-sort plugin when you use Biome.
- ALWAYS use `assist.actions.source.organizeImports: "on"` to sort imports.
