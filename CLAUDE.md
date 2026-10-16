# CLAUDE.md

This file gives guidance to Claude Code (claude.ai/code) for work in this repo.

## What this repo is

**cheatsheet** is a personal cheatsheet.

All prose in this repo must be in ASD-STE100 Simplified Technical English
(Constitution P-8). Code, commands, identifiers, file paths, URLs, and quoted tool
output are exempt. To check the sentence length, run `uv run tests/test_ste_prose.py`.

<!-- lite-spec:pointer-block:start -->

## Read before non-trivial work

Before you write output that changes design, architecture, scope, or behavior, load the spec files. Load them only when necessary. If they disagree with CLAUDE.md, the spec files are correct.

- **`specs/CONSTITUTION.md`** contains the non-negotiable principles. Each change to a principle MUST go through `spec-constitution`. Never change a principle silently.
- **`specs/INTENT/`** has one folder for each intent (`I-N-<slug>/intent.md`).
  - The `experiments/` folder, the `checks/` folder, and an optional `plan.md` file appear only when necessary.
  - Open intents have `status: draft` or `in_progress`. Closed intents have `status: complete` or `superseded`.
  - Outcomes use EARS (`WHEN <trigger> THE SYSTEM SHALL <response>`).
  - Load only the intents whose scope is related to your task.
  - Use `spec-intent` to create, refine, or supersede an intent. `spec-check` sets `status` from the number of outcomes that pass.

## Spec file ownership

There are two levels:

- **HUMAN-OWNED.** `specs/CONSTITUTION.md` (governance) and `specs/INTENT/` (product and scope) are human-owned. This includes the full tree and each `I-N-<slug>/intent.md`.
  - AI agents MUST change these files only with `/spec-constitution` and `/spec-intent`.
  - Never change them with a direct Edit, Write, or sed. This rule also applies to a small correction, for example an old count.
  - The exception is the skill-managed frontmatter fields in each `intent.md` (`status`, `closed`, `verdict_*`). `spec-check` writes these fields.
- **AGENT-WRITABLE.** `specs/INTENT/I-N-<slug>/plan.md` is the implementation plan for one intent.
  - The planning handoff of `/spec-intent` writes it, through `/plan`.
  - You can make it again at any time. `intent.md` stays the source of truth.

You can edit the files outside `specs/` normally. These files include the README, this file, the source code, the `SKILL.md` bodies, and the scripts.

## Spec workflow

This repo uses **lite-spec**. Start the skills by name:

- `/spec-init` starts or repairs the lite-spec setup.
- `/spec-constitution` ratifies or amends principles (`specs/CONSTITUTION.md`).
- `/spec-intent` drafts, refines, or supersedes an intent (`specs/INTENT/I-N-<slug>/intent.md`).
- `/spec-check` gives a drift report and sets the status of each open intent.

<!-- lite-spec:pointer-block:end -->

## Git workflow

When I work in a git worktree and tell you to **merge**, do all of these steps in this order:

1. **Commit** the work on the worktree branch.
2. **Rebase** the branch onto `main`.
3. **Fast-forward merge** the branch into `main` (`--ff-only`).
4. **Clean** the repo. Remove the worktree and delete the merged branch.
5. **Push** `main`.
