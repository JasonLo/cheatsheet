# Data apps & dashboards with Streamlit

_Grounded in JasonLo's repos as of 2026-06-05; current practice per Streamlit official docs (context7 `/streamlit/streamlit`, develop specs)._

## Reference snippet

```python
# app.py — uv run streamlit run app.py
import pandas as pd
import streamlit as st

st.set_page_config(page_title="dashboard", layout="wide")
st.title("Dashboard")

@st.cache_data            # pure, hashable in/out — memoize the transform
def load() -> pd.DataFrame:
    return pd.read_csv("data.csv")

@st.cache_resource        # shared, unhashable handle — create once per process
def engine():
    return create_engine(DB_URL)

df = load()

# init session_state once, keyed
st.session_state.setdefault("threshold", 0)
st.session_state.threshold = st.slider("Threshold", 0, 100, key="threshold")

st.dataframe(df[df.value >= st.session_state.threshold], width="stretch")
st.line_chart(df.set_index("date")["value"])
```

## Typical usage patterns

- Single-file `app.py`: `set_page_config(layout="wide")` + `st.title`, then load → filter → chart top to bottom; reach for it on every small dashboard (`JasonLo/best-in-slot:slots/python-web/streamlit/example/app.py`).
- `@st.cache_data` wrapping the data load/transform so the script reruns cheaply on every widget interaction (same file).
- `@st.cache_resource` reserved for expensive shared handles (DB engine, model) that must not be re-created or hashed (`JasonLo/best-in-slot:slots/python-web/streamlit/CHEATSHEET.md`).

## Learnings

- **"The script is an event handler — wire a button to a callback that mutates state"** → **the whole script reruns top-to-bottom on every interaction.** State lives in `st.session_state`; widgets return their current value inline. Don't model it as a callback/event loop; model it as a pure function of state re-executed each run.
- **"Reach for `st.cache` to memoize anything slow"** → **choose by lifetime, not by speed.** `st.cache_data` for serializable data (returns a copy, safe to mutate); `st.cache_resource` for one unhashable singleton (connection/model). Bare `st.cache` is gone.
- **"Drop files in `pages/` for multipage"** → **declare pages as objects.** `st.navigation([st.Page(...)])` is the current model: pages become first-class, support grouping/auth-gating/dynamic lists, and share top-level state — the magic `pages/` directory is the legacy fallback.

## Agent rules

- ALWAYS treat a Streamlit script as re-run top-to-bottom on every interaction; keep cross-run state in `st.session_state`.
- ALWAYS initialize session state with `st.session_state.setdefault(key, default)` (or `if key not in st.session_state`) before reading it.
- ALWAYS use `@st.cache_data` for serializable data/transforms and `@st.cache_resource` for unhashable singletons (connections, models).
- NEVER use the bare `@st.cache` decorator.
- ALWAYS pass `width="stretch"` (or `"content"`/int) for layout sizing.
- NEVER pass `use_container_width=`.
- ALWAYS build new multipage apps with `st.navigation` + `st.Page`; reserve the `pages/` directory for legacy.
- ALWAYS give interactive widgets an explicit `key=` when their value is read from `st.session_state`.
- ALWAYS wrap a frequently-updating or polling region in `@st.fragment` to avoid full-script reruns.
- ALWAYS run via `uv run streamlit run app.py`; in containers add `--server.headless=true --server.address=0.0.0.0`.
