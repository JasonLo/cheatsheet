# TUI applications in TypeScript with opentui

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from opentui.com/docs._

## Reference snippet

```tsx
// tsconfig.json: "jsx": "react-jsx", "jsxImportSource": "@opentui/react"
import { createCliRenderer } from '@opentui/core'
import { createRoot, useKeyboard } from '@opentui/react'

async function main() {
  const renderer = await createCliRenderer({ exitOnCtrlC: true, targetFps: 30 })
  createRoot(renderer).render(<App />)
  // to exit from code, call renderer.destroy() in SIGINT and SIGTERM handlers
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

- **Multi-screen navigation with tab state**. The top-level `App` keeps a `tab` state enum and renders each screen as a separate React component. A `useKeyboard` hook on the root handles number keys and Tab/Shift-Tab, so the app needs no router library. (seen in `JasonLo/skill-cellar:src/App.tsx`)

- **Keyboard-first UX with `useKeyboard`**. Attach `useKeyboard((e) => {...})` in any component. Key names are lowercase strings, for example `'up'`, `'down'`, `'return'`, `'space'`, and `'tab'`, and the modifier booleans `e.shift`, `e.ctrl`, and `e.meta` are always present. (seen in `JasonLo/skill-cellar:src/App.tsx`, `src/screens/Market.tsx`)

- **Scrollable list that follows the selection**. The list is in a `<scrollbox ref={listRef} scrollY>`, and each row has an `id` prop. In a `useEffect` on the selection index, call `listRef.current?.scrollChildIntoView(`row-${selected}`)` to keep the selected row visible. (seen in `JasonLo/skill-cellar:src/screens/Library.tsx`)

## Learnings

- **Write React for DOM elements** → **Write React for terminal primitives**. Layout uses `<box>` instead of `<div>`, and inline content goes in `<span>` inside `<text>`. Flexbox props, for example `flexDirection`, `width`, `padding`, and `gap`, go on `<box>`, and colors go on `fg`/`bg` props because there is no `style` object.

- **Read keys from browser events or `process.stdin`** → **Read keys with the `useKeyboard` hook**. The `useKeyboard` hook connects to the Zig render loop of OpenTUI, so input is synchronous with each frame. Hooks on the root handle global shortcuts, and hooks on each screen handle local ones without conflict.

- **The process exit restores the terminal** → **The app must release raw mode**. Without `renderer.destroy()`, the terminal stays in raw mode after exit with a broken cursor and no echo. The `exitOnCtrlC: true` option handles Ctrl-C, but `process.exit()` calls and signal handlers must call `renderer.destroy()`.

## Agent rules

- ALWAYS set `"jsxImportSource": "@opentui/react"` in tsconfig when you use @opentui/react.
- ALWAYS use `<box>`, `<text>`, and `<scrollbox>` for terminal layout and content.
- NEVER use `<div>`, `<ul>`, or a `<span>` outside a `<text>`.
- ALWAYS use `useKeyboard` for terminal input.
- NEVER read input from `process.stdin` or `readline` directly.
- ALWAYS call `renderer.destroy()` in SIGINT/SIGTERM handlers and programmatic exit paths.
