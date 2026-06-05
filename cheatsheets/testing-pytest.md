# Testing with pytest

_Grounded in JasonLo's repos as of 2026-06-05; current practice per pytest (`/websites/pytest_en_stable`) and pytest-asyncio (`/websites/pytest-asyncio_readthedocs_io_en_stable`) docs._

## Reference snippet

```python
# tests/test_widget.py
import pytest

# Sync fixture: yield = setup/teardown around the value it provides.
@pytest.fixture
def widget(tmp_path):
    w = Widget(tmp_path / "data.db")
    yield w
    w.close()

# Table-driven test: one case per row, plain assert.
@pytest.mark.parametrize(
    "value,expected",
    [(0, 0), (2, 4), (-3, 9)],
)
def test_square(value: int, expected: int) -> None:
    assert square(value) == expected

# Async test: NO @pytest.mark.asyncio needed under asyncio_mode = "auto".
async def test_fetch(widget) -> None:
    assert await widget.fetch() == 42
```

```toml
# pyproject.toml
[dependency-groups]
dev = ["pytest>=9", "pytest-asyncio>=1.3"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
addopts = "-ra"
testpaths = ["tests"]
markers = ["slow: deselect with -m 'not slow'"]
```

## Typical usage patterns

- **Table-driven tests via `@pytest.mark.parametrize`** — default reach for any pure function with many input/output rows; one row = one case, each reported separately. (`JasonLo/uw-s3:tests/test_updater.py`, `JasonLo/best-in-slot:slots/python-tooling/pytest/example/tests/test_basic.py`)
- **Plain `assert`** — never `unittest` assert methods; rely on pytest's assertion rewriting for diffs. (`JasonLo/best-in-slot:slots/python-tooling/pytest/README.md`)
- **`tests/` at repo root, `test_*.py` / `test_*` naming, package installed editable** (`uv sync`) — no `sys.path` fiddling. (`JasonLo/best-in-slot:slots/python-tooling/pytest/README.md`)
- **Async tests with `asyncio_mode = "auto"`** in `[tool.pytest.ini_options]` — write bare `async def test_*`, no marker. (`JasonLo/uw-s3:pyproject.toml`)
- **`yield` fixtures for setup/teardown**; shared fixtures in top-level `conftest.py`; scope (`function`/`module`/`session`) chosen for cost of shared state. (`JasonLo/best-in-slot:slots/python-tooling/pytest/README.md`)
- **Built-ins before mocks** — `tmp_path` + `monkeypatch` cover most needs before reaching for `unittest.mock`. (`JasonLo/best-in-slot:slots/python-tooling/pytest/README.md`)
- **`slow` marker + `-m "not slow"`** to keep the default run fast. (`JasonLo/best-in-slot:slots/python-tooling/pytest/CHEATSHEET.md`)
- **Run via `uv run pytest`** — `-x`, `--lf`, `-k` for tight feedback loops. (`JasonLo/best-in-slot:slots/python-tooling/pytest/CHEATSHEET.md`)

## Learnings

- **Marker-per-async-test → mode-level async policy.** With `asyncio_mode = "auto"` the suite declares "this is an asyncio project" once; stamping `@pytest.mark.asyncio` on every test is redundant ceremony. Decide the policy in config, not per function. (CHEATSHEET still shows `@pytest.mark.asyncio` while README/`uw-s3` use auto mode — drop the marker; seen in `JasonLo/best-in-slot:slots/python-tooling/pytest/CHEATSHEET.md`)
- **`@pytest.fixture` on `async def` → `@pytest_asyncio.fixture` (or auto mode).** An async fixture is a different lifecycle (awaited setup/teardown), not just a sync fixture that happens to be async; in strict mode it needs its own decorator, and auto mode handles it precisely because it knows the difference.
- **setup/teardown methods → `yield` fixtures.** A fixture composes by dependency injection and per-test scoping; classic `setUp`/`tearDown` couples lifecycle to a test class. Express resource lifecycle as the thing a test asks for, not as hooks it inherits.
- **Reach-for-`mock` reflex → built-in fixtures first.** `tmp_path`/`monkeypatch` are the intended seams for filesystem and environment; mocking is the fallback for genuine external boundaries, not the default.
- **Loops inside one test → parametrize.** Asserting many cases in a `for` loop hides which case failed; parametrize makes each case an independently-reported test with its own id.

## Agent rules

- ALWAYS put tests in `tests/`, name files `test_*.py` and functions `test_*`.
- ALWAYS use plain `assert`; NEVER use `unittest`-style assertion methods.
- ALWAYS set `asyncio_mode = "auto"` in `[tool.pytest.ini_options]` for asyncio projects, and write bare `async def test_*`.
- NEVER add `@pytest.mark.asyncio` when `asyncio_mode = "auto"` is set.
- ALWAYS decorate async fixtures with `@pytest_asyncio.fixture` in strict mode; NEVER mark an `async def` fixture with plain `@pytest.fixture` in strict mode.
- ALWAYS express setup/teardown as `yield` fixtures; NEVER use `setUp`/`tearDown` class methods.
- ALWAYS turn multi-case assertions into `@pytest.mark.parametrize`; NEVER loop over cases inside a single test.
- ALWAYS reach for `tmp_path` and `monkeypatch` before `unittest.mock`.
- ALWAYS install the package under test editable (`uv sync`); NEVER manipulate `sys.path` in tests or conftest.
- ALWAYS place shared fixtures in a top-level `conftest.py` and pick the widest correct fixture scope.
- ALWAYS mark expensive tests `@pytest.mark.slow` and keep the default run lean with `-m "not slow"`.
