# Agent check: Cheatsheet content is short points with only useful detail.

## SHALL

**WHILE** the skill writes a section **THE SYSTEM SHALL** use short points. A point gives an explanation only if it is an important tip for the future or helps the user learn. The skill removes all other detail. [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/concise-point-form.md]

## Success criteria

- Read `.claude/skills/cheatsheet/SKILL.md`.
- Read all files in `cheatsheets/*.md`. Do not use a sample.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: it tells the skill to write short points. It tells the skill to keep detail only when it is an important tip for the future or helps the user learn.
- PASS for a cheatsheet: the content of each section is in bullets, except the reference snippet and the grounding line under the title.
- The test `tests/test_cheatsheet_form.py::test_cheatsheet_point_form` checks the structure and the sentence count. This agent check covers the value of the detail.
- PASS for a bullet: it has one or two short sentences. A bold label at the start of a usage bullet does not count as a sentence. The bold old → new head of a Learning does not count as a sentence.
- PASS for a sentence of detail: it is a tip for the future, or it helps the user learn.
- FAIL: a section has a paragraph of prose in place of bullets.
- FAIL: a bullet has incidental detail, for example history, a long story, or text that repeats a different bullet.
- Cite the `.claude/skills/cheatsheet/SKILL.md` lines that give the instruction.
- Cite the file:line of each failure. If all pass, cite one sample section for each cheatsheet.
