# Agent check: weekly recommender opens one proposal-stub PR per uncovered newly-adopted framework

## SHALL
**WHEN** the weekly scheduled workflow runs **THE SYSTEM SHALL** scan the user's GitHub activity from the past 7 days, cross-reference existing cheatsheets, and open one proposal-stub PR adding `proposals/<slug>.md` per newly-adopted framework not already covered — opening no PR when no new topic surfaces. [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/weekly-proposal-stub-prs.md]

## Success criteria
_Enrich this section with concrete pass conditions: what files to inspect, what patterns count as satisfaction, what file:line evidence the subagent should cite. The seeded SHALL alone is intentionally minimal — `spec-check` will run against whatever is here, so the more specific the better._
