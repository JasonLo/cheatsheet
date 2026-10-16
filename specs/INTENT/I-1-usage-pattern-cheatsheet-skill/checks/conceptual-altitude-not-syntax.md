# Agent check: Learnings corrections are about concepts and intent, not syntax.

## SHALL

**WHILE** the skill writes the "Learnings" section **THE SYSTEM SHALL** write each correction at the level of concept and intent. The skill does not write corrections about syntax or API signatures. [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/conceptual-altitude-not-syntax.md]

## Success criteria

- Read `.claude/skills/cheatsheet/SKILL.md`.
- Read all files in `cheatsheets/*.md`. Do not use a sample. Inspect the `## Learnings` section of each file.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: it tells the skill to write each Learning at the level of intent and mental model. It tells the skill not to write a change that is only syntax.
- PASS for a Learning: it names a change in concept, intent, or mental model, and it gives the reason.
- PASS: a Learning can name an API or a code token, if the bullet also gives the change in concept.
- FAIL: a Learning is only a syntax change or a signature change. An example is "`x()` is now `y()`" with no reason in concept.
- Cite the `.claude/skills/cheatsheet/SKILL.md` lines that give the instruction.
- Cite the file:line of each Learning that fails. If all pass, cite one strong example for each cheatsheet.
