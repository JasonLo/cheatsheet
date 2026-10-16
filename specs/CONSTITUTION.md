# Constitution: cheatsheet

Ratified: 2026-06-05

This file contains the non-negotiable principles of the project. Each other `spec-` skill checks its output against this file. A skill does not write output that breaks a principle.

## Stack choice

- **P-1:** The project SHALL manage dependencies with uv.
- **P-2:** Executable code SHALL be self-contained uv scripts with inline script metadata (PEP 723). The project SHALL run each script with `uv run`. The project NEVER adds a packaged module layout, a separate build step, or a second dependency manager.
- **P-5:** The project SHALL get GitHub data only through the `gh` CLI. The project NEVER calls the GitHub REST or GraphQL API directly. It NEVER adds a GitHub SDK or client library as a dependency.

## Architecture

- **P-3:** The project SHALL use the most simple solution that satisfies the need. It NEVER adds abstraction, indirection, frameworks, or dependencies that no concrete requirement needs.
- **P-6:** Skills (prompted agent workflows) SHALL do the tasks that are abstract, ambiguous, or that need judgment. Code SHALL do the concrete, deterministic tasks. The project NEVER puts open-ended judgment into rigid code. It NEVER puts a deterministic, well-defined task into a skill.

## Artifacts

- **P-4:** The repository root SHALL contain an `index.md` that lists each cheatsheet in the repository.
- ~~**P-8:** All prose in the repository SHALL conform to ASD-STE100 Simplified Technical English (Issue 9). This rule covers cheatsheets, `index.md`, `README.md`, `CLAUDE.md`, all `SKILL.md` files, all files in `specs/`, code comments, docstrings, and new commit messages. Prose SHALL use only STE-approved words in their approved meanings, technical names, or technical verbs. A procedural sentence SHALL have 20 words or fewer. A descriptive sentence SHALL have 25 words or fewer. Each sentence SHALL give one instruction only. Instructions SHALL use the imperative and the active voice. Code, commands, identifiers, file paths, URLs, and quoted tool output are exempt. The rule applies to existing text, not only to new text.~~ [superseded 2026-10-15]
- ~~**P-8:** All prose in the repository SHALL conform to ASD-STE100 Simplified Technical English (Issue 9). This rule covers cheatsheets, `index.md`, `README.md`, `CLAUDE.md`, all `SKILL.md` files, all files in `specs/`, code comments, docstrings, and new commit messages. Prose SHALL use only STE-approved words in their approved meanings, technical names, or technical verbs. A procedural sentence SHALL have 20 words or fewer. A descriptive sentence SHALL have 25 words or fewer. Each sentence SHALL give one instruction only. Instructions SHALL use the imperative and the active voice. Code, commands, identifiers, file paths, URLs, and quoted tool output are exempt. The rule applies to existing text, not only to new text. Text in append-only history sections (`## Change Log` in intents and `## Amendments` in this file) stays as its author wrote it, but new entries SHALL conform.~~ [superseded 2026-10-16]
- **P-8:** All prose in the repository SHALL conform to ASD-STE100 Simplified Technical English (Issue 9). This rule covers cheatsheets, `index.md`, `README.md`, `CLAUDE.md`, all `SKILL.md` files, all files in `specs/`, code comments, docstrings, and new commit messages. Prose SHALL use only STE-approved words in their approved meanings, technical names, or technical verbs. A procedural sentence SHALL have 20 words or fewer. A descriptive sentence SHALL have 25 words or fewer. Each sentence SHALL give one instruction only. Instructions SHALL use the imperative and the active voice. Code, commands, identifiers, file paths, URLs, and quoted tool output are exempt. The rule applies to existing text, not only to new text. Old text in append-only history sections (`## Change Log` in intents and `## Amendments` in this file) does not change. New entries SHALL conform. The project verifies P-8 with two checks. `tests/test_ste_prose.py` checks all repository prose for sentence length and for words that STE does not approve. The agent check `specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/prose-in-ste.md` checks the other STE rules in cheatsheet prose. Prose that passes these checks conforms to P-8. A check against the full ASD-STE100 dictionary is not necessary.

## Security

- **P-7:** Generated cheatsheets and committed artifacts SHALL NOT show the name, owner/repo slug, or URL of a private repository. They SHALL NOT quote or copy code or text from a private repository. WHEN a usage pattern comes from a private repository, the project SHALL give it only in a general form. This form has no repository identifier and no private text. Artifacts MAY cite and quote public repositories.

## Amendments

- **2026-06-05** — Initial constitution ratified.
- **2026-06-05** — Added P-5 (Stack choice): GitHub data accessed via the `gh` CLI, no direct API calls or SDK dependency. Reason: keep GitHub access aligned with the project's minimal-tooling stance (P-1/P-3).
- **2026-06-05** — Added P-6 (Architecture): skills handle abstract/judgment-heavy tasks, code handles concrete deterministic implementation. Reason: route each task to the mechanism suited to it.
- **2026-06-05** — Added P-7 (Security): generated artifacts never disclose a private repository's name/slug/URL or quote its code/content; private-sourced patterns are conveyed redacted and generalized. Reason: mining the user's own repos must not leak anything from the private ones.
- **2026-10-15** — Added P-8 (Artifacts): all repository prose conforms to ASD-STE100 Simplified Technical English (Issue 9), applied retroactively to existing text. Reason: user requirement that all language use the ASD-STE standard.
- **2026-10-15** — Rewrote the preamble and P-1 to P-7 in ASD-STE100 Simplified Technical English. Their meaning did not change. Superseded P-8 with a new text. Old entries in append-only history sections stay as written, but new entries must conform. Reason: P-8 applies to this file, and the append-only rule does not let anyone rewrite old history entries.
- **2026-10-16** — Superseded P-8 with a text that states how the project verifies it. The checks are `tests/test_ste_prose.py` and the STE agent check for cheatsheets. Reason: the full ASD-STE100 dictionary is not available, so P-8 needs a defined check.
