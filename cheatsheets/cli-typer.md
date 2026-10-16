# Terminal CLIs with Typer

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from Typer official docs (context7 `/fastapi/typer`)._

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
        raise typer.Exit(code=2)  # A non-zero code shows an error


if __name__ == "__main__":
    app()
```

## Typical usage patterns

- **One `typer.Typer(...)` for each package that you configure at construction**. Set `no_args_is_help=True` and `add_completion=False`. Then a call without arguments prints help, and the CLI shows no shell-completion options. (seen in `JasonLo/best-in-slot:bis/cli.py`, `JasonLo/cairn:src/cairn/cli/app.py`)
- **An `@app.callback()` root for global options**. The `--version` option is a callback option with `is_eager=True` that echoes the version and calls `raise typer.Exit()`. (seen in `JasonLo/cairn:src/cairn/cli/app.py`)
- **Typer helpers for exits and user input**. Commands use `raise typer.Exit(code=N)`, `typer.echo(..., err=True)`, `typer.prompt`, and `typer.confirm`. They do not use `sys.exit` or `input`. (seen in `JasonLo/best-in-slot:bis/cli.py`)

## Learnings

- **CLI metadata goes in the default value (`x: int = typer.Option(...)`)** → **CLI metadata goes in the type (`x: Annotated[int, typer.Option(...)]`)**. The type holds the CLI metadata, and the default is a real Python default. The function stays callable as plain Python, and type checkers see the true type.
- **`argparse` subparsers and manual `sys.exit` describe the parser** → **Typed functions let Typer make the parser**. The types, for example `int`, `Enum`, `Path(exists=True)`, and `bool` flags, control choices and validation. `typer.Exit(code=…)` replaces raw exits.
- **One CLI file with one large `if/elif` dispatch** → **Domain sub-apps that `add_typer` composes at the root**. Each domain gets its own `Typer` instance in its own module. Each file stays small, and users can find each command in the tree.

## Agent rules

- ALWAYS declare CLI parameters as `Annotated[Type, typer.Option(...)]` or `Annotated[Type, typer.Argument(...)]`.
- ALWAYS write a parameter default as a real Python default after the annotation.
- NEVER use the default-value form `param: Type = typer.Option(...)` or `= typer.Argument(...)` in new code.
- NEVER pass the Ellipsis `...` to mark a required parameter.
- ALWAYS construct the app with `typer.Typer(no_args_is_help=True, add_completion=False)` unless the user wants shell completion.
- ALWAYS split a CLI with many command groups into domain `Typer` instances that `app.add_typer(sub, name=...)` composes.
- ALWAYS put global options, for example `--version`, on an `@app.callback()`.
- ALWAYS use `is_eager=True` and `raise typer.Exit()` for an option that stops the program early.
- ALWAYS exit with `raise typer.Exit(code=N)`, with a non-zero code for errors.
- NEVER call `sys.exit` from a command.
- ALWAYS use `typer.echo`, `typer.prompt`, and `typer.confirm` instead of `print` and `input`.
- ALWAYS pass `err=True` to `typer.echo` for error messages.
- ALWAYS let types control parsing and validation: `Enum` for choices, `Path` with `exists=`/`dir_okay=`, and `bool` for flags.
- NEVER parse choices, paths, or flags by hand.
- ALWAYS use Typer instead of hand-written `argparse` when a tool has typed parameters or more than one subcommand.
