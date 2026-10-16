# /// script
# requires-python = ">=3.14"
# dependencies = ["pytest"]
# ///
"""Check the measurable ASD-STE100 rule for repository prose (Constitution P-8).

Each sentence must have 25 words or fewer. Code, URLs, and test citations are exempt.
An agent check covers the rules that a script cannot measure, for example the approved words.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_WORDS = 25

# Append-only history sections. Text in these sections stays as its author wrote it.
_FROZEN_SECTIONS = ("## Change Log", "## Amendments")
_NEW_UNIT = re.compile(r"^(\s*([-*+]|\d+\.)\s|#|\|)")
_SENTENCE_END = re.compile(r"(?<=[.!?])[*_)\"'”]*\s+(?=[A-Z0-9\"*`(_\[])")
# Words that STE does not approve, with the approved replacement in the comment.
_NOT_APPROVED = re.compile(
    r"\b(once|deliberately?|via|ensure|utili[sz]e|leverage|however|thus|hence|on purpose|sufficient|redundant|"
    r"opaque|omit|scarce|approximately|explicit(ly)?|per|acquires?|forbids?|spans?|integrates?|derived?|"
    r"derives|tie[sd]?|stays? in effect|for a reason|with care|recalibrate|defers?|live TTY)\b|\be\.g\.|\bi\.e\.|\betc\.",
    re.I,
)  # for example: once -> one time, via -> with, ensure -> make sure, sufficient -> enough, omit -> leave out, per -> for each
_WORD = re.compile(r"[A-Za-z0-9][\w'’/-]*")


def _strip(text: str) -> str:
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"^[ \t]*(`{3,}|~{3,}).*?^[ \t]*\1\s*$", "", text, flags=re.S | re.M)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"~~.*?~~", "", text)  # Superseded text is history and stays as it was.
    text = re.sub(r"\[test: [^\]]*\]", "", text)
    text = re.sub(r"`[^`\n]*`", "Code", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"https?://\S+", "url", text)


def prose_units(text: str) -> list[str]:
    """Return the prose units (paragraphs, list items, headings, table cells) of a Markdown text."""
    units: list[str] = []
    current: list[str] = []
    frozen = False
    for line in _strip(text).splitlines():
        if line.startswith("## "):
            frozen = line.strip() in _FROZEN_SECTIONS
        if frozen:
            continue
        if not line.strip() or _NEW_UNIT.match(line):
            if current:
                units.append(" ".join(current))
            current = []
            if line.lstrip().startswith("|"):
                units.extend(cell for cell in line.split("|") if cell.strip())
                continue
            if line.startswith("#"):
                units.append(line)
                continue
        if line.strip():
            current.append(line.strip())
    if current:
        units.append(" ".join(current))
    return units


def long_sentences(text: str) -> list[tuple[int, str]]:
    """Return each sentence with more than MAX_WORDS words, with its word count."""
    found = []
    for unit in prose_units(text):
        for sentence in _SENTENCE_END.split(unit):
            count = len(_WORD.findall(sentence))
            if count > MAX_WORDS:
                found.append((count, sentence))
    return found


def not_approved_words(text: str) -> list[str]:
    """Return each word in the prose that STE does not approve."""
    found = []
    for unit in prose_units(text):
        for m in _NOT_APPROVED.finditer(unit):
            # A word in quotes is a mention of the word, for example in a rule that bans it.
            if unit[m.start() - 1 : m.start()] != '"':
                found.append(m.group(0))
    return found


def _report(paths: list[Path]) -> list[str]:
    return [
        f"{p.relative_to(REPO_ROOT)}: {n} words: {s[:90]}"
        for p in paths
        for n, s in long_sentences(p.read_text())
    ]


def test_long_sentence_is_found():
    text = "- " + " ".join(["word"] * 26) + ".\n- Short sentence.\n"
    assert [n for n, _ in long_sentences(text)] == [26]


def test_bold_period_and_code_start_split_sentences():
    long_half = " ".join(["word"] * 15)
    text = f"- **Old {long_half}** → **New.** Why {long_half}. `x` {long_half}.\n"
    assert long_sentences(text) == []


def test_code_and_history_are_exempt():
    long_code = " ".join(["x"] * 40)
    text = f"Intro.\n\n```py\n{long_code}\n```\n\n## Change Log\n- {long_code}.\n"
    assert long_sentences(text) == []


def test_not_approved_word_is_found():
    assert not_approved_words('Run it once. Use `once` in code. Do not use "e.g.".\n') == ["once"]


def test_cheatsheet_approved_words():
    found = {
        p.name: words
        for p in sorted((REPO_ROOT / "cheatsheets").glob("*.md"))
        if (words := not_approved_words(p.read_text()))
    }
    assert found == {}


def test_cheatsheet_sentence_length():
    assert _report(sorted((REPO_ROOT / "cheatsheets").glob("*.md"))) == []


def _repo_prose_paths() -> list[Path]:
    paths = [REPO_ROOT / name for name in ("README.md", "CLAUDE.md", "index.md")]
    paths += sorted((REPO_ROOT / ".claude" / "skills").rglob("SKILL.md"))
    return paths + sorted((REPO_ROOT / "specs").rglob("*.md"))


def test_repo_prose_approved_words():
    found = {
        str(p.relative_to(REPO_ROOT)): words
        for p in _repo_prose_paths()
        if (words := not_approved_words(p.read_text()))
    }
    assert found == {}


def test_repo_prose_sentence_length():
    assert _report(_repo_prose_paths()) == []


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__]))
