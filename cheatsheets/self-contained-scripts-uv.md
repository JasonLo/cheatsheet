# Self-contained scripts with uv

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from uv official docs (context7 `/astral-sh/uv`)._

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
# run anywhere: `uv run scripts/foo.py world`. You do not need a venv or pip install.
# add a dependency: `uv add --script scripts/foo.py rich`. Pin the dependencies: `uv lock --script scripts/foo.py`
```

## Typical usage patterns

- A **standalone tool script** has a PEP-723 `# /// script` header with its own `requires-python` and `dependencies`, and runs with `uv run`. Use it to distribute a portable CLI with typer and rich that needs only `uv`. (seen in `JasonLo/undock:scripts/release.py`, `JasonLo/uw-s3:scripts/release.py`, `JasonLo/code-template:{{cookiecutter.project_name}}/scripts/release.py`)
- **Remove `VIRTUAL_ENV`** before a script runs child `uv` commands. Under `uv run`, the script inherits a `VIRTUAL_ENV` for its isolated cache env, and the child commands use the wrong venv. (seen in `JasonLo/undock:scripts/release.py`)
- A **project helper script** imports the package of the project and needs the project venv. Run it with `uv run python scripts/x.py`. (seen in a private repo)

## Learnings

- **A script needs the environment of the project** → **A script can own its dependencies.** A PEP-723 tool script declares its dependencies inline. The run style depends on the script type: a standalone tool or a project helper script. (seen in `JasonLo/undock:scripts/release.py` and a private project helper script)
- **`uv run python script.py` is the usual run command** → **`python` selects the project env and ignores inline metadata.** `uv run script.py` builds an isolated env from `# /// script`. The extra `python` disables that isolation without a warning.
- **The `# /// script` block is for hand maintenance** → **uv owns the metadata, and you state the intent.** Use `uv add --script` and `uv lock --script`. A dependency list or a lockfile that you edit by hand becomes inconsistent.

## Agent rules

- ALWAYS choose the run style from the script type, a standalone tool or a project helper script.
- ALWAYS give a standalone tool a `# /// script` header.
- ALWAYS run a standalone tool with `uv run script.py`.
- ALWAYS run a project helper script with `uv run python scripts/x.py`.
- NEVER add `python` to `uv run script.py` for a standalone tool.
- ALWAYS manage inline dependencies with `uv add --script` and `uv lock --script`.
- NEVER edit the `# /// script` dependency list by hand.
- ALWAYS remove `VIRTUAL_ENV` before a `uv run` script starts child `uv` commands.
- ALWAYS run `uv lock --script` when a standalone tool needs reproducibility.
