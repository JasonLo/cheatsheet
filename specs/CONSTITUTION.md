# Constitution: cheatsheet

Ratified: 2026-06-05

Non-negotiable project principles. Every other `spec-` skill validates its output against this file and refuses to produce violating output.

## Stack choice

- **P-1:** Dependencies SHALL be managed with uv.
- **P-2:** Executable code SHALL be written as self-contained uv scripts using inline script metadata (PEP 723) and run via `uv run`. The project NEVER introduces a packaged module layout, separate build step, or a second dependency manager.
- **P-5:** GitHub data SHALL be accessed via the `gh` CLI. The project NEVER calls the GitHub REST/GraphQL API directly or adds a GitHub SDK/client-library dependency.

## Architecture

- **P-3:** The project SHALL favor the simplest solution that satisfies the need. It NEVER adds abstraction, indirection, frameworks, or dependencies that a concrete requirement does not demand.
- **P-6:** Abstract, ambiguous, or judgment-heavy tasks SHALL be handled by skills (prompted agent workflows); concrete, deterministic implementation SHALL be handled by code. The project NEVER hard-codes open-ended judgment into rigid code, and NEVER wraps a deterministic, well-defined task in a skill.

## Artifacts

- **P-4:** The repository root SHALL contain an `index.md` that lists every cheatsheet in the repository.

## Amendments

- **2026-06-05** — Initial constitution ratified.
- **2026-06-05** — Added P-5 (Stack choice): GitHub data accessed via the `gh` CLI, no direct API calls or SDK dependency. Reason: keep GitHub access aligned with the project's minimal-tooling stance (P-1/P-3).
- **2026-06-05** — Added P-6 (Architecture): skills handle abstract/judgment-heavy tasks, code handles concrete deterministic implementation. Reason: route each task to the mechanism suited to it.
