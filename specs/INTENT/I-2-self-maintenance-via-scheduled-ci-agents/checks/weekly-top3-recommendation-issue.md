# Agent check: weekly recommender opens one top-3 recommendation issue (markdown table) for the user to choose from

## SHALL
**WHEN** the weekly scheduled workflow runs **THE SYSTEM SHALL** scan the user's GitHub activity from the past 7 days, cross-reference existing cheatsheets, and open a single issue presenting at most the top 3 highest-value newly-adopted frameworks not already covered as a markdown table for the user to choose from — opening no issue when no new topic surfaces. [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/weekly-top3-recommendation-issue.md]

## Success criteria
_Enrich this section with concrete pass conditions: what files to inspect, what patterns count as satisfaction, what file:line evidence the subagent should cite. The seeded SHALL alone is intentionally minimal — `spec-check` will run against whatever is here, so the more specific the better._
