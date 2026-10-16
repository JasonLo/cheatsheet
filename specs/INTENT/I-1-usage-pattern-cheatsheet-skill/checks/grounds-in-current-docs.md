# Agent check: The skill uses context7 or a web search to find current practice and marks each usage.

## SHALL

**WHEN** the skill has the files **THE SYSTEM SHALL** find the current best practice for the target in context7 documentation. If context7 has no data for the target, the skill uses a web search. Then the skill marks each usage as current or not current. [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/grounds-in-current-docs.md]

## Success criteria

- Read `.claude/skills/cheatsheet/SKILL.md`.
- Read all files in `cheatsheets/*.md`. Do not use a sample. Read the grounding line under the title of each file.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: a workflow step tells the skill to get the current docs from context7, with `resolve-library-id` and `query-docs`.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: the same step tells the skill to use WebSearch and WebFetch when context7 has no entry for the target.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: a later step tells the skill to mark each usage as current or not current. This step comes after the step that collects the files.
- PASS for a cheatsheet: its grounding line names the source of the current practice. Examples are a context7 library ID or an official docs site.
- FAIL: `.claude/skills/cheatsheet/SKILL.md` has no context7 step, has no web fallback, or has no step that marks each usage.
- FAIL: a cheatsheet has no grounding line with a source of current practice.
- Cite the `.claude/skills/cheatsheet/SKILL.md` lines for each PASS condition.
- Cite the file:line of the grounding line in each cheatsheet that fails.
