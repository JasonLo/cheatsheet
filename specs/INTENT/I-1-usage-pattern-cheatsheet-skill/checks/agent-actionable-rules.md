# Agent check: Each cheatsheet has an "Agent rules" section of ALWAYS and NEVER rules.

## SHALL

**WHEN** the skill writes the cheatsheet **THE SYSTEM SHALL** add an "Agent rules" section. Each rule in this section is one ALWAYS or NEVER instruction in point form. Then a coding agent, for example Claude Code, can apply the corrections directly. [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/agent-actionable-rules.md]

## Success criteria

- Read `.claude/skills/cheatsheet/SKILL.md`.
- Read all files in `cheatsheets/*.md`. Do not use a sample.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: it tells the skill to write an "Agent rules" section. It tells the skill to start each bullet with ALWAYS or NEVER, and to give one directive in each bullet.
- PASS for a cheatsheet: it has a `## Agent rules` heading. Each bullet under this heading starts with ALWAYS or NEVER. Bold keywords are correct.
- PASS for a cheatsheet: each bullet gives one imperative directive in point form.
- FAIL: a cheatsheet has no `## Agent rules` section.
- FAIL: a bullet in this section has no ALWAYS or NEVER keyword at its start.
- FAIL: a bullet is a paragraph of prose, gives more than one directive, or uses the old → new form of the Learnings section.
- Cite the `.claude/skills/cheatsheet/SKILL.md` lines that give the instruction.
- Cite the file:line of the `## Agent rules` heading in each cheatsheet. For each failure, cite the file:line of the bullet.
