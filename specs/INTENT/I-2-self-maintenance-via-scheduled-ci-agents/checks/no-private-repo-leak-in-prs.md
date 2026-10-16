# Agent check: Pull requests do not show private repository content.

## SHALL

**WHILE** the system writes pull-request content **THE SYSTEM SHALL** not show the name, slug, URL, code, or text of a private repository (Constitution P-7). It gives patterns from private repositories only in a general form. [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/no-private-repo-leak-in-prs.md]

## Success criteria

- Read `.github/workflows/cheatsheet-generate.yml`. Read the prompt for the pull request title, body, and commit message.
- Read `.github/workflows/cheatsheet-recommend.yml` and `.github/workflows/cheatsheet-refresh.yml` for the same privacy rules.
- PASS: the prompt tells the agent to get the visibility of each mined repo with `gh repo view <login>/<repo> --json visibility`.
- PASS: the prompt bans the name, slug, URL, code, or text of a private repo in committed files and pull request text.
- PASS: the prompt tells the agent to give patterns from private repos only in a general form. It permits cites of public repos.
- FAIL: the prompt has no privacy section, or the section does not cover the pull request title and body.
- FAIL: the prompt puts a list of mined repos or raw file content in the pull request body with no visibility filter.
- Cite the file:line of the privacy section and the visibility command in each workflow.
