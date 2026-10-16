# Notebook kernels with ipykernel

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from ipykernel docs (context7 `/ipython/ipykernel`)._

## Reference snippet

```sh
# Kernel for each project: add ipykernel to the dev dependencies of the project.
# The editor finds the .venv that uv manages. You do not need a global kernelspec.
uv add --dev ipykernel
uv sync

# VS Code or Cursor: open the .ipynb file. Click "Select Kernel" and select the .venv of the project.
# Terminal UIs. These also find the .venv kernel:
uv run jupyter lab
uv run jupyter notebook

# Run with no UI, for CI or for a smoke test:
uv run jupyter execute notebooks/explore.ipynb

# Do this only if a tool needs a named kernelspec that it can find,
# for example a shared JupyterHub. Register a kernelspec for this env:
uv run python -m ipykernel install --user --name myproj --display-name "Python (myproj)"
```

## Typical usage patterns

- **Kernel as a dev dependency.** Add `ipykernel` to `[dependency-groups].dev`, not to the runtime dependencies. Then the notebooks of the project run with the dependencies of the project. (seen in `JasonLo/best-in-slot:slots/python-tooling/ipykernel/example/pyproject.toml`)
- **Automatic kernel discovery.** The editor finds the uv `.venv` kernel, so the project needs no global kernelspec. (`JasonLo/best-in-slot:slots/python-tooling/ipykernel/README.md`)
- **All notebook tools through `uv run`.** Run the UIs and headless executions with `uv run`, so the environment resolves the same way each time. (`JasonLo/best-in-slot:slots/python-tooling/ipykernel/CHEATSHEET.md`)

## Learnings

- **One global kernel serves all notebooks** → **Each project environment is its own kernel**. A kernel for each project shows clearly which environment runs, and versions do not change. `ipykernel install` is a fallback for shared or multi-environment servers. (seen in `JasonLo/best-in-slot:slots/python-tooling/ipykernel/README.md`)
- **ipykernel is part of the application** → **ipykernel is a development tool only**. A runtime dependency on it adds unnecessary packages to the production environment. (seen in `JasonLo/best-in-slot:slots/python-tooling/ipykernel/example/pyproject.toml`)
- **A notebook needs path changes to import project code** → **The project environment already contains the project**. The `uv sync` command installs the package in editable mode, so the kernel can import your code. A `sys.path.insert` call shows that the kernel uses the wrong environment.

## Agent rules

- ALWAYS add `ipykernel` to `[dependency-groups].dev`, not to runtime `dependencies`.
- ALWAYS run notebook tools with `uv run`, for example `uv run jupyter lab` or `uv run jupyter execute`.
- ALWAYS let the editor find the uv-managed `.venv` as the kernel.
- ALWAYS make the project importable with the editable install of `uv sync`.
- NEVER change `sys.path` to import project code in a notebook.
- ALWAYS remove notebook outputs when git stages them with an `nbstripout` `.gitattributes` filter.
- NEVER register a global or `--user` kernelspec by default.
- ALWAYS limit `python -m ipykernel install` to shared or multi-environment servers that need a named kernel.
- NEVER ship `ipykernel` or other notebook tools as a runtime dependency.
- NEVER commit notebooks with outputs in shared repositories.
