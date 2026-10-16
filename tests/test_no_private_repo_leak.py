# /// script
# requires-python = ">=3.14"
# dependencies = ["pytest"]
# ///
"""Check that cheatsheets cite no private repository (Constitution P-7).

The test finds each `<login>/<repo>` reference and each `owner/repo:path` citation in cheatsheets/*.md.
It uses the gh CLI to read the visibility of each repository (Constitution P-5).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _gh(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["gh", *args], capture_output=True, text=True, timeout=30)


def owner_repo_slugs(text: str, login: str) -> set[str]:
    """Return each `<login>/<repo>` slug in the text, with the repo name in its original letter case."""
    pattern = rf"(?<![\w.-]){re.escape(login)}/([A-Za-z0-9._-]*[A-Za-z0-9_-])"
    return {f"{login}/{name}" for name in re.findall(pattern, text, flags=re.I)}


def cited_slugs(text: str) -> set[str]:
    """Return the `owner/repo` part of each `owner/repo:path` citation in backticks."""
    return set(re.findall(r"`([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+):[^`]*`", text))


def test_cited_slugs_finds_any_owner():
    assert cited_slugs("(seen in `Org/tool:src/a.py`) and `a/b` only") == {"Org/tool"}


def test_owner_repo_slugs_finds_cites():
    text = "See `JasonLo/uw-s3:src/a.py` and jasonlo/undock. Not xjasonlo/other."
    assert owner_repo_slugs(text, "JasonLo") == {"JasonLo/uw-s3", "JasonLo/undock"}


def malformed_cites(text: str, login: str) -> list[str]:
    """Return each `<login>/<repo>/<path>` cite that has no colon between the repo and the path."""
    return re.findall(rf"`({re.escape(login)}/[A-Za-z0-9._-]+/[^`:\s]+)`", text, flags=re.I)


def test_malformed_cites_are_found():
    text = "(seen in `JasonLo/cairn/src/app.py`) and (seen in `JasonLo/uw-s3:src/a.py`)"
    assert malformed_cites(text, "JasonLo") == ["JasonLo/cairn/src/app.py"]


def test_cites_use_repo_colon_path():
    login = _gh("api", "user", "--jq", ".login").stdout.strip() or "JasonLo"
    found = {
        sheet.name: bad
        for sheet in sorted((REPO_ROOT / "cheatsheets").glob("*.md"))
        if (bad := malformed_cites(sheet.read_text(), login))
    }
    assert found == {}


def test_cited_repos_are_public():
    login = _gh("api", "user", "--jq", ".login").stdout.strip()
    assert login, "gh is not authenticated"
    slugs = set()
    for sheet in (REPO_ROOT / "cheatsheets").glob("*.md"):
        text = sheet.read_text()
        slugs |= owner_repo_slugs(text, login) | cited_slugs(text)
    not_public = {}
    for slug in sorted(slugs):
        result = _gh("repo", "view", slug, "--json", "visibility", "--jq", ".visibility")
        if result.returncode == 0 and result.stdout.strip() != "PUBLIC":
            not_public[slug] = result.stdout.strip()
    assert not_public == {}


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__]))
