---
name: cheatsheet
description: Make a personal cheatsheet from a use case and a named target. The skill mines the user's OWN GitHub repos with gh to find how they use the target. It compares this usage with the current official docs (context7 and web). It writes a cheatsheet in Simplified Technical English. The Learnings section corrects old patterns at the level of concepts. Triggers on "make a cheatsheet", "cheatsheet for X", "/cheatsheet", "how do I use X in my repos".
---

# cheatsheet

Make a cheatsheet for a **use case** and a named **target**. A target is a
library, a tool, a repo, or a path. The cheatsheet shows how the user uses the
target today. It also corrects the usage that is not current. The cheatsheet is
about concepts and intent. One small reference snippet shows the current form of
the code. The prose stays at the level of concepts and does not list syntax changes.

## Inputs

- **Use case** (free text). Examples are "data fetching" and "config loading".
- **`--target`** (required). This is the library, tool, repo, or path for the
  cheatsheet. Examples are `httpx`, `pydantic`, `owner/repo`, and `src/db/`.

If `--target` is missing, ask for it one time before you continue.

## Workflow

1. **Get the GitHub identity.** Run `gh api user --jq .login` to get the login
   of the authenticated user (for example, `jasonlo`). Use only the `gh` CLI
   for GitHub access in this skill. Do not use a direct API call or an SDK
   (Constitution P-5).

2. **Collect the usage from the user's repos.** Search the user's code for the
   target. Keep the files that are most related to the use case.
   - Search the code:
     `gh search code --owner <login> "<target>" --limit 50 --json repository,path`
   - If necessary, list the repos first:
     `gh repo list <login> --limit 200 --json name,pushedAt`
   - Get the raw content of each candidate file:
     `gh api repos/<login>/<repo>/contents/<path> -H "Accept: application/vnd.github.raw"`
   - Keep the small set of files that best show the user's usual patterns,
     imports, and conventions for the use case.
   - **Record the visibility of each repo (Constitution P-7).** Get it one time
     for each repo:
     `gh repo view <login>/<repo> --json visibility -q .visibility`.
     The value is `PUBLIC` or a different value. Record the visibility with each
     file path.
   - Write down the file paths. You can cite **public** sources in the
     cheatsheet. **Never** write the name, slug, URL, or text of a **private**
     repo.

3. **Find the current best practice.** Get the current official documentation
   for the target from context7. Use `resolve-library-id`, then use `query-docs`
   for the use case. If context7 has no entry for the target, use WebSearch and
   WebFetch. Read the official docs, the changelog, or the migration guide. Use
   the most recent stable guidance.

4. **Mark each pattern as current or not current.** Compare each usage from the
   user's repos with the current guidance. Mark it as current or as replaced.
   For each replaced usage, find the change in the mental model. Do not record
   only the new function name.

5. **Write the cheatsheet** to `cheatsheets/<slug>.md`. The `<slug>` is the use
   case and the target, in lowercase, with hyphens between the words.

   **Write all prose in ASD-STE100 Simplified Technical English (O-10, P-8).**
   Code, commands, identifiers, file paths, URLs, and quoted tool output are
   exempt. Obey these rules:
   - Write a maximum of 25 words in a descriptive sentence. Write a maximum of
     20 words in an instruction.
   - Write one instruction in each sentence. Use the imperative for instructions.
   - Use the active voice. Use simple tenses.
   - Use approved STE words, technical names, and technical verbs. Do not use
     idioms or figurative words.
   - Do not leave out articles or verbs to make a sentence shorter.
   - Do not use semicolons, contractions, or "e.g.". Write "for example".
   - Do not make noun clusters of more than three words.

   **Write each section in short point form (O-4).** Use short bullets, not
   paragraphs. Each bullet has one or two short sentences. A usage bullet can
   start with a bold label. A Learning starts with its bold old → new head. An
   Agent rule has one sentence. Keep a detail only if it is an important tip for
   future use or if it carries the concept. Remove history, version timelines,
   benchmarks, prices, and repeated points. Write one idea in each bullet. Do not
   write prose between the title and the first section, or in the Reference
   snippet section. Put a note for the snippet in a code comment.

   Use this structure exactly:

   ````markdown
   # <Use case> with <target>

   _Grounded in <login>'s repos as of <today>. Current practice is from <doc source>._

   ## Reference snippet

   ```<lang>
   # One minimal block that shows the current usage of <target>.
   # Take it from the current docs of step 3.
   # Do NOT copy it from the user's repo code, because that code can be old.
   ```

   This block shows the correct usage today. Take it from the docs of step 3,
   not from the files that you mined. Write one block that shows the form of the
   code. Do not write a list of API calls. The rule against syntax lists applies
   to the prose, not to this block.

   ## Typical usage patterns

   - Write one bullet for each pattern of how you use <target> today. Give the
     pattern and the time when you use it. Cite a real file (`owner/repo:path`)
     **only when the source repo is public**. For a private source, do not
     write a cite. Describe the pattern in a general form (P-7).
     Do not write the private repo name, slug, URL, or code.
     Write one line for each bullet if possible. Write concepts, not syntax.
     **Write only the 3 patterns with the highest value (O-5).** Add a fourth
     bullet only for a strong reason. An example is a different, important
     pattern that the top 3 do not cover. Never add a bullet only to fill space.

   ## Learnings

   Each bullet names an old pattern or an error from your code and its
   replacement. Write it at the level of intent and mental model, not API
   signatures. Write one or two short sentences.
   **Write only the 3 learnings with the highest value (O-5).** Add a fourth
   learning only for a strong reason. An example is a different error that the
   other learnings do not cover.

   - **<Old mental model>** → **<New mental model>.** Give the reason, and say
     what now expresses the same intent. (seen in `owner/repo:path`. Use only
     public sources. For private sources, do not write this part, per P-7.)

   ## Agent rules

   Write rules that a coding agent (for example, Claude Code) can apply
   directly. Take each rule from a Learning or a pattern above. Start each
   bullet with ALWAYS or NEVER. Give one directive in each bullet. Do not give
   a reason. Do not use the old → new form, because that form is for Learnings.

   - ALWAYS <do the current-practice action>.
   - NEVER <do the old action>.
   ````

6. **Write the Learnings section at the level of concepts (O-6).** Each entry
   must give a reason. The reason is the change in intent or in the mental
   model. Do not write a change that is only syntax (for example, "`x()` is now
   `y()`"). You can write it only together with the reason for the change in
   concept. Do not write a change that is only cosmetic syntax.

7. **Write the Agent rules section (O-7).** Write the same findings as
   directives that a coding agent can apply without the prose. Start each
   bullet with **ALWAYS** or **NEVER**. Write one directive in each bullet, in
   point form. Write at least one rule for each important safety rule. Take the
   rules from the Learnings and the usage patterns. Do not write the old → new
   form, lists of signatures, YAML frontmatter, or tags. Keep the rules in this
   cheatsheet file. Never make a separate file for them.

8. **Register the cheatsheet.** Run `uv run scripts/register_cheatsheet.py` to
   update the root `index.md` (Constitution P-4). Do not edit `index.md`
   manually.

9. **Check the cheatsheet.** Run
   `uv run tests/test_ste_prose.py`,
   `uv run tests/test_cheatsheet_form.py`, and
   `uv run tests/test_no_private_repo_leak.py`.
   If a test fails, correct the cheatsheet and run the test again.

10. **Report** the path of the file, the files that you mined, the source of
    the docs, and the number of learnings.

## Constraints

- Use only the `gh` CLI for GitHub access (P-5).
- Write each deterministic helper as a self-contained `uv` script with PEP 723
  metadata (P-1, P-2). This skill runs only `scripts/register_cheatsheet.py`
  and the tests in `tests/`.
- Use the most simple method that makes a useful cheatsheet (P-3).
- **Never show a private repo (P-7).** The cheatsheet MUST NOT contain the name,
  the owner/repo slug, or the URL of a private repository. It MUST NOT quote or
  copy the code or text of a private repository. Give the patterns from private
  repos only in a general form. Cite only public sources word for word.
- Write all prose in ASD-STE100 Simplified Technical English (P-8).
