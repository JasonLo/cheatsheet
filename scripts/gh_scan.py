# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Run the gh CLI with the read-only scan token (Constitution P-5, Intents I-2 and I-3).

The workflows read other repositories only with GH_SCAN_TOKEN. They write only with the default token.
An agent cannot run "GH_TOKEN=$GH_SCAN_TOKEN gh ...", because its tool rules do not allow "$" in a command.
This script gives the scan token to gh, so the command has no "$".

Run it with: uv run scripts/gh_scan.py <gh arguments>
"""
from __future__ import annotations

import os
import sys


def scan_env(environ: dict[str, str]) -> dict[str, str]:
    """Return a copy of the environment with GH_TOKEN set to the scan token."""
    token = environ.get("GH_SCAN_TOKEN", "")
    if not token:
        raise SystemExit("error: GH_SCAN_TOKEN is empty. Set the read-only scan token first.")
    return {**environ, "GH_TOKEN": token}


def main(argv: list[str]) -> None:
    os.execvpe("gh", ["gh", *argv], scan_env(dict(os.environ)))


if __name__ == "__main__":
    main(sys.argv[1:])
