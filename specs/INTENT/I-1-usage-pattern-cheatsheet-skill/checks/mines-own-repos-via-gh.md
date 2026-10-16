# Agent check: The skill uses gh to get the user's repo files before the analysis.

## SHALL

**WHEN** the skill starts with a target **THE SYSTEM SHALL** use the `gh` CLI to get the target files from the user's GitHub repositories. The input is a use case and a target. The skill gets the files before the analysis. [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/mines-own-repos-via-gh.md]

## Success criteria

- Read `.claude/skills/cheatsheet/SKILL.md`.
- PASS: an early workflow step runs `gh api user --jq .login` to get the login of the authenticated user.
- PASS: a later step collects the target files from the repos of that login with `gh`. Examples are `gh search code --owner <login>`, `gh repo list <login>`, and `gh api repos/<login>/<repo>/contents/<path>`.
- PASS: these two steps come before the step that finds the current best practice and before the analysis.
- PASS: the inputs section requires a use case and a `--target`.
- FAIL: `.claude/skills/cheatsheet/SKILL.md` uses a direct API call or an SDK in place of the `gh` CLI for GitHub access.
- FAIL: the collection step comes after the analysis, or it does not limit the search to the repos of the user.
- Cite the file:line of the identity step, the collection commands, and the inputs section.
