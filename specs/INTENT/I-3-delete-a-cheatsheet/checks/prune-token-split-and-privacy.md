# Agent check: prune/delete workflows use read-only cross-repo token + in-repo GITHUB_TOKEN and never disclose private repos in issue/PR content

## SHALL
**WHILE** a staleness or selection-triggered delete workflow runs **THE SYSTEM SHALL** read cross-repository GitHub data only through a read-only token via the `gh` CLI, perform writes (the proposal issue, the deletion PR) only within this repository via the default `GITHUB_TOKEN`, and exclude every private repository's name/slug/URL and verbatim content from issue and PR content (Constitution P-5, P-7). [test: agent:specs/INTENT/I-3-delete-a-cheatsheet/checks/prune-token-split-and-privacy.md]

## Success criteria
_Enrich this section with concrete pass conditions: what files to inspect, what patterns count as satisfaction, what file:line evidence the subagent should cite. The seeded SHALL alone is intentionally minimal — `spec-check` will run against whatever is here, so the more specific the better._
