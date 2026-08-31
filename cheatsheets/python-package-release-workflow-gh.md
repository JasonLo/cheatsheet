# Python package release workflow with gh

_Grounded in JasonLo's repos as of 2026-08-31; current practice per [cli.github.com/manual/gh_release_create](https://cli.github.com/manual/gh_release_create) and PyPA packaging guide._

## Reference snippet

```bash
# Atomic release: push branch + tag together, then create the GitHub Release
git tag v1.2.3
git push --atomic origin main v1.2.3
gh release create v1.2.3 \
  --verify-tag \
  --title "v1.2.3" \
  --generate-notes
```

## Typical usage patterns

- **PEP 723 release script (`uv run scripts/release.py [major|minor|patch]`)**: pre-flight guards (on `main`, clean working tree, synced with remote) → version bump → CHANGELOG stamp → `git commit` + `git tag` → `git push --atomic` → `gh release create --verify-tag`. Self-contained (`uv` installs deps from `# /// script` header on demand). Used in `UW-Madison-DSI/agentic-web-extraction:scripts/release.py` and `JasonLo/uw-s3:scripts/release.py`.
- **CHANGELOG-driven release notes (`--notes-file -`)**: parse the `## Unreleased` block before any mutation, pipe it to `gh release create --notes-file -` via stdin. The same commit that bumps the version stamps `## Unreleased` → `## vX.Y.Z — YYYY-MM-DD` and re-opens a fresh `## Unreleased` so the next author has a landing zone. Seen in `UW-Madison-DSI/agentic-web-extraction:scripts/release.py`.
- **Rollback-on-push-failure guard**: if `git push --atomic` fails, immediately `git tag -d vX.Y.Z` + `git reset --mixed HEAD~1`. Once the tag is public (push succeeded), skip the rollback and only print the manual-fix command — no automated undo after remote state exists. Pattern from `UW-Madison-DSI/agentic-web-extraction:scripts/release.py` and `JasonLo/lite-spec:scripts/release.sh`.

## Learnings

- **Two separate pushes (`git push origin main && git push origin --tags`) leave a race window** → **`git push --atomic origin <branch> <tag>` is the standard**. If the branch push succeeds but the tag push fails, CI can trigger on a commit with no matching release; atomic ensures both refs land together or neither does. (seen in `JasonLo/sound-trim:scripts/release.sh` using the older two-step pattern)
- **`gh release create` silently auto-creates the tag if it does not exist on the remote** → **always add `--verify-tag` in automated pipelines**. Without it, a failed `git push --atomic` followed by `gh release create` stamps a release at whatever the remote default branch tip happens to be — a phantom tag at the wrong commit. `--verify-tag` turns this into a hard abort instead of a silent misrelease. (pattern from `UW-Madison-DSI/agentic-web-extraction:scripts/release.py`)
- **Regex-patching `pyproject.toml` to bump the version** → **`uv version --bump <increment>` delegates the write to `uv`**. Manual regex is fragile across TOML formatting variants and Python versions; `uv version` reads and writes the canonical field reliably and prints the new version with `--short` for downstream use. (seen in `JasonLo/uw-s3:scripts/release.py` vs. the regex approach in `UW-Madison-DSI/agentic-web-extraction:scripts/release.py`)

## Agent rules

- ALWAYS use `git push --atomic origin <branch> <tag>` to push the release commit and tag in one transaction.
- ALWAYS pass `--verify-tag` to `gh release create` in any scripted or automated release pipeline.
- NEVER run `gh release create` before confirming the tag exists on the remote.
- ALWAYS run pre-flight guards (on `main`, clean working tree, synced with remote) before mutating `pyproject.toml` or creating a tag.
- NEVER attempt automated rollback once a tag is confirmed pushed — print the manual-fix command instead.
