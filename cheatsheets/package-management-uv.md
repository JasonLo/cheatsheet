# Package & project management with uv

_Grounded in JasonLo's repos as of 2026-06-05; current practice per uv official docs (context7 `/astral-sh/uv`)._

> Scope: project/dependency lifecycle (init, add, sync, lock, run, tools, Python pinning, build backend). For single-file PEP-723 scripts, see `self-contained-scripts-uv.md`.

## Reference snippet

```sh
uv init --package mypkg          # new packaged project (src layout, build-system)
cd mypkg
uv add "httpx>=0.28"             # runtime dep -> [project.dependencies] + lock + sync
uv add --dev pytest ruff ty      # dev dep -> [dependency-groups].dev (synced by default)
uv add --optional notebooks pandas   # extra -> [project.optional-dependencies].notebooks
uv python pin 3.14               # writes .python-version
uv run pytest -q                 # auto-syncs, runs inside the project env
uv lock --upgrade-package httpx  # bump one dep; uv.lock is the source of truth
uv sync --locked                 # CI: fail if lock is stale, no implicit relock
```

```toml
[project]
name = "mypkg"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = ["httpx>=0.28"]

[project.optional-dependencies]      # extras: installable by consumers (`pip install mypkg[notebooks]`)
notebooks = ["pandas>=2.3", "ipykernel>=7.1"]

[dependency-groups]                  # dev-only: never published, synced by default
dev = ["pytest>=9", "ruff>=0.15", "ty>=0.0.20"]

[project.scripts]
mypkg = "mypkg.cli:main"

[build-system]
requires = ["uv_build>=0.11,<0.12"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-root = ""                     # flat layout: package at repo root, not src/
```

## Typical usage patterns

- **`uv_build` as the build backend** — standardize on `uv_build` with a pinned `requires=["uv_build>=X,<X+1"]` range for any installable package. Reach for it on every new CLI/library. (`JasonLo/uw-s3:pyproject.toml`, `JasonLo/undock:pyproject.toml`, `JasonLo/sound-trim:pyproject.toml`)
- **Standardized `[dependency-groups].dev`** — dev tooling (pytest, ruff, ty) lives in the PEP-735 group, added via `uv add --dev`, synced into the env by default but never shipped in the wheel. (`JasonLo/uw-s3:pyproject.toml`, `JasonLo/undock:pyproject.toml`)
- **`uv sync --frozen` / `--locked` in CI & Docker** — install strictly from `uv.lock` so a stale lock fails the build instead of silently relocking. (`JasonLo/best-in-slot:slots/python-tooling/uv/CHEATSHEET.md`)
- **Global tools via `uv tool` / `uvx`** — `uv tool install` (incl. from `git+https://...`) for persistent CLIs, `uvx <tool>` for ephemeral one-offs; keeps tools out of project deps. (`JasonLo/best-in-slot:slots/python-tooling/uv/CHEATSHEET.md`)

## Learnings

- **"Dev deps go under `[project.optional-dependencies]` (a `dev` extra)"** → **"Dev deps belong in `[dependency-groups]`."** Extras are part of the *published* package's metadata (a consumer can install them); dev tooling is not — PEP-735 groups model "needed to work on this, never shipped." The split is about audience, not syntax. (older `dev`-as-extra shape still shown in `JasonLo/best-in-slot:slots/python-tooling/uv/CHEATSHEET.md`)
- **"Pick a build backend like hatchling/setuptools, configured separately"** → **"`uv_build` is the default, uv-native backend."** When uv manages the project, its own backend removes a second tool from the toolchain and matches `uv init`'s output; reach for hatchling only when you need its plugins. (legacy `hatchling` in `JasonLo/connectionist:pyproject.toml`)
- **"`requirements.txt` / `uv pip install` is how you manage deps"** → **"`pyproject.toml` + `uv.lock` is the project's source of truth; `uv add`/`uv sync` maintain it."** The project workflow is declarative and locked; the `uv pip` interface is an escape hatch for legacy/non-project envs, not the default.

## Agent rules

- ALWAYS manage project deps with `uv add` / `uv remove` and let `uv.lock` be the source of truth; never hand-edit the lockfile.
- ALWAYS put dev-only tooling in `[dependency-groups]` via `uv add --dev`, and reserve `[project.optional-dependencies]` for consumer-facing extras.
- ALWAYS use `uv_build` as the build backend for new uv-managed packages; pin it as `uv_build>=X,<X+1`.
- ALWAYS declare layout explicitly with `[tool.uv.build-backend] module-root`/`module-name` for flat layouts.
- ALWAYS pin the interpreter with `uv python pin` / `.python-version` and set a `requires-python` floor.
- ALWAYS run project commands through `uv run` so the env auto-syncs; never call a bare `python`/`pytest` against the project.
- ALWAYS use `uv sync --locked` (or `--frozen`) in CI/Docker so a stale lock fails the build instead of relocking.
- ALWAYS install global CLIs with `uv tool install` / run one-offs with `uvx`; never add a standalone tool to project dependencies.
- NEVER introduce `requirements.txt` or default to `uv pip install` for a project that has a `pyproject.toml`.
- NEVER add a build backend other than `uv_build` unless a concrete need (e.g. a hatchling plugin) demands it.
- NEVER split co-developed packages across repos when a single `[tool.uv.workspace]` with shared lock fits.
