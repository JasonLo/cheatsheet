# Agent check: Each cheatsheet has a short code snippet of current usage.

## SHALL

**WHEN** the analysis is complete **THE SYSTEM SHALL** write one markdown cheatsheet with three parts. The first part is a short code snippet that shows the current correct usage of the target. The second part is a "Typical usage patterns" section. The third part is a "Learnings" section. This section gives each old pattern or error and its current replacement. [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/has-reference-snippet.md]

## Success criteria

- Read `.claude/skills/cheatsheet/SKILL.md`.
- Read all files in `cheatsheets/*.md`. Do not use a sample.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: its template has a `## Reference snippet` section with one fenced code block. It tells the skill to take this block from the current docs, not from the mined files.
- PASS for a cheatsheet: it has a `## Reference snippet` heading before `## Typical usage patterns`. One fenced code block follows the heading.
- PASS for a cheatsheet: the block is short and shows the current usual form of the target. It is not a list of API calls.
- FAIL: a cheatsheet has no `## Reference snippet` section or no code block in it.
- FAIL: the block uses a pattern that the `## Learnings` section of the same file calls old.
- Cite the `.claude/skills/cheatsheet/SKILL.md` lines of the template.
- Cite the file:line of the snippet heading in each cheatsheet. For each failure, cite the file:line of the problem.
