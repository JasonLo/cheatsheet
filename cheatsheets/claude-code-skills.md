# Claude Code skills with SKILL.md

_Grounded in JasonLo's repos as of 2026-06-05; current practice per Claude Code docs (code.claude.com/docs/en/skills) + Anthropic "Equipping agents with Agent Skills"._

## Reference snippet

````markdown
<!-- .claude/skills/summarize-diff/SKILL.md  (dir name → /summarize-diff) -->
---
name: summarize-diff
description: >-
  Summarizes uncommitted changes and flags anything risky. Use when the user
  asks what changed, wants a commit message, or asks to review their diff.
allowed-tools: Read, Grep, Bash(git diff *), Bash(git status *)
# disable-model-invocation: true   # only-you trigger; for side-effectful /deploy, /commit
---

# summarize-diff

Body loads ONLY when the skill fires (progressive disclosure level 2).
Keep it under ~500 lines; push bulk detail to sibling files.

## When to use
- The user asks "what changed" / wants a commit message.

## Steps
1. Run `git diff` and `git status`.
2. Group changes, flag risky edits, propose a commit message.

## Reference
- Detailed conventions: see [reference.md](reference.md)  <!-- level 3: loaded on demand -->
````

## Typical usage patterns

- **Action-oriented `description` with explicit triggers** — third-person "Verbs X. Use when Y. Triggers on '...'." Reach for it on every skill: it is the only thing Claude reads to decide whether to load you. (seen in `JasonLo/skill-sommelier:skills/ss-skill-craft/SKILL.md`, `JasonLo/cheatsheet:.claude/skills/cheatsheet/SKILL.md`)
- **One skill = one focused capability** — split if it does two things; route-by-mode inside one skill only when modes share a domain. (seen in `JasonLo/best-in-slot:slots/claude-code/skill-md/README.md`)
- **Progressive disclosure via sibling files** — keep `SKILL.md` lean; bundle templates/reference and reference them by name so they load only when needed. (seen in `JasonLo/lite-spec:skills/spec-intent/` — `INTENT.template.md`, `AGENT_PROMPT_SEED.template.md`)
- **`allowed-tools` to pre-approve a skill's tools** — list the tools the workflow needs so it runs without permission prompts. (seen in `JasonLo/skill-sommelier:skills/ss-skill-craft/SKILL.md`)
- **Minimal SKILL.md, no runtime** — frontmatter + prose steps, no scripts unless shell/curl genuinely can't do it; a skill is instructions, not a program. (seen in `JasonLo/best-in-slot:slots/claude-code/skill-md/example/skills/hello/SKILL.md`, `JasonLo/undock:.claude/skills/sync-docs/SKILL.md`)
- **Public `skills/` vs maintainer-only folder** — distribute user-facing skills under `skills/`; keep release/maintenance skills in a separate `maintainer-skills/` tree. (seen in `JasonLo/skill-sommelier`)

## Learnings

- **"`name` sets the command you type"** → **"the directory name sets the command; `name` is just a display label."** `.claude/skills/deploy/SKILL.md` is `/deploy` regardless of frontmatter `name`. `name` only sets the invocation at a *plugin-root* `SKILL.md`. Stop hand-syncing `name` to the slash command. (seen in `JasonLo/best-in-slot:slots/claude-code/skill-md/CHEATSHEET.md`)
- **"`triggers:` is a frontmatter field"** → **"trigger phrasing lives inside `description` (or the optional `when_to_use`)."** There is no `triggers` field; fold trigger phrases into `description`, front-loaded — the combined `description`+`when_to_use` is truncated at 1,536 chars in the listing. Put the key use case first. (seen in `JasonLo/best-in-slot:slots/claude-code/skill-md/README.md`)
- **"Skills and slash commands are different mechanisms"** → **"commands are merged into skills."** A `.claude/commands/x.md` and a `.claude/skills/x/SKILL.md` both make `/x`; old command files still work, but skills are the recommended form (supporting files, auto-invocation, invocation control). Author new procedures as skills.
- **"Put everything the agent might need into SKILL.md"** → **"three-level progressive disclosure."** Metadata (name+description) preloads; the body loads on trigger; bundled files load only when referenced. A fat SKILL.md burns context on every load — split mutually-exclusive paths into sibling files.
- **"A skill is a subagent / runs in its own context"** → **"a skill runs inline by default; forking is opt-in."** Skill content joins the current context unless you set `context: fork` (+ `agent`). Don't assume isolation — for an autonomous side-effect workflow, gate it with `disable-model-invocation: true`, not by hoping it's sandboxed.
- **"Auto-invocation is always fine"** → **"side-effectful workflows must be user-only."** Set `disable-model-invocation: true` for `/deploy`, `/commit`, anything with consequences, so Claude doesn't fire it because the code "looks ready."

## Agent rules

- ALWAYS put the command-determining name in the skill's directory name; treat frontmatter `name` as a display label only (except at a plugin-root `SKILL.md`).
- ALWAYS write `description` in third person, action-first, with explicit trigger phrases, key use case first; keep `description`+`when_to_use` under 1,536 chars.
- NEVER add a `triggers:` frontmatter field — fold trigger phrasing into `description` (or `when_to_use`).
- ALWAYS keep `SKILL.md` under ~500 lines; move bulk reference/templates to sibling files and reference them by name.
- ALWAYS scope a skill to one capability; split a two-job skill.
- ALWAYS author new procedures as a `.claude/skills/<name>/SKILL.md` rather than a `.claude/commands/*.md` file.
- ALWAYS set `disable-model-invocation: true` on any skill with side effects (deploy, commit, send-message).
- ALWAYS set `context: fork` (and `agent`) explicitly when a skill must run isolated; never assume a skill is sandboxed by default.
- ALWAYS list a workflow's required tools in `allowed-tools` to avoid permission prompts; review project-checked-in `allowed-tools` before trusting a repo.
- NEVER add scripts to a skill unless shell/markdown instructions genuinely cannot express the task.
