import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "delete_cheatsheet.py"


def _load():
    spec = importlib.util.spec_from_file_location("delete_cheatsheet", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


dele = _load()


def test_delete_removes_file_and_reindexes(tmp_path):
    cdir = tmp_path / "cheatsheets"
    cdir.mkdir()
    (cdir / "a.md").write_text("# Alpha\n")
    (cdir / "b.md").write_text("# Beta\n")

    rc = dele.main(["--root", str(tmp_path), "a"])

    assert rc == 0
    assert not (cdir / "a.md").exists()
    assert (cdir / "b.md").exists()
    index = (tmp_path / "index.md").read_text()
    assert "- [Beta](cheatsheets/b.md)" in index
    assert "Alpha" not in index
    assert "cheatsheets/a.md" not in index


def test_unknown_name_errors_and_leaves_repo_unchanged(tmp_path, capsys):
    cdir = tmp_path / "cheatsheets"
    cdir.mkdir()
    (cdir / "a.md").write_text("# Alpha\n")
    index_path = tmp_path / "index.md"
    index_path.write_text("# Cheatsheets\n\n- [Alpha](cheatsheets/a.md)\n")

    before_listing = sorted(p.name for p in cdir.iterdir())
    before_index = index_path.read_text()

    rc = dele.main(["--root", str(tmp_path), "does-not-exist"])

    assert rc != 0
    assert sorted(p.name for p in cdir.iterdir()) == before_listing
    assert index_path.read_text() == before_index
    err = capsys.readouterr().err
    assert "does-not-exist" in err
