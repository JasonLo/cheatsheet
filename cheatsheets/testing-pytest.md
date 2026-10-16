# Testing with pytest

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from pytest (`/websites/pytest_en_stable`) and pytest-asyncio (`/websites/pytest-asyncio_readthedocs_io_en_stable`) docs._

## Reference snippet

```python
# tests/test_widget.py
import pytest

# Sync fixture: code before yield is setup. Code after yield is teardown.
@pytest.fixture
def widget(tmp_path):
    w = Widget(tmp_path / "data.db")
    yield w
    w.close()

# Table-driven test: one case for each row, with a plain assert.
@pytest.mark.parametrize(
    "value,expected",
    [(0, 0), (2, 4), (-3, 9)],
)
def test_square(value: int, expected: int) -> None:
    assert square(value) == expected

# Async test: with asyncio_mode = "auto", you do not need @pytest.mark.asyncio.
async def test_fetch(widget) -> None:
    assert await widget.fetch() == 42
```

## Typical usage patterns

- **Table-driven tests with `@pytest.mark.parametrize`.** Use it for a pure function with many input and output rows. Each row is one case, and pytest reports each case separately. (seen in `JasonLo/uw-s3:tests/test_updater.py`, `JasonLo/best-in-slot:slots/python-tooling/pytest/example/tests/test_basic.py`)
- **Async tests with `asyncio_mode = "auto"`.** With `pytest-asyncio` in the dev group and this mode in `[tool.pytest.ini_options]`, bare `async def test_*` functions need no marker. (seen in `JasonLo/uw-s3:pyproject.toml`)
- **`yield` fixtures for setup and teardown.** Put shared fixtures in a top-level `conftest.py`. Choose the `function`, `module`, or `session` scope by the cost of the shared state. (seen in `JasonLo/best-in-slot:slots/python-tooling/pytest/README.md`)

## Learnings

- **Each async test declares that it is async** → **The project declares its async policy one time in configuration**. With `asyncio_mode = "auto"`, `@pytest.mark.asyncio` on each test is unnecessary. (seen in `JasonLo/best-in-slot:slots/python-tooling/pytest/CHEATSHEET.md`)
- **An async fixture is a sync fixture with `async def`** → **An async fixture has a different lifecycle**. pytest awaits its setup and teardown. In strict mode it needs `@pytest_asyncio.fixture`, and auto mode handles it for you.
- **A test inherits setup and teardown hooks** → **A test asks for the resources that it needs**. A `yield` fixture works by dependency injection and has its own scope. Classic `setUp`/`tearDown` methods put the lifecycle in a test class.

## Agent rules

- ALWAYS put tests in `tests/`, with file names `test_*.py` and function names `test_*`.
- ALWAYS use plain `assert`.
- NEVER use `unittest`-style assertion methods.
- ALWAYS set `asyncio_mode = "auto"` in `[tool.pytest.ini_options]` for asyncio projects.
- ALWAYS write bare `async def test_*` functions when you set auto mode.
- NEVER add `@pytest.mark.asyncio` when the config sets `asyncio_mode = "auto"`.
- ALWAYS decorate async fixtures with `@pytest_asyncio.fixture` in strict mode.
- NEVER mark an `async def` fixture with plain `@pytest.fixture` in strict mode.
- ALWAYS write setup and teardown as `yield` fixtures.
- NEVER use `setUp`/`tearDown` class methods.
- ALWAYS write assertions for many cases as `@pytest.mark.parametrize` rows.
- NEVER use a loop of cases inside a single test.
- ALWAYS try `tmp_path` and `monkeypatch` before `unittest.mock`.
- ALWAYS install the package under test in editable mode with `uv sync`.
- NEVER change `sys.path` in tests or conftest.
- ALWAYS put shared fixtures in a top-level `conftest.py`.
- ALWAYS choose the widest correct fixture scope.
- ALWAYS mark expensive tests with `@pytest.mark.slow`.
- ALWAYS register custom markers, for example `slow`, in `markers` under `[tool.pytest.ini_options]`.
- ALWAYS keep the default run small with `-m "not slow"`.
