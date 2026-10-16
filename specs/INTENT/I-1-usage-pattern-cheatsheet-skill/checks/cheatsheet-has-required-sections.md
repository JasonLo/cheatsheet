# Agent check: Each cheatsheet has a "Typical usage patterns" section and a "Learnings" section.

## SHALL

**WHEN** the analysis is complete **THE SYSTEM SHALL** write one markdown cheatsheet with three parts. The first part is a short code snippet that shows the current correct usage of the target. The second part is a "Typical usage patterns" section. The third part is a "Learnings" section. This section gives each old pattern or error and its current replacement. [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/cheatsheet-has-required-sections.md]

## Success criteria

- Read `.claude/skills/cheatsheet/SKILL.md`.
- Read all files in `cheatsheets/*.md`. Do not use a sample.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: its cheatsheet template has a `## Typical usage patterns` section and a `## Learnings` section.
- PASS for a cheatsheet: it has a `## Typical usage patterns` heading and a `## Learnings` heading.
- PASS for a cheatsheet: each Learnings bullet names an old pattern or error and its current replacement. The usual form is `**<old>** → **<new>.**`.
- FAIL: a cheatsheet does not have one of the two headings.
- FAIL: a Learnings bullet gives no old pattern or gives no replacement.
- Cite the `.claude/skills/cheatsheet/SKILL.md` lines of the template.
- Cite the file:line of the two headings in each cheatsheet. For each failure, cite the file:line of the problem.
