# Package management + JS toolchain with bun

_Grounded in JasonLo's repos as of 2026-06-05; current practice per bun.sh/docs._

## Reference snippet

```bash
# Manage dependencies
bun install              # install all (reads package.json)
bun add zod              # add to dependencies
bun add -d @types/bun    # add to devDependencies
bun remove zod           # remove
bun ci                   # CI: fail if lockfile out of sync

# Run package.json scripts
bun run dev              # explicit form
bun dev                  # shorthand (resolves after built-in commands)

# Execute a one-off binary without prior install
bunx prettier --write .

# Run TypeScript/TSX directly — no separate build step
bun run src/main.tsx
```

## Typical usage patterns

- **Lock in bun as the constitutional toolchain** — define all dev workflows as `bun run <script>` in `package.json` and encode the no-npm/pnpm rule explicitly (e.g. in CLAUDE.md or a constitution doc). Prevents npm from creeping back in CI or agent-generated commands. Commit `bun.lock` (text); delete any `bun.lockb` (binary, legacy pre-v1.2). (JasonLo/skill-cellar:specs/CONSTITUTION.md)

- **Run TypeScript/TSX entry points directly** — script `"dev": "bun run src/main.tsx"` in package.json; no separate `tsc` step, no ts-node wrapper. Bun transpiles on the fly. Works for TUI apps, CLI scripts, and services without a build pipeline. (JasonLo/skill-cellar:package.json)

- **Delegate all task invocation through `bun run`** — even when using vitest or another test runner, invoke it via `bun run test`. Keeps the interface uniform (all tasks go through bun), and lets you swap runners later without changing how CI calls things. (JasonLo/skill-cellar:package.json)

## Learnings

- **npm runs lifecycle scripts by default → bun skips them unless opted in.** Packages with `postinstall`/`prepare` hooks don't execute on `bun install` unless listed in `trustedDependencies`. This blocks a class of supply-chain attacks, but silently breaks packages that expect a build step at install time. When a dep misbehaves after install, add it to `trustedDependencies` in package.json — don't reach for `npm install` as a workaround.

- **Binary lockfile (`bun.lockb`) → text lockfile (`bun.lock`).** Bun v1.2+ generates a human-readable `bun.lock` by default. Repos still using `bun.lockb` are on an older workflow; migrate by deleting the binary lockfile and re-running `bun install`. Always commit `bun.lock` to git for reproducible installs.

- **Bun CLI flags must come before `run`, not after it.** `bun run --watch dev` silently ignores `--watch`; `bun --watch run dev` is correct. The pattern is `bun [bun-flags] run <script>`, not `bun run [flags] <script>` — a common trap when muscle memory from npm carries over.

## Agent rules

- ALWAYS use `bun install` / `bun add` / `bun remove` — NEVER npm, yarn, or pnpm
- ALWAYS commit `bun.lock` (text) to git; delete `bun.lockb` (binary) if present
- ALWAYS place bun flags before `run`: `bun --watch run dev`, NEVER `bun run --watch dev`
- NEVER assume lifecycle scripts ran; add packages requiring postinstall to `trustedDependencies`
