# Agent check: Cheatsheets do not show private repository content.

## SHALL

**WHILE** the skill writes the cheatsheet **THE SYSTEM SHALL** not show the name, slug, URL, code, or text of a private repository (Constitution P-7). The skill cites and quotes only public sources. It gives patterns from private repositories only in a general form without identifiers. [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/no-private-repo-leak.md]

## Success criteria

- The pytest test `tests/test_no_private_repo_leak.py::test_cited_repos_are_public` checks the visibility of each cited repo. This agent check does not do that.
- This agent check covers the parts that a test cannot measure.
- Read `.claude/skills/cheatsheet/SKILL.md`.
- Read all files in `cheatsheets/*.md`. Do not use a sample.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: it tells the skill to record the visibility of each mined repo.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: it tells the skill to cite only public sources. It tells the skill to give patterns from private repos only in a general form (Constitution P-7).
- PASS for a cheatsheet: each fenced code block and each quote is general. As an alternative, it comes from a cited public source or the official docs.
- PASS for a cheatsheet: a pattern with no cite has a general form. It has no project names, internal hostnames, internal paths, or business details.
- FAIL: a cheatsheet has code or text that looks like a copy of a private project, with no public cite.
- FAIL: a cheatsheet names a project, a host, or a path that identifies a private repo.
- FAIL: `.claude/skills/cheatsheet/SKILL.md` has no instruction for P-7.
- Cite the `.claude/skills/cheatsheet/SKILL.md` lines for P-7.
- Cite the file:line of each failure. If all pass, cite the file:line of the strongest reference that you checked.
