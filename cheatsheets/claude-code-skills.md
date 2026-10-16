# Claude Code skills with SKILL.md

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from Claude Code docs (code.claude.com/docs/en/skills) and Anthropic "Equipping agents with Agent Skills"._

## Reference snippet

```markdown
<!-- .claude/skills/summarize-diff/SKILL.md. The directory name gives /summarize-diff. -->
---
name: summarize-diff
description: >-
  Summarizes uncommitted changes and flags anything risky. Use when the user
  asks what changed, wants a commit message, or asks to review their diff.
allowed-tools: Read, Grep, Bash(git diff *), Bash(git status *)
# disable-model-invocation: true   # Only the user can start it. Use for /deploy, /commit, and other commands with side effects.
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
- Detailed conventions: see [reference.md](reference.md)  <!-- Level 3. Claude loads this file only when necessary. -->
```

## Typical usage patterns

- **Action-oriented `description` with stated triggers.** Write it in the third person, with the action first and stated trigger phrases. Claude reads only this field to decide when to load the skill. (seen in `JasonLo/skill-sommelier:skills/ss-skill-craft/SKILL.md`, `JasonLo/cheatsheet:.claude/skills/cheatsheet/SKILL.md`)
- **One skill for one focused capability.** Split a skill that does two jobs. Route by mode inside one skill only when the modes share a domain. (seen in `JasonLo/best-in-slot:slots/claude-code/skill-md/README.md`)
- **Progressive disclosure with sibling files.** `SKILL.md` stays small and names the sibling files that hold templates and reference text. Claude loads a sibling file only when it needs it. (seen in `JasonLo/lite-spec:skills/spec-intent/` with `INTENT.template.md` and `AGENT_PROMPT_SEED.template.md`)

## Learnings

- **The `name` field sets the command** → **The directory name sets the command**. The file `.claude/skills/deploy/SKILL.md` is `/deploy` for all values of `name`, which is a display label. Only a *plugin-root* `SKILL.md` uses `name` for the command. (seen in `JasonLo/best-in-slot:slots/claude-code/skill-md/CHEATSHEET.md`)
- **Triggers are a separate setting** → **Trigger phrases are part of the description**. There is no `triggers` field, so put trigger phrases in `description` or `when_to_use`. The listing cuts the combined text at 1,536 characters, so put the key use case first. (seen in `JasonLo/best-in-slot:slots/claude-code/skill-md/README.md`)
- **A skill runs isolated, like a subagent** → **A skill runs inline in the current context by default**. To isolate a skill, set `context: fork` and `agent`. To control a workflow with side effects, use `disable-model-invocation: true`, not a sandbox.

## Agent rules

- ALWAYS set the command with the skill directory name, not frontmatter `name`, outside a plugin root.
- ALWAYS start a third-person `description` with the action and the key use case.
- ALWAYS keep `description` and `when_to_use` together under 1,536 characters.
- NEVER add a `triggers:` frontmatter field.
- ALWAYS put trigger phrases in `description` or `when_to_use`.
- ALWAYS keep `SKILL.md` below about 500 lines.
- ALWAYS move large reference text and templates to sibling files.
- ALWAYS scope a skill to one capability.
- ALWAYS split a skill that does two jobs into two skills.
- ALWAYS write new procedures as `.claude/skills/<name>/SKILL.md`, not as a `.claude/commands/*.md` file.
- ALWAYS set `disable-model-invocation: true` on a skill with side effects, for example deploy, commit, or send-message.
- ALWAYS set `context: fork` and `agent` when a skill must run isolated.
- NEVER assume that a skill runs in a sandbox by default.
- ALWAYS list the tools that a workflow needs in `allowed-tools` to prevent permission prompts.
- ALWAYS review the `allowed-tools` in a repository before you trust that repository.
- NEVER add scripts to a skill unless shell commands or markdown instructions cannot do the task.
