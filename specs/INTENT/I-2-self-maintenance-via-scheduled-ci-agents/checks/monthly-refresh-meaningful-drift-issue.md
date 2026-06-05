# Agent check: monthly refresh opens one issue flagging only meaningfully-drifted cheatsheets

## SHALL
**WHEN** the monthly scheduled workflow runs **THE SYSTEM SHALL** re-mine the user's repositories via the `gh` CLI, regenerate each existing cheatsheet against current documentation, and open a single issue presenting as a markdown table only those cheatsheets whose content changed in meaning — a conceptual or semantic shift in an idiom, Learning, or Agent rule (e.g. an obsolete API pattern or a changed best practice) — ignoring wording, reordering, and cosmetic edits, and opening no issue when no cheatsheet changed meaningfully. [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/monthly-refresh-meaningful-drift-issue.md]

## Success criteria
_Enrich this section with concrete pass conditions: what files to inspect, what patterns count as satisfaction, what file:line evidence the subagent should cite. The seeded SHALL alone is intentionally minimal — `spec-check` will run against whatever is here, so the more specific the better._
