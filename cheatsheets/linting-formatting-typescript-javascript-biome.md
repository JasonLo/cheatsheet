# Linting & formatting TypeScript/JavaScript with Biome

_Grounded in JasonLo's repos as of 2026-11-03. Current practice is from Biome official docs (biomejs.dev), Biome 2.5+._

## Reference snippet

```json
{
  "$schema": "https://biomejs.dev/schemas/2.5.15/schema.json",
  "vcs": { "enabled": true, "clientKind": "git", "useIgnoreFile": true },
  "files": { "includes": ["**", "!dist"] },
  "formatter": { "indentStyle": "space", "indentWidth": 2, "lineWidth": 80 },
  "linter": {
    "enabled": true,
    "rules": { "preset": "recommended" },
    "domains": { "react": "recommended" }
  },
  "assist": { "actions": { "source": { "organizeImports": "on" } } },
  "javascript": { "formatter": { "quoteStyle": "single", "semicolons": "asNeeded" } }
}
```

## Typical usage patterns

- **One check command for all tasks.** The `biome check --write` command runs the formatter, the linter, and the import organizer in one pass. For CI pipelines, `biome ci` is the read-only command. (seen in `JasonLo/skill-cellar:package.json`)
- **File exclusion from VCS.** The `vcs.useIgnoreFile: true` setting makes Biome use `.gitignore` as its ignore list. Use `files.includes` negations only for tracked files that Biome must not lint, for example generated bindings. (seen in `JasonLo/jasonlo.dev:biome.jsonc`)
- **Framework rules by domain.** The `linter.domains.react: "recommended"` setting adds the React rule set. Place the `domains` key inside `linter`, not at the JSON root. (seen in `JasonLo/skill-cellar:biome.json`)

## Learnings

- **Separate tools format, lint, and sort imports** → **One tool runs the full pipeline.** Biome does all three tasks from one config file. The `biome check --write` command replaces `eslint . && prettier --write .`, `.prettierrc`, and the import-sort plugin.
- **`domains.react` at the JSON root** → **`linter.domains.react` inside the linter object.** Biome 2.5 moved domain configuration under `linter`. The root-level `domains` key no longer has any effect.
- **`rules.recommended: true` (boolean flag)** → **`rules.preset: "recommended"` (named preset).** Biome 2.5 replaced the boolean toggle with named preset strings. Use `"preset": "recommended"` to select the recommended rules.

## Agent rules

- ALWAYS run `biome check --write` for the combined format, lint, and import-sort pass.
- ALWAYS use `biome ci` in CI, not `biome check`.
- ALWAYS pin the exact Biome version with `-E`, for example `npm i -D -E @biomejs/biome`.
- ALWAYS reference the pinned Biome version in `$schema`.
- ALWAYS set `vcs.useIgnoreFile: true` to get the exclusions from `.gitignore`.
- NEVER copy the `.gitignore` exclusions into `files.includes`.
- NEVER install `eslint-plugin-react` when you use Biome.
- ALWAYS use `linter.domains.react: "recommended"` for React rules, not `domains.react` at the JSON root.
- NEVER install a separate import-sort plugin when you use Biome.
- ALWAYS use `assist.actions.source.organizeImports: "on"` to sort imports.
- ALWAYS use `linter.rules.preset: "recommended"`, not `linter.rules.recommended: true`.
