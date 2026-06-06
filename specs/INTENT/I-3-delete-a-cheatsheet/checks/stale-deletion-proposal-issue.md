# Agent check: scheduled staleness workflow opens one issue proposing only >1-year-unused cheatsheets as a markdown table

## SHALL
**WHEN** the scheduled staleness workflow runs **THE SYSTEM SHALL** inspect the owner's GitHub usage history via the `gh` CLI and open a single issue presenting, as a markdown table, only those cheatsheets whose target has not appeared in the owner's activity for more than one year — opening no issue when every cheatsheet's target was used within the past year. [test: agent:specs/INTENT/I-3-delete-a-cheatsheet/checks/stale-deletion-proposal-issue.md]

## Success criteria
_Enrich this section with concrete pass conditions: what files to inspect, what patterns count as satisfaction, what file:line evidence the subagent should cite. The seeded SHALL alone is intentionally minimal — `spec-check` will run against whatever is here, so the more specific the better._
