# Containerized dev environment setup with devcontainers

_Grounded in JasonLo's repos as of 2026-08-31; current practice per containers.dev spec._

## Reference snippet

```json
{
  "name": "my-project",
  "image": "mcr.microsoft.com/devcontainers/python:3.12",
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/anthropics/devcontainer-features/claude-code:1": {}
  },
  "customizations": {
    "vscode": {
      "extensions": ["ms-python.python", "ms-toolsai.jupyter"],
      "settings": { "python.defaultInterpreterPath": "/usr/local/bin/python" }
    }
  },
  "postCreateCommand": "pip install -e '.[dev]'"
}
```

## Typical usage patterns

- **Minimal sandbox for Claude Code with `--dangerously-skip-permission`**: a single-file `devcontainer.json` with a base image + `postCreateCommand` to install Claude Code; the container's isolation limits blast radius to the container, not the host. (`JasonLo/jasonlo.dev:src/content/blog/devcontainer-as-claude-code-sandbox.mdx`)

- **GPU-backed custom image for deep-learning work**: set `image` to a framework-specific registry image (e.g., `tensorflow/tensorflow:2.9.3-gpu-jupyter`) with `runArgs: ["--gpus", "all"]` and `workspaceMount` to bind the repo into the container. (`JasonLo/connectionist:.devcontainer/devcontainer.json`)

- **Features for shared tooling**: install cross-cutting tools (Node, GitHub CLI, Claude Code) via `ghcr.io/devcontainers/features/<name>:<major>` instead of baking them into a Dockerfile — lets the base image vary while keeping tool versions explicit. (`simulation-based-inference/simulation-based-inference.github.io:.devcontainer/devcontainer.json`)

## Learnings

- **Top-level `extensions` and `settings` keys** → **`customizations.vscode.extensions` and `customizations.vscode.settings`.** VS Code stopped reading the top-level keys in 1.76 (2023); they are silently ignored, so extensions listed there are never installed. The intent (configure the editor inside the container) is the same; the key path is not. (seen in `JasonLo/connectionist:.devcontainer/devcontainer.json`)

- **Old shorthand feature IDs** (`"features": {"git": {"version": "latest"}}`) → **full OCI URI format** (`"ghcr.io/devcontainers/features/git:1"`). The shorthand was a VS Code-specific convention from the pre-spec era; the current spec resolves feature names only from OCI registries, so shorthand names either fail silently or resolve to nothing. (seen in `JasonLo/connectionist:.devcontainer/devcontainer.json`)

- **`postCreateCommand` as the one lifecycle hook** → **differentiate by when it runs.** `postCreateCommand` runs once at creation; `postStartCommand` re-runs every container start; `onCreateCommand` runs before the user is set. Treating them as interchangeable means idempotent one-time setup runs on every container start, or startup-time services never launch after a rebuild.

## Agent rules

- ALWAYS put VS Code extensions and settings under `customizations.vscode`, never at the JSON root.
- ALWAYS use full OCI URIs for features (`ghcr.io/devcontainers/features/<name>:<major>`), never shorthand names.
- NEVER use `appPort`; use `forwardPorts` instead (appPort is legacy and ignored by newer clients).
- ALWAYS pin feature major versions explicitly (`:1`, `:2`), not `:latest`, so rebuilds are reproducible.
- NEVER duplicate tooling in both `features` and a `Dockerfile` — pick one installation path per tool.
