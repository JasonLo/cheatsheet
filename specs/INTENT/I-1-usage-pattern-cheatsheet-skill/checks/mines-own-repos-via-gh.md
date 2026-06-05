# Agent check: skill resolves the authenticated user and mines their own repos via gh before analyzing

## SHALL
**WHEN** invoked with a use case and an explicit target **THE SYSTEM SHALL** resolve the authenticated GitHub user via the `gh` CLI and collect, from that user's repositories, the files relevant to the target before analyzing. [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/mines-own-repos-via-gh.md]

## Success criteria
_Enrich this section with concrete pass conditions: what files to inspect, what patterns count as satisfaction, what file:line evidence the subagent should cite. The seeded SHALL alone is intentionally minimal — `spec-check` will run against whatever is here, so the more specific the better._
