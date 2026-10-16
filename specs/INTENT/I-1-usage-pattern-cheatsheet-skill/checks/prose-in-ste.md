# Agent check: Cheatsheet prose follows ASD-STE100 Simplified Technical English.

## SHALL

**WHEN** the skill writes a cheatsheet **THE SYSTEM SHALL** write all prose in ASD-STE100 Simplified Technical English (Constitution P-8). Code, commands, identifiers, file paths, URLs, and quoted tool output are exempt. [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/prose-in-ste.md]

## Success criteria

- The pytest test `tests/test_ste_prose.py::test_cheatsheet_sentence_length` checks the length of each sentence. This agent check does not count words.
- This agent check covers the other STE rules.
- Read `.claude/skills/cheatsheet/SKILL.md`.
- Read all files in `cheatsheets/*.md`. Do not use a sample.
- Do not check code blocks, inline code, commands, identifiers, file paths, URLs, citations, or quoted tool output. These are exempt.
- PASS for `.claude/skills/cheatsheet/SKILL.md`: it tells the skill to write all prose in ASD-STE100 Simplified Technical English (P-8).
- PASS for a cheatsheet: the prose uses simple approved words and has no idioms or figurative language.
- PASS for a cheatsheet: the prose uses the active voice.
- PASS for a cheatsheet: each instruction uses the imperative and gives one instruction for each sentence.
- PASS for a cheatsheet: the prose has no semicolons, no contractions, and no "e.g.".
- PASS for a cheatsheet: the prose has no noun clusters of more than 3 words.
- PASS: technical names and technical verbs are correct STE. Examples are library names, API names, "deploy", "commit", and "cache".
- FAIL: a sentence breaks one of these rules.
- Cite the `.claude/skills/cheatsheet/SKILL.md` lines for STE.
- Cite the file:line of each sentence that fails, and name the rule that it breaks.
