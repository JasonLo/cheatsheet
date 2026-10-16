# Python package release workflow with gh

_Grounded in JasonLo's repos as of 2026-08-31. Current practice is from [cli.github.com/manual/gh_release_create](https://cli.github.com/manual/gh_release_create) and the PyPA packaging guide._

## Reference snippet

```bash
# Atomic release: push the branch and the tag together. Then create the GitHub Release.
git tag v1.2.3
git push --atomic origin main v1.2.3
gh release create v1.2.3 \
  --verify-tag \
  --title "v1.2.3" \
  --generate-notes
```

## Typical usage patterns

- **PEP 723 release script (`uv run scripts/release.py [major|minor|patch]`).** The script first checks for `main`, a clean working tree, and sync with the remote. Then it increases the version, writes the date into the CHANGELOG, commits, tags, runs `git push --atomic`, and runs `gh release create --verify-tag`. (seen in `UW-Madison-DSI/agentic-web-extraction:scripts/release.py`, `JasonLo/uw-s3:scripts/release.py`)
- **Release notes from the CHANGELOG (`--notes-file -`).** The script parses the `## Unreleased` block before any change and sends it to `gh release create --notes-file -` on stdin. The version commit renames `## Unreleased` to `## vX.Y.Z — YYYY-MM-DD` and adds a new empty `## Unreleased`. (seen in `UW-Madison-DSI/agentic-web-extraction:scripts/release.py`)
- **Rollback when the push fails.** If `git push --atomic` fails, the script runs `git tag -d vX.Y.Z` and `git reset --mixed HEAD~1`. After the tag is public, the script does not roll back and prints the manual-fix command. (seen in `UW-Madison-DSI/agentic-web-extraction:scripts/release.py`, `JasonLo/lite-spec:scripts/release.sh`)

## Learnings

- **The branch and the tag are two separate updates** → **A release is one transaction**. With two pushes, the branch can arrive without the tag, and CI can run on a commit with no release. The command `git push --atomic origin <branch> <tag>` sends both refs or neither. (seen in `JasonLo/sound-trim:scripts/release.sh`, which uses two pushes)
- **The release tool uses the tag that you pushed** → **Release creation must check the tag, not create it**. The `gh release create` command creates a missing tag at the tip of the remote default branch, which can be the wrong commit. The `--verify-tag` flag stops the release instead. (seen in `UW-Madison-DSI/agentic-web-extraction:scripts/release.py`)
- **The version is text that you patch** → **The package tool owns the version field**. A regex on `pyproject.toml` can fail on different TOML formats. `uv version --bump <increment>` writes the correct field, and `--short` prints the new version for the next steps. (seen in `JasonLo/uw-s3:scripts/release.py`, not the regex in `UW-Madison-DSI/agentic-web-extraction:scripts/release.py`)

## Agent rules

- ALWAYS use `git push --atomic origin <branch> <tag>` to push the release commit and tag together.
- ALWAYS pass `--verify-tag` to `gh release create` in a scripted or automated release.
- NEVER run `gh release create` before you confirm that the tag exists on the remote.
- ALWAYS check for `main`, a clean tree, and sync with the remote before you change `pyproject.toml` or tag.
- NEVER roll back automatically after the tag push succeeds.
- ALWAYS print the manual-fix command when a release fails after the tag is public.
