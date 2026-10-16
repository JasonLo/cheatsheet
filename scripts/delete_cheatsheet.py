# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Delete a cheatsheet by name and make the root index.md again (Intent I-3 O-1, O-2).

The script is deterministic. It removes cheatsheets/<name>.md. Then it writes index.md
with the discover and render functions of register_cheatsheet.py (Constitution P-4).
As a result, the index format has one source. If the name is unknown, the script changes
nothing and exits with a non-zero code.

Run it with: uv run scripts/delete_cheatsheet.py <name>
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

_REG = Path(__file__).resolve().parent / "register_cheatsheet.py"


def _load_register():
    """Import register_cheatsheet.py from the same folder. Its main() runs only as __main__."""
    spec = importlib.util.spec_from_file_location("register_cheatsheet", _REG)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def normalize_name(name: str) -> str:
    """Return the slug from a name. The name can end in .md or start with cheatsheets/."""
    name = name.strip().removeprefix("cheatsheets/").removesuffix(".md")
    return name


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Delete a cheatsheet and make index.md again.")
    parser.add_argument("name", help="Cheatsheet name (slug), for example http-client-httpx.")
    parser.add_argument("--root", default=".", help="Repo root. The default is the current directory.")
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
