# E2E browser testing with playwright

_Grounded in JasonLo's repos as of 2026-10-22. Current practice is from playwright.dev docs._

## Reference snippet

```typescript
// playwright.config.ts — current recommended structure.
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  testMatch: /\.e2e\.ts$/,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI
    ? [["list"], ["html", { open: "never" }]]
    : "list",
  use: {
    baseURL: "http://localhost:3000",
    trace: "retain-on-failure",
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
  webServer: {
    command: "bun run start",
    url: "http://localhost:3000/api/health",
    timeout: 60_000,
    reuseExistingServer: !process.env.CI,
  },
});
```

## Typical usage patterns

- **Config with `webServer` and named projects.** Use `webServer` to start the real server before the test run. Split browser targets into named `projects` entries with `devices` to run desktop and mobile suites separately.

- **Seed state with `page.request` before navigation.** Create server-side data with `page.request.post()` before calling `page.goto()`. Use `page.addInitScript()` to set browser storage before the page loads.

- **`expect.poll()` for async server state.** Use `expect.poll(async () => ...)` when you must confirm that the server processed a change before you assert. Playwright retries the function until the assertion passes or the timeout expires.

## Learnings

- **`.spec.ts` naming** → **`.e2e.ts` naming.** When the project uses `bun test` alongside Playwright, `bun test` picks up `*.spec.ts` files automatically. Use a custom suffix such as `.e2e.ts` and set `testMatch` in `playwright.config.ts` to keep the two test runners separate.

- **`page.waitForSelector()` or `setTimeout()`** → **auto-waiting assertions.** Playwright waits for elements to be actionable before each action. Use `expect(locator).toBeVisible()` or `expect.poll()` instead of manual waits.

- **Set test state through the UI** → **seed state through the API.** Setting up data by clicking through the UI is slow and adds test interdependency. Use `page.request` helpers or server API calls to create the required state directly, then navigate to the page.

## Agent rules

- ALWAYS use a custom `testMatch` pattern such as `/\.e2e\.ts$/` when the project also uses `bun test` or Vitest.
- ALWAYS set `forbidOnly: !!process.env.CI` to prevent accidental `.only` calls from passing CI.
- ALWAYS seed test state with `page.request` or `page.addInitScript` before `page.goto()`.
- ALWAYS use semantic locators: `getByRole`, `getByLabel`, or `getByText`.
- NEVER use `page.waitForSelector`, `page.waitForTimeout`, or raw CSS selectors.
- NEVER set up test data by navigating through the UI; use the server API directly.
