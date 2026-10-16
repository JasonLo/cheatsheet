# Agent check: The weekly recommender opens one issue with not more than 3 new topics.

## SHALL

**WHEN** the weekly scheduled workflow runs **THE SYSTEM SHALL** open one issue that shows the top 3 new frameworks in a markdown table. The workflow scans the user's GitHub activity of the last 7 days. It compares this activity with the current cheatsheets. The table shows only frameworks that no cheatsheet covers, and not more than 3. The user selects frameworks from this table. If the workflow finds no new topic, it opens no issue. [test: agent:specs/INTENT/I-2-self-maintenance-via-scheduled-ci-agents/checks/weekly-top3-recommendation-issue.md]

## Success criteria

- Read `.github/workflows/cheatsheet-recommend.yml`. Use Glob to list `cheatsheets/*.md`.
- PASS: the workflow has a weekly `schedule:` cron and a `workflow_dispatch:` trigger.
- PASS: the prompt scans the user's GitHub activity of the last 7 days with `gh`, through `uv run scripts/gh_scan.py`.
- PASS: the prompt compares the topics that it finds with the current cheatsheets and with `index.md`. It drops each topic that a cheatsheet covers.
- PASS: the prompt opens exactly one issue with a markdown table of not more than 3 topics, in order of value.
- PASS: column 2 of the table is the use case and column 3 is the target in backticks. The generate workflow needs this format.
- PASS: the issue title starts with `Cheatsheet recommendations`. The issue tells the user to comment the numbers of the selected rows.
- PASS: the prompt opens no issue when it finds no new topic.
- FAIL: the job writes files, pushes a branch, or opens a pull request.
- FAIL: the table can have more than 3 rows, or it can list a topic that a cheatsheet covers.
- Cite the file:line of the trigger, the 7-day window, the coverage check, the limit of 3, the table format, and the "no issue" rule.
