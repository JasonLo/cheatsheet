# Full-feature frontend with React

_Grounded in JasonLo's repos as of 2026-06-05; current practice per the official React docs (react.dev, incl. the React 19 upgrade guide)._

## Reference snippet

```tsx
import { useState } from "react";

interface CounterProps {
  label: string;
  initial?: number;
}

// Function component, typed props, hooks. No class, no forwardRef needed (React 19).
export function Counter({ label, initial = 0, ref }: CounterProps & { ref?: React.Ref<HTMLButtonElement> }) {
  const [count, setCount] = useState(initial);     // local state
  const doubled = count * 2;                         // derived in render — not stored in state

  return (
    <button ref={ref} onClick={() => setCount((c) => c + 1)}>
      {label}: {count} (x2 = {doubled})
    </button>
  );
}
```

```tsx
// Mount with createRoot (React 18+); legacy ReactDOM.render is removed in React 19.
import { createRoot } from "react-dom/client";
createRoot(document.getElementById("root")!).render(<Counter label="Clicks" />);
```

## Typical usage patterns

- TypeScript + TSX throughout; props typed via inline object types or a `Props` interface destructured in the signature (`croissant:editor/components/tabs/frontend/src/Tabs.tsx`).
- Local UI state with `useState`, updates via functional updater `setX((x) => ...)` to avoid stale reads (`croissant:editor/components/tabs/frontend/src/Tabs.tsx`).
- Derived data computed during render rather than mirrored into extra state — e.g. building a node-tree from a flat node list each render (`croissant:editor/components/tree/frontend/src/Tree.tsx`).
- Composition via MUI primitives (`Box`, `Tabs`, `ThemeProvider`) and small presentational sub-components nested inside a container component.
- Recursive component rendering for tree-shaped data, passing the shared lookup map down as a prop.
- Styling through a theme object (`createTheme` + `ThemeProvider`) and `styled()` wrappers rather than ad-hoc inline CSS for reusable pieces.
- Embedding React as custom widgets inside a host framework (Streamlit component bridge), so each widget mounts its own root.

## Learnings

- **Class components (`extends Component` / `StreamlitComponentBase`, `render()` method)** -> **Function components + hooks.** Hooks are the unit of stateful logic and composition today; classes carry lifecycle ceremony and no longer get new React features. (seen in `croissant:editor/components/tabs/frontend/src/Tabs.tsx`, `croissant:editor/components/tree/frontend/src/Tree.tsx`)
- **`ReactDOM.render(...)` to mount** -> **`createRoot(node).render(...)`.** The mental shift is from a one-shot paint to a persistent, concurrent-capable root you create once and render into; legacy `render` is gone in React 19. (seen in `croissant:editor/components/tabs/frontend/src/index.tsx`)
- **`forwardRef` wrapper to receive a ref** -> **`ref` as an ordinary prop.** Refs are just data flowing through props now; the wrapper was an artifact of old plumbing, deprecated in React 19. (seen in `croissant:editor/components/tree/frontend/src/Tree.tsx`)
- **Seeding `useState` from a prop (`useState(selectedTab)`) and treating it as the source of truth** -> **Let the owner own the value, or fully derive it.** Copying props into state silently de-syncs when the prop changes; lift state up or compute, don't snapshot. (seen in `croissant:editor/components/tabs/frontend/src/Tabs.tsx`)
- **Reaching for `useEffect` to keep one piece of state in step with another** -> **Effects are an escape hatch for external systems only.** Anything you can compute from existing props/state should be derived during render; effects are for subscriptions, timers, network — and always with a cleanup return.
- **Rendering a mapped list without a stable `key`** -> **Give every list element a stable identity key.** Keys are React's reconciliation identity, not a lint nicety; missing/index keys corrupt state on reorder. (seen in `croissant:editor/components/tree/frontend/src/Tree.tsx`)

## Agent rules

- ALWAYS write new components as typed function components; NEVER add class components.
- ALWAYS mount with `createRoot(...).render(...)`; NEVER call `ReactDOM.render`.
- ALWAYS accept `ref` as a normal prop in new code; NEVER wrap new components in `forwardRef`.
- ALWAYS compute values you can derive from props/state during render; NEVER store derived values in extra state.
- ALWAYS reserve `useEffect` for external systems (subscriptions, timers, network) and pair it with a cleanup return; NEVER use an effect to sync internal state.
- ALWAYS lift shared state to the owner instead of copying a prop into `useState`; NEVER treat prop-seeded state as the source of truth.
- ALWAYS give mapped list elements a stable `key`; NEVER omit keys or key by array index for reorderable lists.
- ALWAYS use the functional updater form `setX((x) => ...)` when the next value depends on the previous.
