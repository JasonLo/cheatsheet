# Agent check: The monthly refresh opens one issue that lists only cheatsheets with a change in meaning.

## SHALL

**WHEN** the monthly scheduled workflow runs **THE SYSTEM SHALL** open one issue with a markdown table of the cheatsheets whose meaning changed. The workflow mines the user's repositories again with the `gh` CLI. It makes each cheatsheet again with the current documentation. A change in meaning is a change in the concept of a usage pattern, a Learning, or an Agent rule. An old API pattern and a new best practice are examples. The workflow ignores changes in wording, changes in order, and cosmetic changes. If no cheatsheet changed in meaning, the workflow opens no issue. [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/monthly-refresh-meaningful-drift-issue.md]

## Success criteria

- Read `.github/workflows/cheatsheet-refresh.yml` and `.claude/skills/cheatsheet/SKILL.md`.
- PASS: the workflow has a monthly `schedule:` cron and a `workflow_dispatch:` trigger.
- PASS: the prompt mines the user's repos again with `gh` and makes each cheatsheet again with current docs. It uses the I-1 skill or the same steps.
- PASS: the prompt keeps a cheatsheet only if its meaning changed. A change in meaning is a change in the concept of a usage pattern, a Learning, or an Agent rule.
- PASS: the prompt ignores changes in wording, changes in order, cosmetic changes, and a new date in the grounding line.
- PASS: the prompt opens exactly one issue with a markdown table. It opens no issue when no cheatsheet changed in meaning.
- PASS: the issue title starts with `Cheatsheet refresh`, so `.github/workflows/cheatsheet-generate.yml` accepts a selection on it.
- FAIL: the job commits files, pushes a branch, or opens a pull request.
- FAIL: the prompt opens more than one issue, or opens an issue when no change in meaning occurred.
- Cite the file:line of the trigger, the mining step, the rule for a change in meaning, the "no issue" rule, and the `gh issue create` step.
