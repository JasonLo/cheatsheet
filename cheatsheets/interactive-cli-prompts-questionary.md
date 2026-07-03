# Interactive CLI prompts with questionary

_Grounded in JasonLo's repos as of 2026-07-03; current practice per [questionary.readthedocs.io](https://questionary.readthedocs.io/en/stable/) (v2.1.1)._

## Reference snippet

```python
from questionary import Choice
import questionary

choice = questionary.select(
    "Pick an action:",
    choices=[
        Choice("Accept", value="accept"),
        Choice("Skip", value="skip"),
        Choice("Type a different name…", value="__freeform__"),
    ],
).ask()

if choice is None:           # Ctrl-C or Esc — .ask() returns None, never raises
    raise KeyboardInterrupt

if choice == "__freeform__":
    value = questionary.text("Enter name:", default="current-value").ask()
    if value is None:
        raise KeyboardInterrupt
```

## Typical usage patterns

- `questionary.select()` for single-pick menus with `Choice(title=..., value=...)` objects; append a sentinel `Choice` to trigger a freeform fallback via `questionary.text(..., default=current)` — decouples display label from returned token (seen in `JasonLo/best-in-slot:bis/walk.py`)
- Rich message construction: assemble the full `message=` string (with evidence counts, recency, confidence qualifiers) before calling `select()` — context belongs in the prompt header, not in separate `print()` calls (seen in `JasonLo/best-in-slot:bis/walk.py`)
- Protocol + adapter pattern for TTY isolation: define a `@runtime_checkable Protocol` with a `ScriptedAdapter` test double that consumes a flat answer list; questionary is imported and called only inside the production adapter — test code never touches it (seen in `JasonLo/best-in-slot:bis/walk.py`)

## Learnings

- **Calling `.ask()` without checking the return value** → `.ask()` returns `None` on Ctrl-C or Esc instead of raising; always guard with `if answer is None` or switch to `.unsafe_ask()` which re-raises `KeyboardInterrupt` explicitly (seen in `JasonLo/best-in-slot:bis/walk.py`)
- **Dict choices `{"name": ..., "value": ...}` in the direct API** → prefer `Choice(title=..., value=..., description=...)` for the `select()`/`checkbox()` direct API; dicts are the format for the `prompt()`/`form()` dict-of-questions style; `Choice` gains a `description=` field in v2.1.0 and allows disabled/checked states cleanly
- **Importing questionary at module top-level** → questionary depends on a live TTY at import time; import lazily (inside the method body) or hide behind an adapter Protocol so the module remains importable in CI, tests, and headless environments

## Agent rules

- ALWAYS check `if answer is None` after every `.ask()` call and handle cancellation; NEVER assume `.ask()` raises on Ctrl-C.
- ALWAYS use `Choice(title=..., value=...)` when building choices programmatically for `select()`/`checkbox()`; NEVER pass raw dicts `{"name": ..., "value": ...}` to the direct API.
- ALWAYS import questionary lazily (inside method bodies) or behind an adapter Protocol; NEVER import it at module top-level in shared or test-facing code.
- NEVER call questionary functions directly from test code; ALWAYS isolate them behind a Protocol with a scripted test double.
