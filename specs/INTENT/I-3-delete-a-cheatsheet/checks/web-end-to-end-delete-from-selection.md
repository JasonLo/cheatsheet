# Agent check: owner comment-selection on a staleness issue deletes selected sheets and opens one run-scoped PR, web-complete, no auto-merge

## SHALL
**WHEN** the repository owner comments a selection (e.g. "1 and 3") on an open staleness proposal issue **THE SYSTEM SHALL** delete every selected cheatsheet via the deterministic deletion path (removing each file and updating `index.md`) and open exactly one run-scoped pull request bundling all selected deletions and the index update — requiring no local execution and never auto-merging — so the propose → select → delete → review loop completes entirely within the GitHub web interface. [test: agent:specs/INTENT/I-3-delete-a-cheatsheet/checks/web-end-to-end-delete-from-selection.md]

## Success criteria
_Enrich this section with concrete pass conditions: what files to inspect, what patterns count as satisfaction, what file:line evidence the subagent should cite. The seeded SHALL alone is intentionally minimal — `spec-check` will run against whatever is here, so the more specific the better._
