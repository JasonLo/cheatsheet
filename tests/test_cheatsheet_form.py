# /// script
# requires-python = ">=3.14"
# dependencies = ["pytest"]
# ///
"""Check the short point form of each cheatsheet (Intent I-1 O-4).

The rules:
- Before the first section, a cheatsheet has only the H1 title and the grounding line.
- The "Reference snippet" section has exactly one fenced code block and no prose.
- The other sections have only bullets.
- A "Typical usage patterns" bullet has an optional bold label and one or two sentences.
- A "Learnings" bullet has a bold old → new head and one or two sentences.
- An "Agent rules" bullet has one sentence.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_prose():
    spec = importlib.util.spec_from_file_location("ste_prose", Path(__file__).parent / "test_ste_prose.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


prose = _load_prose()

_MAX_SENTENCES = {"Typical usage patterns": 2, "Learnings": 2, "Agent rules": 1}
_LEARNING_HEAD = re.compile(r"^\*\*.+?\*\*\s*→\s*\*\*.+?\*\*\.?\s*")
_LABEL = re.compile(r"^\*\*[^*]+\*\*\.?\s+(?=\S)")
_SEEN_IN = re.compile(r"\s*\((seen in|in) [^)]*\)\.?\s*$")


def sentence_count(text: str) -> int:
    return len([s for s in prose._SENTENCE_END.split(text.strip()) if s.strip()])


def problems(text: str) -> list[str]:
    """Return each break of the point-form rules in a cheatsheet text."""
    found = []
    body = re.sub(r"^(`{3,}|~{3,}).*?^\1\s*$", "", text, flags=re.S | re.M)
    section = None
    bullets: dict[str, list[str]] = {}
    for line in body.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if not line.strip() or line.startswith("# "):
            continue
        if section is None:
            if not (line.startswith("_Grounded in ") and line.rstrip().endswith("._")):
                found.append(f"text before the first section: {line[:60]}")
        elif section == "Reference snippet":
            found.append(f"prose in Reference snippet: {line[:60]}")
        elif line.startswith("- "):
            bullets.setdefault(section, []).append(line[2:])
        elif line.startswith("  ") and bullets.get(section):
            bullets[section][-1] += " " + line.strip()
        else:
            found.append(f"text that is not a bullet in {section}: {line[:60]}")
    snippet = re.search(r"^## Reference snippet\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M)
    blocks = len(re.findall(r"^(`{3,}|~{3,})\S", snippet.group(1), flags=re.M)) if snippet else 0
    if blocks != 1:
        found.append(f"Reference snippet has {blocks} code blocks, not 1")
    for name, limit in _MAX_SENTENCES.items():
        for bullet in bullets.get(name, []):
            text = prose._strip(bullet)
            text = _SEEN_IN.sub("", text)
            if name == "Learnings":
                text, n = _LEARNING_HEAD.subn("", text)
                if not n:
                    found.append(f"Learning without a bold old → new head: {bullet[:60]}")
            elif name == "Typical usage patterns":
                text = _LABEL.sub("", text)
            if sentence_count(text) > limit:
                found.append(f"{name} bullet with more than {limit} sentence(s): {bullet[:60]}")
    return found


def test_problems_finds_long_bullet_and_paragraph():
    text = (
        "# T\n\n_Grounded in x's repos as of d. Current practice is from y._\n\n"
        "## Reference snippet\n\n```py\nx = 1\n```\n\n```sh\nrun\n```\n\n"
        "## Learnings\n\n- **A** → **B.** One. Two. Three.\n\n"
        "## Agent rules\n\n- ALWAYS do X.\n"
    )
    assert len(problems(text)) == 2  # two code blocks, and a Learning with three sentences


def test_cheatsheet_point_form():
    report = [
        f"{sheet.name}: {problem}"
        for sheet in sorted((REPO_ROOT / "cheatsheets").glob("*.md"))
        for problem in problems(sheet.read_text())
    ]
    assert report == []


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__]))
