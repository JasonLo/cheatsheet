# Full-feature frontend with React

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from the official React docs (react.dev, including the React 19 upgrade guide)._

## Reference snippet

```tsx
// src/Counter.tsx
import { useState, type Ref } from "react";

interface CounterProps {
  label: string;
  initial?: number;
  ref?: Ref<HTMLButtonElement>;                     // React 19: ref is a normal prop. Do not use forwardRef.
}

// Function component with typed props and hooks. Do not use a class.
export function Counter({ label, initial = 0, ref }: CounterProps) {
  const [count, setCount] = useState(initial);     // Local state
  const doubled = count * 2;                         // Calculate this in render. Do not keep it in state.

  return (
    <button ref={ref} onClick={() => setCount((c) => c + 1)}>
      {label}: {count} (x2 = {doubled})
    </button>
  );
}

// src/main.tsx: mount with createRoot. React 19 removes the old ReactDOM.render.
import { createRoot } from "react-dom/client";
import { Counter } from "./Counter";

createRoot(document.getElementById("root")!).render(<Counter label="Clicks" />);
```

## Typical usage patterns

- The components use TypeScript and TSX everywhere. Each signature destructures props that have an inline object type or a `Props` interface. (seen in `JasonLo/croissant:editor/components/tabs/frontend/src/Tabs.tsx`)
- Components keep local UI state in `useState`. Updates use the functional updater `setX((x) => ...)`, which prevents reads of old values. (seen in `JasonLo/croissant:editor/components/tabs/frontend/src/Tabs.tsx`)
- Components build complex view data during render from flat props. For example, the tree component builds a node tree from a flat node list on each render. (seen in `JasonLo/croissant:editor/components/tree/frontend/src/Tree.tsx`)

## Learnings

- **Class components (`extends Component` / `StreamlitComponentBase`, `render()` method)** → **Function components and hooks.** Hooks are the current unit of stateful logic and composition. Classes need more lifecycle code and get no new React features. (seen in `JasonLo/croissant:editor/components/tabs/frontend/src/Tabs.tsx`, `croissant:editor/components/tree/frontend/src/Tree.tsx`)
- **Mount as a single render with `ReactDOM.render(...)`** → **Create one persistent root and render into it.** The `createRoot(node).render(...)` root supports concurrent rendering. React 19 removed the old `render`. (seen in `JasonLo/croissant:editor/components/tabs/frontend/src/index.tsx`)
- **Use `useEffect` to sync one state with another** → **Effects are only for external systems.** Calculate values from props and state during render. Use effects with a cleanup function for subscriptions, timers, and network calls.

## Agent rules

- ALWAYS write new components as typed function components.
- NEVER add class components.
- ALWAYS mount with `createRoot(...).render(...)`.
- NEVER call `ReactDOM.render`.
- ALWAYS accept `ref` as a normal prop in new code.
- NEVER wrap new components in `forwardRef`.
- ALWAYS compute during render the values that you can calculate from props or state.
- NEVER store calculated values in extra state.
- ALWAYS use `useEffect` only for external systems, for example subscriptions, timers, and network calls.
- ALWAYS return a cleanup function from each `useEffect`.
- NEVER use an effect to synchronize internal state.
- ALWAYS move shared state to the owner component instead of copying a prop into `useState`.
- NEVER expect state that a prop initializes to follow later changes of that prop.
- ALWAYS give mapped list elements a stable `key`.
- NEVER leave out keys on mapped list elements.
- NEVER use the array index as the key for lists that can change order.
- ALWAYS use the functional updater form `setX((x) => ...)` when the next value depends on the previous value.
