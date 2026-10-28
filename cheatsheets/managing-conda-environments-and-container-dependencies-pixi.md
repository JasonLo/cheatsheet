# Managing conda environments and container dependencies with pixi

_Grounded in JasonLo's repos as of 2026-10-28. Current practice is from [pixi.prefix.dev/latest](https://pixi.prefix.dev/latest/) (pixi v0.83.0)._

## Reference snippet

```toml
# Minimal pixi.toml for a scientific container with GPU channel support.
# Source: pixi.prefix.dev/latest. Place specialized channels before conda-forge.
[project]
name = "my-proj"
channels = ["pytorch", "nvidia", "conda-forge"]
platforms = ["linux-64"]
channel-priority = "strict"

[dependencies]
python = "3.12.*"
pytorch = { version = ">=2.5", channel = "pytorch" }
pytorch-cuda = { version = "12.4", channel = "pytorch" }

[pypi-dependencies]
# Use this section only for packages that conda-forge does not carry.
anthropic = ">=0.39"

[tasks]
train = "python -m my_proj.train"
```

## Typical usage patterns

- **Container environment pinning.** Commit `pixi.lock` alongside `pixi.toml`. Run `pixi install --locked` in the Dockerfile to install the exact pinned environment. (seen in `JasonLo/best-in-slot:slots/infra/pixi/CHEATSHEET.md`)
- **GPU channel ordering.** Place specialized channels (`pytorch`, `nvidia`) before `conda-forge`. Set `channel-priority = "strict"` to prevent conda-forge from replacing GPU-specific builds. (seen in `JasonLo/best-in-slot:slots/infra/pixi/CHEATSHEET.md`)
- **PyPI fallback.** Add packages that conda-forge does not carry to `[pypi-dependencies]`. These packages resolve on top of the conda base. (seen in `JasonLo/best-in-slot:slots/infra/pixi/CHEATSHEET.md`)

## Learnings

- **`environment.yml` records intent only** → **`pixi.lock` records the full solution.** `pixi.lock` stores every package, exact version, hash, and platform resolution. Commit the lock file to make container builds reproducible.
- **`conda activate` in a container** → **set `PATH` directly.** conda requires a shell activation step before running commands. In a Dockerfile, set `ENV PATH="/app/.pixi/envs/default/bin:$PATH"` instead. (seen in `JasonLo/best-in-slot:slots/infra/pixi/example/Dockerfile`)
- **`--frozen` accepts lock file drift** → **`--locked` aborts on drift.** `pixi install --frozen` installs the lock file even when it does not match `pixi.toml`. Use `--locked` in CI to abort on mismatch and catch drift early.

## Agent rules

- ALWAYS commit `pixi.lock` to version control alongside `pixi.toml`.
- NEVER commit the `.pixi/` directory.
- ALWAYS use `pixi install --locked` in Dockerfiles and CI pipelines.
- ALWAYS place specialized channels before `conda-forge` when you need GPU or scientific packages.
- ALWAYS set `channel-priority = "strict"` when you use more than one channel.
- NEVER use `conda activate` in a container; set `ENV PATH` to `.pixi/envs/default/bin` instead.
- ALWAYS add packages that conda-forge does not carry to `[pypi-dependencies]`.
