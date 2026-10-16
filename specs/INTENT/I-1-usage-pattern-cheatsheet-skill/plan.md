# Implementation Plan — I-1 Outcome O-6: "Agent rules" section

> This file is an agent-writable working doc that an agent can generate again. The source of truth is `intent.md`. If the two files do not agree, the intent is correct. The `/spec-intent` planning handoff generated this plan again. It did this after the 2026-06-05 refine that added O-6. O-6 adds an "Agent rules" section that AI agents can use easily.

**Intent:** `specs/INTENT/I-1-usage-pattern-cheatsheet-skill/intent.md`
**New outcome (O-6):** WHEN writing the cheatsheet THE SYSTEM SHALL include an "Agent rules" section.
This section states each mandatory rule as an imperative ALWAYS/NEVER directive in point form.
Then a coding agent, for example Claude Code, can apply the corrections directly and not read the prose again.
**Current verdict:** fail (6/7). The mandatory template in SKILL.md does not emit this section. The one generated cheatsheet also does not emit it.
**Target verdict:** pass (7/7), status `complete`.

## Design summary

An edit to the skill template and an update to the existing cheatsheet satisfy O-6. The change adds no new code, no new dependencies, and no machine-readable artifact.
This follows Constitution P-3 (simplest solution) and P-6 (skills handle judgment).
The "Agent rules" section is a separate, imperative ALWAYS/NEVER view of the same findings that the Learnings section gives to humans.
The two sections are intentionally separate, at two different levels:

- **Learnings** — This section gives a human reader the conceptual change from the old mental model to the new one (O-5).
- **Agent rules** — This section gives short imperative directives that a coding agent applies directly without the prose (O-6).

Placement: put the section directly **after** Learnings. The rules come from the Learnings and from Typical usage patterns.
This order keeps the derivation easy to read: first the concept, then the short directive.

The intent gives these non-goals. Do NOT do these:
- Do not add YAML frontmatter, tags, or machine-parseable metadata. Plain markdown does not need them, and Claude Code does not use them.
- Do not add a separate machine file for each topic. The rules stay inside the single self-contained cheatsheet.
- Do not connect the rules automatically into the CLAUDE.md or `@`-imports of a consumer repo.

## Phase 1 — Add "Agent rules" to the SKILL.md template and authoring steps

**File touched:** `.claude/skills/cheatsheet/SKILL.md`

1. **Extend the fenced template (lines ~59-91).** Find the end of the `## Learnings` block (near line 90). After it, add a new `## Agent rules` block inside the same fenced ` ````markdown ` example. Suggested template body:

   ```
   ## Agent rules

   Imperative, point-form guardrails a coding agent applies directly —
   each distilled from a Learning/pattern above. Every bullet starts with
   ALWAYS or NEVER and is directly actionable (no "why", no old→new framing;
   that lives in Learnings):

   - ALWAYS <do the current-practice action>.
   - NEVER <do the obsolete/anti-pattern action>.
   ```

2. **Add an authoring instruction step** near the current steps 5-6. Give new numbers to the last steps 7-8. Alternatively, insert the step as "6b" to change fewer numbers. Content of the new step:
   - Title: *Author the Agent rules section (O-6).*
   - Make each rule from the findings in Learnings and Typical usage. Write it again as an imperative ALWAYS or NEVER directive in point form.
   - Write at least one rule for each important safety rule. Put one directive in each bullet.
   - The section is for direct use by an agent. Do not add conceptual prose, lists of signatures, frontmatter, or tags. Cite the non-goal so that future edits do not change this.
   - Keep the section inside the single cheatsheet file. Do not make a separate artifact.

3. **Do not change step 7 (Register).** Keep the registration step and the `## Constraints` block as they are.

**Acceptance for Phase 1:** The SKILL.md template has an `## Agent rules` heading inside the fenced structure. The workflow has a separate step that tells the agent to write imperative ALWAYS/NEVER rules in point form.

## Phase 2 — Update the existing cheatsheet

**File touched:** `cheatsheets/self-contained-scripts-uv.md`

Add an `## Agent rules` section after the current `## Learnings` block, after line 39. Change the four Learnings and the patterns into imperative directives. Draft content:

```
## Agent rules

- ALWAYS decide tool-vs-glue before choosing the run style: portable tool → `# /// script` + `uv run script.py`; project glue → `uv run python script.py`.
- NEVER insert `python` into `uv run script.py` for a self-contained tool script — it opts out of PEP-723 isolation and uses the project env.
- ALWAYS manage inline deps with `uv add --script` / `uv lock --script`.
- NEVER hand-edit the `# /// script` dependency list — let uv own the metadata.
- ALWAYS strip `VIRTUAL_ENV` before a `uv run` script shells out to child `uv` commands (the inherited value points at the isolated cache env).
- ALWAYS run `uv lock --script` when a self-contained tool needs reproducibility — portability and pinning are independent axes.
```

**Acceptance for Phase 2:** The cheatsheet has an `## Agent rules` heading with ≥1 bullet. Each bullet starts with ALWAYS or NEVER in imperative form.
The section is in point form, with bullets only and no paragraphs. Each directive comes from a Learning or pattern that is already in the file.

## Phase 3 — Register the index again

**File potentially touched:** `index.md`

- The H1 of the cheatsheet (`# Self-contained scripts with uv`) does not change. The change adds or removes no file.
  `scripts/register_cheatsheet.py` builds the index only from the `cheatsheets/*.md` filenames and the first H1. For this reason, the rendered `index.md` stays byte-identical.
- Run `uv run scripts/register_cheatsheet.py` in all cases. It is fast and idempotent, and it follows the "register after writing" habit. Expect no diff to `index.md`.

**Acceptance for Phase 3:** `git diff index.md` is empty after the script runs.

## Phase 4 — Improve the Success criteria of the O-6 agent check (recommended)

**File touched (by the user, recommended):** `specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/agent-actionable-rules.md`

The `## Success criteria` of the check is still the placeholder. As a result, `/spec-check` grades O-6 loosely.
We recommend that the user replaces it with concrete pass conditions, so that O-6 gets a precise grade. Suggested criteria:
- Examine each `cheatsheets/*.md` and the template in `.claude/skills/cheatsheet/SKILL.md`.
- Each generated cheatsheet must meet these conditions to pass. An `## Agent rules` heading is present. The section has ≥1 bullet.
  Each bullet is imperative and starts with `ALWAYS` or `NEVER`. The section uses bullets, not prose paragraphs. No YAML or tag metadata carries the rules.
- Template pass: the mandatory structure in SKILL.md has the `## Agent rules` heading. It also has an authoring step that describes the imperative ALWAYS/NEVER derivation.
- Cite this evidence: `cheatsheets/self-contained-scripts-uv.md:<line of "## Agent rules">` and `.claude/skills/cheatsheet/SKILL.md:<line of "## Agent rules">`.

This phase is advisory because it only makes the grade stricter. O-6 can change to pass with only the seeded SHALL.
But precise criteria prevent regressions and false passes. Note: the user owns the bodies of agent-prompt files.
`/spec-intent` only writes their first version, so the user makes this change.

## Verification / Acceptance

1. **Spec-check.** Run `/spec-check --intent I-1`. Expect O-6 to change from fail to **pass**. Expect the intent verdict to return to **complete (7/7)**.
   The values are `verdict_outcomes_passed: 7` of `verdict_outcomes_total: 7` and `status: complete`. `spec-check` also sets `closed` again.
2. **Template check.** Make sure that `## Agent rules` is inside the fenced template. Make sure that a related authoring step is in `.claude/skills/cheatsheet/SKILL.md`.
3. **Content check.** Make sure that `cheatsheets/self-contained-scripts-uv.md` has an `## Agent rules` section that meets the Phase 2 acceptance bullets.
4. **Index no-op.** Make sure that `git diff index.md` is empty after `uv run scripts/register_cheatsheet.py`.
5. **Constitution sanity.** The change adds no new files, dependencies, modules, or build steps (P-1/P-2/P-3). It does not change GitHub access (P-5).
   Judgment stays in the skill, not in code (P-6).

## Sequencing & dependencies

- Phase 1 and Phase 2 are independent edits. You can do them in either order. Do both before verification.
- Phase 3 runs after Phase 2 because it reads the cheatsheet. It is a no-op in both cases.
- Do Phase 4 (the improvement of the check) **before** the final `/spec-check`. Then `/spec-check` grades O-6 against the precise criteria.
- Risk note: keep Agent rules clearly different from Learnings. A reviewer or check can see old→new conceptual framing in the Agent rules section.
  Then it can think that the section duplicates the Learnings. Keep the rules only imperative and actionable.

## Critical files
- `.claude/skills/cheatsheet/SKILL.md`
- `cheatsheets/self-contained-scripts-uv.md`
- `specs/INTENT/I-1-usage-pattern-cheatsheet-skill/checks/agent-actionable-rules.md`
- `specs/INTENT/I-1-usage-pattern-cheatsheet-skill/intent.md`
- `scripts/register_cheatsheet.py`
