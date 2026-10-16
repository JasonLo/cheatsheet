# Package management + JS toolchain with bun

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from bun.sh/docs._

## Reference snippet

```bash
# Manage dependencies
bun install              # install all dependencies from package.json
bun add zod              # add to dependencies
bun add -d @types/bun    # add to devDependencies
bun remove zod           # remove a dependency
bun ci                   # CI: fail if the lockfile does not match

# Run package.json scripts
bun run dev              # full form
bun dev                  # short form. Built-in commands have priority.

# Run a binary one time without an install
bunx prettier --write .

# Run TypeScript or TSX directly. You do not need a separate build step.
bun run src/main.tsx
```

## Typical usage patterns

- **Make bun the required toolchain**. All dev workflows are `bun run <script>` entries in `package.json`. A rule in CLAUDE.md or in a constitution document does not allow npm and pnpm in CI and in commands that agents write. (seen in `JasonLo/skill-cellar:specs/CONSTITUTION.md`)

- **Run TypeScript/TSX entry points directly**. The script `"dev": "bun run src/main.tsx"` in package.json needs no `tsc` step and no ts-node wrapper, because Bun transpiles the code when it runs it. (seen in `JasonLo/skill-cellar:package.json`)

- **Send all tasks through `bun run`**. Call vitest or another test runner with `bun run test`, so that all tasks have one interface. Then you can change the runner without a change to how CI calls it. (seen in `JasonLo/skill-cellar:package.json`)

## Learnings

- **Install runs the lifecycle scripts of each package** → **Install runs lifecycle scripts only for trusted packages**. The `bun install` command runs `postinstall`/`prepare` hooks only for packages in `trustedDependencies`, and this blocks a class of supply-chain attacks. When a dependency fails after install, add it to that list.

- **The lockfile is a binary file that you cannot read (`bun.lockb`)** → **The lockfile is a text file (`bun.lock`) that you can read and must commit**. A new `bun install` without the binary lockfile writes `bun.lock`. Commit `bun.lock` to git for reproducible installs.

- **Flags anywhere after `bun run` configure bun, as in npm** → **Flags between `bun` and `run` configure bun**. The command form is `bun [bun-flags] run <script>`. For example, `bun run --watch dev` ignores `--watch`, but `bun --watch run dev` works.

## Agent rules

- ALWAYS use `bun install`, `bun add`, and `bun remove` to manage dependencies.
- NEVER use npm, yarn, or pnpm.
- ALWAYS commit the text lockfile `bun.lock` to git.
- ALWAYS delete a binary `bun.lockb` if one is present.
- ALWAYS place bun flags before `run`, for example `bun --watch run dev`.
- NEVER place bun flags after `run`, as in `bun run --watch dev`.
- NEVER assume that lifecycle scripts ran.
- ALWAYS add packages that need a postinstall step to `trustedDependencies`.
