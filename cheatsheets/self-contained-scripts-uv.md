# Self-contained scripts with uv

_Grounded in JasonLo's repos as of 2026-06-05; current practice per uv official docs (context7 `/astral-sh/uv`)._

## Typical usage patterns

- **The self-contained tool script.** A standalone executable shipped *with* a
  repo but not *part of* its package: a PEP-723 `# /// script` header declaring
  its own `requires-python` and `dependencies`, run via `uv run scripts/foo.py`.
  Your reusable release manager is the canonical example — same shape across
  `JasonLo/undock:scripts/release.py`,
  `JasonLo/uw-s3:scripts/release.py`, and
  `JasonLo/code-template:{{cookiecutter.project_name}}/scripts/release.py`.
  The intent: ship a CLI tool (typer + rich) that runs identically on any
  machine with `uv`, with zero `pip install` and no packaging step.

- **The environment-isolation gotcha you already solved.** In
  `JasonLo/undock:scripts/release.py` you strip `VIRTUAL_ENV` from the
  environment before shelling out to `uv version`, because a script launched by
  `uv run` inherits a `VIRTUAL_ENV` pointing at the script's *isolated cache
  env* — so child `uv` commands would otherwise target the wrong venv. The
  pattern worth remembering: a self-contained script and the project it acts on
  live in **different** environments; be explicit about which one a subprocess
  should see.

- **The project-internal automation script.** A one-off operational script that
  imports the project's own package and needs the project venv, e.g.
  `JasonLo/matryoshka-weights:scripts/upload_imagenet_to_s3.py`
  (`from matryoshka_weights.s3 import ...`, run as
  `uv run python scripts/upload_imagenet_to_s3.py`). This is a legitimately
  *different* category from the self-contained tool — it is glue for one repo,
  not a portable tool.

## Learnings

- **"A script needs the project's environment"** → **"A script can own its
  dependencies."** The mental shift PEP-723 + uv enables is that a script is no
  longer a second-class citizen of a project venv. If a script is a *tool*
  (not project-internal glue), declare its deps inline and let it run anywhere
  via `uv run script.py`. Your `matryoshka-weights` upload script is bound to
  its repo by `uv run python ... ` + a project import; your `undock/release.py`
  is portable. Decide which one you're writing *before* you pick the run style.

- **"`uv run python script.py` is just how you run a script with uv"** →
  **"The `python` indirection chooses the project environment and ignores
  inline metadata."** `uv run script.py` reads the `# /// script` block and
  builds an *isolated* env for that script; inserting `python` runs it in the
  active/project environment instead. The conceptual question isn't syntax —
  it's *which environment model you're invoking*: a self-contained tool, or a
  command inside a project. Reaching for `python` silently opts out of the
  isolation a self-contained script is meant to have.

- **"The `# /// script` block is mine to hand-maintain"** → **"uv owns the
  metadata; you state intent."** Treat the dependency block as generated, not
  hand-curated: `uv add --script script.py 'rich'` writes and updates it for
  you, and `uv lock --script script.py` pins it to a sibling `.lock` for
  reproducibility. Hand-editing the list is how it drifts out of sync with what
  actually resolves — the same reason you don't hand-edit a project lockfile.

- **"Self-contained means unpinned / throwaway"** → **"Self-contained can still
  be reproducible."** A portable tool script isn't inherently less rigorous than
  a project: if it matters, `uv lock --script` gives it the same
  resolved-and-pinned guarantee a project gets from `uv.lock`. Portability and
  reproducibility are independent axes, not a trade-off.
