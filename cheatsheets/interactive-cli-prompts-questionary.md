# Interactive CLI prompts with questionary

_Grounded in JasonLo's repos as of 2026-07-03. Current practice is from [questionary.readthedocs.io](https://questionary.readthedocs.io/en/stable/) (v2.1.1)._

## Reference snippet

```python
def pick_action(current: str) -> str:
    import questionary                      # Import late. This keeps the TTY dependency at the edge of the program.
    from questionary import Choice

    choice = questionary.select(
        "Pick an action:",
        choices=[
            Choice("Accept", value="accept"),
            Choice("Skip", value="skip"),
            Choice("Type a different name…", value="__freeform__"),
        ],
    ).ask()

    if choice is None:                      # On Ctrl-C or Esc, .ask() returns None. It does not raise an error.
        raise KeyboardInterrupt

    if choice == "__freeform__":
        value = questionary.text("Enter name:", default=current).ask()
        if value is None:
            raise KeyboardInterrupt
        return value
    return choice
```

## Typical usage patterns

- Use `questionary.select()` with `Choice(title=..., value=...)` objects, so the display label is separate from the returned value. Add a sentinel `Choice` that opens a freeform `questionary.text(..., default=current)` prompt. (seen in `JasonLo/best-in-slot:bis/walk.py`)
- Build the full `message=` string with evidence counts, recency, and confidence before you call `select()`. The context belongs in the prompt header, not in separate `print()` calls. (seen in `JasonLo/best-in-slot:bis/walk.py`)
- Isolate questionary with a `@runtime_checkable Protocol` and a `ScriptedAdapter` test double that reads a flat answer list. Only the production adapter imports and calls questionary, so the test code never uses it. (seen in `JasonLo/best-in-slot:bis/walk.py`)

## Learnings

- **`.ask()` raises on cancel, so the return value needs no check** → **Cancel is a normal return value.** `.ask()` returns `None` on Ctrl-C or Esc, but `.unsafe_ask()` raises `KeyboardInterrupt`. Check every answer from `.ask()` with `if answer is None`. (seen in `JasonLo/best-in-slot:bis/walk.py`)
- **Dicts `{"name": ..., "value": ...}` work for every API** → **Each API style has its own choice format.** The direct `select()`/`checkbox()` API takes `Choice(title=..., value=..., description=...)` objects. Dicts belong to the `prompt()`/`form()` dict-of-questions style, and only a `Choice` has the `description=` field.
- **Import questionary at the module top level** → **Keep the TTY dependency in the outer layer of the program.** Questionary needs an interactive TTY at import time. Import it lazily or only inside an adapter Protocol, so the module imports in CI, tests, and headless environments.

## Agent rules

- ALWAYS check `if answer is None` after every `.ask()` call.
- ALWAYS handle the cancellation when `.ask()` returns `None`.
- NEVER assume that `.ask()` raises on Ctrl-C.
- ALWAYS use `Choice(title=..., value=...)` to build choices programmatically for `select()`/`checkbox()`.
- NEVER pass raw dicts `{"name": ..., "value": ...}` to the direct API.
- ALWAYS import questionary lazily inside method bodies or inside an adapter Protocol.
- NEVER import questionary at the module top level in shared or test-facing code.
- NEVER call questionary functions directly from test code.
- ALWAYS isolate questionary with a Protocol and a scripted test double.
