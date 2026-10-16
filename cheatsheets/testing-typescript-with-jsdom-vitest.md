# Testing TypeScript with jsdom with Vitest

_Grounded in JasonLo's repos as of 2026-06-06. Current practice is from Vitest official docs (vitest.dev)._

## Reference snippet

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'node',          // default. Correct for pure logic and server code.
    include: ['src/**/*.test.{ts,tsx}'],
  },
})

// src/button.test.ts
// @vitest-environment jsdom
// Set jsdom only in a file that uses DOM APIs. Do not change the environment of the whole suite.
import { expect, test } from 'vitest'

test('renders', () => {
  document.body.innerHTML = '<button>Click</button>'
  expect(document.querySelector('button')?.textContent).toBe('Click')
})
```

## Typical usage patterns

- Import all Vitest APIs from `'vitest'`, for example `describe`, `it`, `expect`, `beforeEach`, `afterEach`, and `vi`. Without `globals: true` in the config, the imports stay visible and tsconfig needs no extra type declarations. (seen in `JasonLo/skill-cellar:src/core/**/*.test.ts`)
- Replace external dependencies with fake classes that implement the same TypeScript interface, not with module-level `vi.mock()`. For example, `FakeFetcher implements RegistryFetcher`. (seen in `JasonLo/skill-cellar:src/core/`)
- In `beforeEach`/`afterEach`, track temporary directories in a `created: string[]` array. Each `mkdtempSync` directory goes into the array, and teardown removes it with `rmSync(..., { recursive: true, force: true })`. (seen in `JasonLo/skill-cellar:src/core/fs-skills/publish.test.ts`)

## Learnings

- **Set `environment: 'jsdom'` for the whole suite** → **Scope jsdom to the files that test DOM APIs.** `environment: 'node'` is correct for logic, server, and CLI code. Even in a React project, the `// @vitest-environment jsdom` docblock adds browser globals only where a test needs them.
- **Replace a dependency with `vi.mock()`** → **Inject a fake when you own the typed interface.** Vitest hoists `vi.mock()`, and the mock replaces the module for the whole file. An injected fake is a plain object that TypeScript checks, and it exists only in its test.

## Agent rules

- ALWAYS set `environment: 'node'` in `vitest.config.ts` for suites that test pure logic.
- NEVER set a global `environment: 'jsdom'` unless every test in the suite needs browser globals.
- ALWAYS use, in each file, a `// @vitest-environment jsdom` docblock for UI component tests.
- ALWAYS import `{ describe, it, expect, vi }` from `'vitest'`.
- NEVER use implicit Vitest globals.
- ALWAYS use a fake class that implements the TypeScript interface instead of `vi.mock()` when you control that interface.
