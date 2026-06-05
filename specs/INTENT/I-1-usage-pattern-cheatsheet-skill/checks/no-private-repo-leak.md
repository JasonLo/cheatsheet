# Agent check: the cheatsheet never discloses or reproduces a private repository

## SHALL
**WHILE** writing the cheatsheet **THE SYSTEM SHALL** exclude the name, owner/repo slug, URL, and verbatim code or content of any private repository — citing and quoting only public sources, and conveying patterns learned from private repositories in redacted, generalized form (Constitution P-7). [test: agent:specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/no-private-repo-leak.md]

## Success criteria
- Inspect every file under `cheatsheets/*.md`.
- For each `owner/repo` or `owner/repo:path` reference and each fenced code block, the cited/quoted repo MUST be public (verify with `gh repo view <owner>/<repo> --json visibility`). Any private repo name, slug, URL, or verbatim private content = FAIL.
- PASS only if no private-repo identifier or content appears. Cite file:line of any violation found, or the cleanest reference checked if none.
