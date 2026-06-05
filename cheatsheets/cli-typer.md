# Terminal CLIs with Typer

_Grounded in JasonLo's repos as of 2026-06-05; current practice per Typer official docs (context7 `/fastapi/typer`)._

## Reference snippet

```python
from typing import Annotated

import typer

app = typer.Typer(no_args_is_help=True, add_completion=False, help="Example CLI.")


def _version_cb(value: bool) -> None:
    if value:
        typer.echo("0.1.0")
        raise typer.Exit()


@app.callback()
def _root(
    version: Annotated[
        bool, typer.Option("--version", callback=_version_cb, is_eager=True)
    ] = False,
) -> None:
    """Root callback — shared options live here."""


@app.command()
def greet(
    name: Annotated[str, typer.Argument(help="Who to greet.")],
    times: Annotated[int, typer.Option("--times", "-n", min=1)] = 1,
    loud: Annotated[bool, typer.Option(help="UPPERCASE output.")] = False,
) -> None:
    """Say hello."""
    msg = f"Hello, {name}!"
    for _ in range(times):
        typer.echo(msg.upper() if loud else msg)
    if not name:
        raise typer.Exit(code=2)  # non-zero = error


if __name__ == "__main__":
    app()
```

## Typical usage patterns

- **One `typer.Typer(...)` per package, configured up front** — set `no_args_is_help=True` and `add_completion=False` at construction so a bare invocation prints help and no shell-completion noise leaks. (`JasonLo/best-in-slot:bis/cli.py`, `JasonLo/cairn/src/cairn/cli/app.py`)
- **Sub-apps composed with `add_typer`** — each command group is its own `Typer` in its own module, wired into the root app under a name; keeps large CLIs flat-per-file. (`JasonLo/cairn/src/cairn/cli/app.py`)
- **`@app.callback()` root for shared/global options** — `--version` implemented as a callback option with `is_eager=True` that echoes and `raise typer.Exit()`. (`JasonLo/cairn/src/cairn/cli/app.py`)
- **`raise typer.Exit(code=N)` for error exits**, `typer.echo(..., err=True)` for stderr, `typer.prompt` / `typer.confirm` for interaction — used instead of `sys.exit` / `input`. (`JasonLo/best-in-slot:bis/cli.py`)

## Learnings

- **Default-value parameters (`x: int = typer.Option(...)`) → type annotation carries the metadata (`x: Annotated[int, typer.Option(...)]`).** The parameter's *type* is the source of truth and its default is a real Python default, so the same function stays callable as a plain function and type checkers see the true type — the old style overloaded the default slot with a sentinel object.
- **Hand-rolled `argparse` subparsers / manual `sys.exit` → declare commands as typed functions and let Typer derive parsing.** Intent shifts from "describe the parser" to "write the function"; types drive choices/validation (`int`, `Enum`, `Path(exists=True)`, `bool` flags) and `typer.Exit(code=…)` replaces raw exits.
- **Monolithic single-file CLI → sub-apps via `add_typer`.** Group commands by domain into separate `Typer` instances; composition at the root keeps each file small and the command tree discoverable, instead of one growing `if/elif` dispatch.

## Agent rules

- ALWAYS declare CLI parameters as `Annotated[Type, typer.Option(...)]` / `Annotated[Type, typer.Argument(...)]`, with any default as a real Python default after the annotation.
- NEVER use the default-value form `param: Type = typer.Option(...)` / `= typer.Argument(...)` in new code.
- NEVER pass `...` (Ellipsis) to mark a parameter required — omit the default instead.
- ALWAYS construct the app with `typer.Typer(no_args_is_help=True, add_completion=False)` unless completion is explicitly wanted.
- ALWAYS split a multi-group CLI into per-domain `Typer` instances composed with `app.add_typer(sub, name=...)`.
- ALWAYS put global options (e.g. `--version`) on an `@app.callback()`, using `is_eager=True` and `raise typer.Exit()` for short-circuit options.
- ALWAYS exit via `raise typer.Exit(code=N)` (non-zero for errors); NEVER call `sys.exit` from a command.
- ALWAYS use `typer.echo` (with `err=True` for errors), `typer.prompt`, and `typer.confirm` instead of `print` / `input`.
- ALWAYS let types drive parsing/validation (`Enum` for choices, `Path` with `exists=`/`dir_okay=`, `bool` for flags); NEVER hand-parse those.
- PREFER Typer over hand-written `argparse` once a tool has typed parameters or more than one subcommand.
