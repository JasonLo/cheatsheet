# Containerized dev environment setup with devcontainers

_Grounded in JasonLo's repos as of 2026-08-31. Current practice is from the containers.dev spec._

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

- **Minimal sandbox for Claude Code with `--dangerously-skip-permission`.** Use a single `devcontainer.json` with a base image and a `postCreateCommand` that installs Claude Code. The container keeps possible damage inside the container, not on the host. (seen in `JasonLo/jasonlo.dev:src/content/blog/devcontainer-as-claude-code-sandbox.mdx`)

- **Custom GPU image for deep-learning work.** Set `image` to a framework image, for example `tensorflow/tensorflow:2.9.3-gpu-jupyter`. Add `runArgs: ["--gpus", "all"]` and a `workspaceMount` that binds the repository into the container. (seen in `JasonLo/connectionist:.devcontainer/devcontainer.json`)

- **Features for shared tools.** Install common tools, for example Node, GitHub CLI, and Claude Code, with `ghcr.io/devcontainers/features/<name>:<major>`, not in a Dockerfile. Then the base image can change and the tool versions stay specified. (seen in `simulation-based-inference/simulation-based-inference.github.io:.devcontainer/devcontainer.json`)

## Learnings

- **Editor settings are general container settings** → **Editor settings belong to one tool, in the `customizations` namespace**. VS Code ignores top-level `extensions` and `settings` keys and gives no error. Put them under `customizations.vscode`, or the extensions do not install. (seen in `JasonLo/connectionist:.devcontainer/devcontainer.json`)

- **A feature is a local name that the editor knows** → **A feature is a versioned package from an OCI registry**. The current spec resolves features only from OCI registries, for example `"ghcr.io/devcontainers/features/git:1"`. Shorthand names, for example `"git"`, fail or resolve to nothing. (seen in `JasonLo/connectionist:.devcontainer/devcontainer.json`)

- **One lifecycle hook does all setup** → **Each lifecycle hook has a different run time**. The `onCreateCommand` hook runs before the container sets the user, `postCreateCommand` runs one time at creation, and `postStartCommand` runs at each start. Choose the hook by the time when the step must run.

## Agent rules

- ALWAYS put VS Code extensions and settings under `customizations.vscode`.
- NEVER put VS Code extensions or settings at the JSON root.
- ALWAYS use full OCI URIs for features, for example `ghcr.io/devcontainers/features/<name>:<major>`.
- NEVER use shorthand feature names.
- NEVER use `appPort`.
- ALWAYS use `forwardPorts` to expose ports.
- ALWAYS pin feature major versions, for example `:1` or `:2`, not `:latest`.
- NEVER install the same tool in both `features` and a `Dockerfile`.
