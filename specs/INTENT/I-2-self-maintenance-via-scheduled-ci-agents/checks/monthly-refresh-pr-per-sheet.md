# Agent check: monthly refresh re-mines repos and opens one PR per materially-changed cheatsheet

## SHALL
**WHEN** the monthly scheduled workflow runs **THE SYSTEM SHALL** re-mine the user's repositories via the `gh` CLI, regenerate each existing cheatsheet against current documentation, and open exactly one pull request per materially-changed cheatsheet — opening no PR for a cheatsheet whose content is unchanged. [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/monthly-refresh-pr-per-sheet.md]

## Success criteria
_Enrich this section with concrete pass conditions: what files to inspect, what patterns count as satisfaction, what file:line evidence the subagent should cite. The seeded SHALL alone is intentionally minimal — `spec-check` will run against whatever is here, so the more specific the better._
