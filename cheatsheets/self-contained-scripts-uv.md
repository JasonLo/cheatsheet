# Self-contained scripts with uv

_Grounded in JasonLo's repos as of 2026-06-05; current practice per uv official docs (context7 `/astral-sh/uv`)._

## Reference snippet

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["typer", "rich"]
# ///
import typer

app = typer.Typer()


@app.command()
def main(name: str) -> None:
    print(f"hello {name}")


if __name__ == "__main__":
    app()
# run anywhere: `uv run scripts/foo.py world` — no venv, no pip install
# manage deps: `uv add --script scripts/foo.py rich`; pin: `uv lock --script scripts/foo.py`
```

## Typical usage patterns

- **Self-contained tool script** — a PEP-723 `# /// script` header declaring its own `requires-python`/`dependencies`, run via `uv run`. Reach for it to ship a portable CLI (typer + rich) that runs on any machine with `uv`, zero packaging. (seen in `JasonLo/undock:scripts/release.py`, `JasonLo/uw-s3:scripts/release.py`, `JasonLo/code-template:{{cookiecutter.project_name}}/scripts/release.py`)
- **Strip `VIRTUAL_ENV` before shelling out to `uv`** — a script launched by `uv run` inherits a `VIRTUAL_ENV` pointing at its *isolated cache env*, so child `uv` commands target the wrong venv. Must-know: the script and the project it acts on live in different environments. (seen in `JasonLo/undock:scripts/release.py`)
- **Project-internal automation script** — imports the project's own package, needs the project venv, run as `uv run python scripts/x.py`. A different category from the portable tool: glue for one repo, not a standalone tool. (seen in `JasonLo/matryoshka-weights:scripts/upload_imagenet_to_s3.py`)

## Learnings

- **"A script needs the project's environment"** → **"A script can own its dependencies."** PEP-723 + uv lets a *tool* script declare deps inline and run anywhere; decide tool-vs-glue before picking the run style. (seen in `JasonLo/undock:scripts/release.py` vs `JasonLo/matryoshka-weights:scripts/upload_imagenet_to_s3.py`)
- **"`uv run python script.py` is just how you run a script"** → **"`python` chooses the project env and ignores inline metadata."** `uv run script.py` builds an isolated env from `# /// script`; inserting `python` silently opts out of that isolation. The question is which environment model you're invoking, not syntax.
- **"The `# /// script` block is mine to hand-maintain"** → **"uv owns the metadata; you state intent."** Use `uv add --script` / `uv lock --script`; hand-editing the dep list drifts it out of sync, same as hand-editing a lockfile.
- **"Self-contained means unpinned/throwaway"** → **"Self-contained can still be reproducible."** `uv lock --script` gives a portable tool the same pinned guarantee a project gets from `uv.lock`; portability and reproducibility are independent axes.
