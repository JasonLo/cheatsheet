import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "register_cheatsheet.py"


def _load():
    spec = importlib.util.spec_from_file_location("register_cheatsheet", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


reg = _load()


def test_extract_title_reads_first_h1(tmp_path):
    f = tmp_path / "axios.md"
    f.write_text("# Data fetching with axios\n\nbody\n")
    assert reg.extract_title(f) == "Data fetching with axios"


def test_extract_title_falls_back_to_stem(tmp_path):
    f = tmp_path / "redis_caching.md"
    f.write_text("no heading here\n")
    assert reg.extract_title(f) == "redis_caching"


def test_discover_cheatsheets_sorted_with_relpaths(tmp_path):
    cdir = tmp_path / "cheatsheets"
    cdir.mkdir()
    (cdir / "b.md").write_text("# Beta\n")
    (cdir / "a.md").write_text("# Alpha\n")
    (cdir / "notes.txt").write_text("ignored\n")
    entries = reg.discover_cheatsheets(tmp_path)
    assert entries == [("cheatsheets/a.md", "Alpha"), ("cheatsheets/b.md", "Beta")]


def test_render_index_lists_entries():
    out = reg.render_index([("cheatsheets/a.md", "Alpha"), ("cheatsheets/b.md", "Beta")])
    assert out.startswith("# Cheatsheets\n")
    assert "- [Alpha](cheatsheets/a.md)" in out
    assert "- [Beta](cheatsheets/b.md)" in out
    assert out.endswith("\n")


def test_render_index_empty_has_placeholder():
    out = reg.render_index([])
    assert "_No cheatsheets yet._" in out


def test_main_writes_index(tmp_path):
    cdir = tmp_path / "cheatsheets"
    cdir.mkdir()
    (cdir / "axios.md").write_text("# Data fetching with axios\n")
    reg.main(["--root", str(tmp_path)])
    index = (tmp_path / "index.md").read_text()
    assert "- [Data fetching with axios](cheatsheets/axios.md)" in index
