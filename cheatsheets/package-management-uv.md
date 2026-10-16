# Package & project management with uv

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from uv official docs (context7 `/astral-sh/uv`)._

## Reference snippet

```sh
uv init --package mypkg          # new package project with src layout and build-system
cd mypkg
uv add "httpx>=0.28"             # runtime dependency: adds to [project.dependencies], then locks and syncs
uv add --dev pytest ruff ty      # dev dependency: adds to [dependency-groups].dev. uv syncs it by default.
uv add --optional notebooks pandas   # extra: adds to [project.optional-dependencies].notebooks
uv python pin 3.14               # writes .python-version
uv run pytest -q                 # syncs automatically, then runs in the project env
uv lock --upgrade-package httpx  # upgrade one dependency. uv.lock is the source of truth.
uv sync --locked                 # CI: fail if the lock is not current. Do not relock.
```

## Typical usage patterns

- **Dev tools in `[dependency-groups].dev`.** Add pytest, ruff, and ty with `uv add --dev`. uv syncs this PEP-735 group into the environment by default, but never puts it in the wheel. (seen in `JasonLo/uw-s3:pyproject.toml`, `JasonLo/undock:pyproject.toml`)
- **`uv sync --frozen` or `--locked` in CI and Docker.** Install only from `uv.lock`, so that an old lock fails the build and uv does not relock silently. (seen in `JasonLo/best-in-slot:slots/python-tooling/uv/CHEATSHEET.md`)
- **Global tools with `uv tool` and `uvx`.** The `uv tool install` command installs persistent CLIs, also from `git+https://...`, and `uvx <tool>` does one-time runs. Then the project dependencies do not contain these tools. (seen in `JasonLo/best-in-slot:slots/python-tooling/uv/CHEATSHEET.md`)

## Learnings

- **A `dev` extra holds the dev dependencies** → **The users of a dependency decide where it goes.** Extras are in the published metadata, so consumers can install them. Dev tools in `[dependency-groups]` serve only the people who work on the project. (seen in `JasonLo/best-in-slot:slots/python-tooling/uv/CHEATSHEET.md`)
- **Select a separate build backend, for example hatchling** → **uv manages the build with `uv_build`.** This removes a second tool and matches the output of `uv init`. Use hatchling only when you need its plugins. (seen in `JasonLo/sound-trim:pyproject.toml` and `JasonLo/connectionist:pyproject.toml`)
- **`requirements.txt` and `uv pip install` manage dependencies** → **You declare the project, and uv locks it.** The `pyproject.toml` and `uv.lock` files are the reference for all dependencies, and `uv add` and `uv sync` maintain them. The `uv pip` interface is only for old environments that are not projects.

## Agent rules

- ALWAYS manage project dependencies with `uv add` and `uv remove`.
- ALWAYS treat `uv.lock` as the reference for all installs.
- NEVER edit the lockfile by hand.
- ALWAYS put dev-only tools in `[dependency-groups]` with `uv add --dev`.
- ALWAYS keep `[project.optional-dependencies]` for extras that consumers install.
- ALWAYS use `uv_build` as the build backend for new uv-managed packages.
- ALWAYS pin the backend as `uv_build>=X,<X+1`.
- ALWAYS declare a flat layout with `[tool.uv.build-backend] module-root` and `module-name`.
- ALWAYS pin the interpreter with `uv python pin`, which writes `.python-version`.
- ALWAYS set a minimum Python version in `requires-python`.
- ALWAYS run project commands through `uv run`.
- NEVER call `python` or `pytest` against the project without `uv run`.
- ALWAYS use `uv sync --locked` or `--frozen` in CI and Docker.
- ALWAYS install global CLIs with `uv tool install`.
- ALWAYS run one-time tools with `uvx`.
- NEVER add a standalone tool to the project dependencies.
- NEVER add `requirements.txt` to a project that has a `pyproject.toml`.
- NEVER use `uv pip install` as the default for a project that has a `pyproject.toml`.
- NEVER add a build backend other than `uv_build` without a concrete need, for example a hatchling plugin.
- NEVER split co-developed packages across repos when one `[tool.uv.workspace]` with a shared lock can hold them.
