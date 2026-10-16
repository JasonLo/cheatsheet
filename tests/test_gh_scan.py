# /// script
# requires-python = ">=3.14"
# dependencies = ["pytest"]
# ///
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "gh_scan.py"


def _run(tmp_path, scan_token):
    fake_gh = tmp_path / "gh"
    fake_gh.write_text('#!/bin/sh\necho "token=$GH_TOKEN args=$*"\n')
    fake_gh.chmod(0o755)
    env = {**os.environ, "PATH": f"{tmp_path}{os.pathsep}{os.environ['PATH']}", "GH_TOKEN": "default"}
    env["GH_SCAN_TOKEN"] = scan_token
    return subprocess.run(
        [sys.executable, str(SCRIPT), "search", "code", "--owner", "me"],
        capture_output=True, text=True, env=env,
    )


def test_gh_runs_with_scan_token(tmp_path):
    result = _run(tmp_path, "scan-secret")
    assert result.returncode == 0
    assert result.stdout.strip() == "token=scan-secret args=search code --owner me"


def test_empty_scan_token_stops(tmp_path):
    result = _run(tmp_path, "")
    assert result.returncode != 0
    assert "GH_SCAN_TOKEN is empty" in result.stderr


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
