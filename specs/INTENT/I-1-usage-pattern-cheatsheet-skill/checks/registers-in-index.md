# Agent check: Each cheatsheet has an entry in the root `index.md`.

## SHALL

**WHEN** the skill writes a cheatsheet file **THE SYSTEM SHALL** add an entry for that file to the `index.md` file in the repository root. [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/registers-in-index.md]

## Success criteria

- Read `.claude/skills/cheatsheet/SKILL.md`, `index.md`, and `scripts/register_cheatsheet.py`.
- Use Glob to list all files in `cheatsheets/*.md`.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: a workflow step runs `uv run scripts/register_cheatsheet.py` after the skill writes the cheatsheet. It tells the skill not to edit `index.md` manually.
- PASS for `scripts/register_cheatsheet.py`: it writes one `index.md` entry for each file in `cheatsheets/`.
- PASS for `index.md`: it has exactly one link for each file in `cheatsheets/*.md`.
- FAIL: a cheatsheet file has no entry in `index.md`.
- FAIL: an `index.md` entry links to a file that does not exist.
- FAIL: `.claude/skills/cheatsheet/SKILL.md` has no step that registers the cheatsheet.
- Cite the `.claude/skills/cheatsheet/SKILL.md` line of the step and the file:line of the script logic.
- Cite each missing or extra entry. If all pass, give the number of files and the number of entries.
