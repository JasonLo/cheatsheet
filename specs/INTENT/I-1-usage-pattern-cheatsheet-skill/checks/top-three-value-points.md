# Agent check: The usage and Learnings sections each have only the 3 best points.

## SHALL

**WHILE** the skill writes the "Typical usage patterns" and "Learnings" sections **THE SYSTEM SHALL** put only the 3 most important points in each section. The skill adds a fourth point only for a strong reason. [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/top-three-value-points.md]

## Success criteria

- Read `.claude/skills/cheatsheet/SKILL.md`.
- Read all files in `cheatsheets/*.md`. Do not use a sample. Count the bullets in `## Typical usage patterns` and in `## Learnings` of each file.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: it tells the skill to write only the 3 points with the highest value in each of the two sections. It permits a fourth point only for a strong reason.
- PASS for a cheatsheet: each of the two sections has 3 bullets or fewer.
- PASS for a cheatsheet: a section with 4 or more bullets is correct only if each extra bullet covers a different, important point. The top 3 bullets must not cover it.
- FAIL: a section has more than 3 bullets, and an extra bullet repeats a different bullet or adds little value.
- Cite the `.claude/skills/cheatsheet/SKILL.md` lines of the instruction.
- Give the bullet count of each section for each cheatsheet.
- Cite the file:line of each extra bullet and say if it has a strong reason.
