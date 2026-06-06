# Testing TypeScript with jsdom with Vitest

_Grounded in JasonLo's repos as of 2026-06-06; current practice per Vitest official docs (vitest.dev)._

## Reference snippet

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'node',          // default; correct for pure logic / server code
    include: ['src/**/*.test.{ts,tsx}'],
  },
})
```

For a file that exercises DOM APIs, override the environment at the file level instead of switching the whole suite:

```ts
// @vitest-environment jsdom
import { expect, test } from 'vitest'

test('renders', () => {
  document.body.innerHTML = '<button>Click</button>'
  expect(document.querySelector('button')?.textContent).toBe('Click')
})
```

## Typical usage patterns

- **Named imports, no globals**: all Vitest APIs (`describe`, `it`, `expect`, `beforeEach`, `afterEach`, `vi`) imported explicitly from `'vitest'` — no `globals: true` in config, which keeps scope visible and avoids tsconfig augmentation. (seen in `JasonLo/skill-cellar:src/core/**/*.test.ts`)
- **Fake classes over `vi.mock()`**: external dependencies replaced with fake classes that implement the same TypeScript interface (e.g., `FakeFetcher implements RegistryFetcher`) rather than module-level `vi.mock()` — preserves type checking, avoids hoisting surprises, and limits the fake to the test that constructs it. (seen in `JasonLo/skill-cellar:src/core/`)
- **Filesystem fixture cleanup via tracked array**: `beforeEach`/`afterEach` maintain a `created: string[]`; each temp dir is pushed on creation via `mkdtempSync` and cleaned in teardown with `rmSync(..., { recursive: true, force: true })` — no extra library, no leaked state between tests. (seen in `JasonLo/skill-cellar:src/core/fs-skills/publish.test.ts`)

## Learnings

- **jsdom is scoped to DOM API tests, not the suite default**: Vitest's `environment: 'node'` is correct for pure logic, server, and CLI code even when the project uses React. Globally setting `environment: 'jsdom'` burdens all tests with browser-global overhead when only component tests need it; the `// @vitest-environment jsdom` per-file docblock limits jsdom to the files that actually exercise the DOM.
- **`vi.mock()` replaces modules globally; fake classes replace at the call site**: `vi.mock()` is hoisted and shadows the module for the entire file; an injected fake class is a plain object, checked by TypeScript's structural typing, and exists only in the test that creates it — prefer fakes when the dependency is a typed interface you own.

## Agent rules

- ALWAYS set `environment: 'node'` in `vitest.config.ts` for suites that test pure logic; NEVER set global `environment: 'jsdom'` unless every test in the suite needs browser globals.
- ALWAYS use a per-file `// @vitest-environment jsdom` docblock for UI component tests rather than switching the entire suite environment.
- ALWAYS import `{ describe, it, expect, vi }` explicitly from `'vitest'`; NEVER rely on implicit Vitest globals.
- ALWAYS prefer a fake class that implements the TypeScript interface over `vi.mock()` when the dependency is a typed interface you control.
