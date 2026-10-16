# Data apps & dashboards with Streamlit

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from Streamlit official docs (context7 `/streamlit/streamlit`, develop specs)._

## Reference snippet

```python
# app.py. Run it with: uv run streamlit run app.py
import pandas as pd
import streamlit as st

st.set_page_config(page_title="dashboard", layout="wide")
st.title("Dashboard")

@st.cache_data            # Pure function with hashable input and output. Cache the transform.
def load() -> pd.DataFrame:
    return pd.read_csv("data.csv")

@st.cache_resource        # Shared handle that is not hashable. Create it one time for each process.
def engine():
    return create_engine(DB_URL)

df = load()

# Set session_state one time. Then the keyed widget controls the value.
st.session_state.setdefault("threshold", 0)
st.slider("Threshold", 0, 100, key="threshold")

st.dataframe(df[df.value >= st.session_state.threshold], width="stretch")
st.line_chart(df.set_index("date")["value"])
```

## Typical usage patterns

- A single-file `app.py` calls `set_page_config(layout="wide")` and `st.title`, then loads, filters, and charts the data from top to bottom. Use this shape for every small dashboard. (seen in `JasonLo/best-in-slot:slots/python-web/streamlit/example/app.py`)
- `@st.cache_data` wraps the data load and transform. Then each widget interaction reruns the script at low cost. (seen in `JasonLo/best-in-slot:slots/python-web/streamlit/example/app.py`)
- `@st.cache_resource` holds expensive shared handles, for example a DB engine or a model. The app must not create these handles again or hash them. (seen in `JasonLo/best-in-slot:slots/python-web/streamlit/CHEATSHEET.md`)

## Learnings

- **The script is an event handler** → **The whole script reruns on every interaction.** Streamlit keeps state in `st.session_state`, and widgets return their current value inline. Model the app as a pure function of state.
- **Use `st.cache` to memoize anything slow** → **Choose the cache by lifetime, not by speed.** `st.cache_data` returns a safe copy of serializable data. `st.cache_resource` keeps one unhashable singleton, for example a connection.
- **Put files in `pages/` for a multipage app** → **Declare pages as objects.** `st.navigation([st.Page(...)])` creates each page as a Python object. The pages support groups, authentication checks, and dynamic lists, and they share top-level state.

## Agent rules

- ALWAYS treat a Streamlit script as code that reruns from top to bottom on every interaction.
- ALWAYS keep cross-run state in `st.session_state`.
- ALWAYS initialize session state with `st.session_state.setdefault(key, default)` or `if key not in st.session_state` before you read it.
- ALWAYS use `@st.cache_data` for serializable data and transforms.
- ALWAYS use `@st.cache_resource` for unhashable singletons, for example connections and models.
- NEVER use the bare `@st.cache` decorator.
- ALWAYS pass `width="stretch"`, `"content"`, or an int for layout sizing.
- NEVER pass `use_container_width=`.
- ALWAYS build new multipage apps with `st.navigation` and `st.Page`.
- NEVER use the old `pages/` directory for a new app.
- ALWAYS give an interactive widget a specified `key=` when the app reads its value from `st.session_state`.
- ALWAYS wrap a region that updates often or polls in `@st.fragment` to prevent full-script reruns.
- ALWAYS run the app with `uv run streamlit run app.py`.
- ALWAYS add `--server.headless=true --server.address=0.0.0.0` when the app runs in a container.
