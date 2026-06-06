# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Delete a cheatsheet by name and regenerate the root index.md (Intent I-3 O-1/O-2).

Deterministic and side-effect-bounded: removes cheatsheets/<name>.md, then rewrites
index.md by reusing register_cheatsheet.py's discover/render logic (single source of
truth for the index format, Constitution P-4). Unknown name → no mutation, non-zero exit.

Run via: uv run scripts/delete_cheatsheet.py <name>
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

_REG = Path(__file__).resolve().parent / "register_cheatsheet.py"


def _load_register():
    """Import register_cheatsheet.py as a sibling module (its main() is __main__-guarded)."""
    spec = importlib.util.spec_from_file_location("register_cheatsheet", _REG)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalize_name(name: str) -> str:
    """Accept a bare slug, a trailing .md, or a leading cheatsheets/ — return the slug."""
    name = name.strip().removeprefix("cheatsheets/").removesuffix(".md")
    return name


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Delete a cheatsheet and regenerate index.md.")
    parser.add_argument("name", help="Cheatsheet name (slug), e.g. http-client-httpx.")
    parser.add_argument("--root", default=".", help="Repo root (default: current directory).")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    slug = normalize_name(args.name)
    target = root / "cheatsheets" / f"{slug}.md"

    if not target.is_file():
        print(f"error: no cheatsheet named '{slug}' ({target.relative_to(root)} not found)", file=sys.stderr)
        return 2

    target.unlink()

    register = _load_register()
    entries = register.discover_cheatsheets(root)
    (root / "index.md").write_text(register.render_index(entries), encoding="utf-8")
    print(f"deleted cheatsheets/{slug}.md; index.md updated: {len(entries)} cheatsheet(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
