# TUI applications in TypeScript with opentui

_Grounded in JasonLo's repos as of 2026-06-05; current practice per opentui.com/docs._

## Reference snippet

```tsx
// tsconfig.json: "jsx": "react-jsx", "jsxImportSource": "@opentui/react"
import { createCliRenderer } from '@opentui/core'
import { createRoot, useKeyboard } from '@opentui/react'

async function main() {
  const renderer = await createCliRenderer({ exitOnCtrlC: true, targetFps: 30 })
  createRoot(renderer).render(<App />)
  // call renderer.destroy() in SIGINT/SIGTERM handlers for programmatic exit
}
main().catch((e) => { console.error(e); process.exit(1) })

function App() {
  useKeyboard((e) => {
    if (e.name === 'q' && !e.ctrl && !e.meta) process.exit(0)
  })
  return (
    <box flexDirection="column" width="100%" height="100%">
      <text fg="#7fd17f">Hello, terminal!</text>
    </box>
  )
}
```

## Typical usage patterns

- **Multi-screen navigation with tab state** — top-level `App` holds a `tab` state enum; each screen is a separate React component rendered conditionally. `useKeyboard` on the root handles number-key jumps and Tab/Shift-Tab cycling. No router or navigation library needed. (JasonLo/skill-cellar:src/App.tsx)

- **Keyboard-first UX via `useKeyboard`** — attach `useKeyboard((e) => {...})` in any component; key names are lowercase strings (`'up'`, `'down'`, `'return'`, `'space'`, `'tab'`). Modifier booleans `e.shift`, `e.ctrl`, `e.meta` are always present. Multiple hooks across the component tree coexist safely. (JasonLo/skill-cellar:src/App.tsx, src/screens/Market.tsx)

- **Scrollable list with programmatic scroll tracking** — wrap the list in `<scrollbox ref={listRef} scrollY>` and assign each row an `id` prop; call `listRef.current?.scrollChildIntoView(`row-${selected}`)` in a `useEffect` on the selection index to keep the highlighted row visible as keyboard selection moves. (JasonLo/skill-cellar:src/screens/Library.tsx)

## Learnings

- **React DOM primitives → OpenTUI terminal primitives.** `<div>` → `<box>`, inline content → `<span>` inside `<text>`, `<ul><li>` → looped `<box>` rows. Flexbox props (`flexDirection`, `width`, `padding`, `gap`) work the same but belong on `<box>`, not `<div>`. Colors go on `fg`/`bg` props (hex `#rrggbb` or CSS name) — there is no `style` object.

- **Browser keyboard events → `useKeyboard` hook.** Don't wire `process.stdin` or `readline` directly; `useKeyboard` integrates with OpenTUI's Zig render loop so input is frame-synchronous and composable. Attach it at multiple component levels — root for global shortcuts, each screen for local ones — without conflict.

- **OpenTUI holds terminal raw mode → explicit cleanup on exit.** Without `renderer.destroy()`, the terminal stays in raw mode after the process ends (broken cursor, no echo). `exitOnCtrlC: true` in `createCliRenderer` covers Ctrl-C, but not `process.exit()` calls or signal handlers — add `renderer.destroy()` there explicitly.

## Agent rules

- ALWAYS set `"jsxImportSource": "@opentui/react"` in tsconfig when using @opentui/react
- ALWAYS use `<box>` / `<text>` / `<scrollbox>` — NEVER `<div>` / `<span>` / `<ul>`
- ALWAYS use `useKeyboard` for terminal input — NEVER wire `process.stdin` or `readline` directly
- ALWAYS call `renderer.destroy()` in SIGINT/SIGTERM handlers and programmatic exit paths
