# /// script
# requires-python = ">=3.14"
# dependencies = ["pytest"]
# ///
"""Check that each workflow agent can run its cross-repo reads (Intents I-2 O-3 and I-3 O-6).

An agent tool rule does not allow "$" in a command, so "GH_TOKEN=$GH_SCAN_TOKEN gh ..." is always denied.
Each workflow must read other repos through `uv run scripts/gh_scan.py`, allow that command, and install uv.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = sorted((REPO_ROOT / ".github" / "workflows").glob("cheatsheet-*.yml"))
_ALLOWED_TOOLS = re.compile(r'--allowedTools "([^"]*)"')


def test_all_workflows_found():
    assert len(WORKFLOWS) == 5


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda p: p.stem)
def test_cross_repo_reads_use_gh_scan(workflow):
    text = workflow.read_text()
    assert "GH_TOKEN=$" not in text
    assert "uv run scripts/gh_scan.py" in text
    tools = _ALLOWED_TOOLS.search(text).group(1).split(",")
    assert "Bash(uv run scripts/gh_scan.py:*)" in tools or "Bash(uv run:*)" in tools
    assert "astral-sh/setup-uv@" in text


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
