# Agent check: cross-repo reads use a read-only token; writes stay in this repo via GITHUB_TOKEN

## SHALL
**WHILE** a self-maintenance workflow runs **THE SYSTEM SHALL** read cross-repository GitHub data only through a read-only token via the `gh` CLI, and perform commits/PRs only within this repository via the default `GITHUB_TOKEN`. [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/least-privilege-token-split.md]

## Success criteria
_Enrich this section with concrete pass conditions: what files to inspect, what patterns count as satisfaction, what file:line evidence the subagent should cite. The seeded SHALL alone is intentionally minimal — `spec-check` will run against whatever is here, so the more specific the better._
