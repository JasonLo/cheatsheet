# Notebook kernels with ipykernel

_Grounded in JasonLo's repos as of 2026-06-05; current practice per ipykernel docs (context7 `/ipython/ipykernel`)._

## Reference snippet

```sh
# Per-project kernel: add ipykernel to the project's dev deps, let the editor
# discover the uv-managed .venv — no global kernelspec needed.
uv add --dev ipykernel
uv sync

# VS Code / Cursor: open the .ipynb, "Select Kernel" -> pick the project's .venv.
# Terminal UIs (also resolve the .venv kernel):
uv run jupyter lab
uv run jupyter notebook

# Headless execution (CI / smoke test):
uv run jupyter execute notebooks/explore.ipynb

# Only if a tool needs a *named, discoverable* kernelspec (e.g. a shared
# JupyterHub) — register one pointing at this env:
uv run python -m ipykernel install --user --name myproj --display-name "Python (myproj)"
```

## Typical usage patterns

- Add `ipykernel` to `[dependency-groups].dev`, never as a runtime dep — "this project's notebooks run with this project's deps" (`JasonLo/best-in-slot:slots/python-tooling/ipykernel/example/pyproject.toml`).
- Let the editor auto-discover the uv `.venv` kernel; don't register a global kernelspec (`JasonLo/best-in-slot:slots/python-tooling/ipykernel/README.md`).
- Run UIs and headless executions through `uv run` so the env is resolved consistently (`JasonLo/best-in-slot:slots/python-tooling/ipykernel/CHEATSHEET.md`).

## Learnings

- **"Install a kernel globally / `--user` and point notebooks at it"** → **one kernel per project env, discovered automatically.** The editor reads the project's `.venv`; a per-project dev dep removes global-kernel ambiguity and version drift. Explicit `ipykernel install` is a fallback for shared/multi-env servers, not the default. (seen in `JasonLo/best-in-slot:slots/python-tooling/ipykernel/README.md`)
- **"ipykernel is part of my app"** → **it's dev tooling only.** Belongs in the dev dependency group; shipping it as a runtime dep pollutes the production env. (seen in `JasonLo/best-in-slot:slots/python-tooling/ipykernel/example/pyproject.toml`)
- **"`sys.path.insert` to import project code in a notebook"** → **install the package editable.** `uv sync` makes the project importable in its own env, so the kernel already sees your code — path hacks signal a mis-scoped kernel.

## Agent rules

- ALWAYS add `ipykernel` to `[dependency-groups].dev`, never to runtime `dependencies`.
- ALWAYS run notebook tooling via `uv run` (e.g. `uv run jupyter lab`, `uv run jupyter execute`).
- ALWAYS rely on the editor discovering the uv-managed `.venv` as the kernel.
- ALWAYS make the project importable via `uv sync` (editable install) instead of `sys.path` manipulation.
- ALWAYS strip notebook outputs at the git boundary with an `nbstripout` `.gitattributes` filter.
- NEVER register a global/`--user` kernelspec by default; reserve `python -m ipykernel install` for shared or multi-env servers that require a named kernel.
- NEVER ship `ipykernel` or other notebook tooling as a runtime dependency.
- NEVER commit notebooks with embedded outputs in collaborative repos.
