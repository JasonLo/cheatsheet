# Typed config loading with pydantic-settings

_Grounded in JasonLo's repos as of 2026-06-05; current practice per pydantic-settings official docs (context7 `/pydantic/pydantic-settings`)._

## Reference snippet

```python
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MYAPP_",
        env_nested_delimiter="__",   # MYAPP_DB__URL -> db.url
        extra="ignore",
    )

    # Required: no default -> a missing value is a load-time ValidationError.
    api_key: SecretStr
    db_url: str = "sqlite:///./app.db"
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()  # one validated, cached instance per process
```

Default source priority (highest wins): **constructor args > env vars > `.env` > secrets dir**. Reorder by overriding `settings_customise_sources`; add file sources (`YamlConfigSettingsSource`, `Toml…`, `Json…`) there rather than loading them by hand.

## Typical usage patterns

- **One `Settings(BaseSettings)` + `SettingsConfigDict(env_file, env_prefix, extra="ignore")`** — the config contract is the typed class; loading is just `Settings()`. Reach for it for any service/CLI that reads env + `.env`. (seen in `JasonLo/best-in-slot:slots/python-web/pydantic-settings/example/pydantic_settings_example/__init__.py`)
- **`@lru_cache def get_settings()`** — settings are validated once and reused, not re-parsed per call site. Pairs with FastAPI `Depends(get_settings)` so handlers receive the singleton and tests can swap it. (seen in `JasonLo/best-in-slot:slots/python-web/pydantic-settings/CHEATSHEET.md`)
- **Nested config via `env_nested_delimiter="__"`** — group related keys under a sub-model (`db.url`, `db.pool_size`) fed by `MYAPP_DB__URL`. Reach for it when flat env names get noisy. (seen in `JasonLo/best-in-slot:slots/python-web/pydantic-settings/CHEATSHEET.md`)
- **Tests pin the source with `Settings(_env_file=None)` + `monkeypatch.setenv(...)`** — disable `.env` discovery and drive values through env so tests don't depend on a developer's local file; clear `get_settings.cache_clear()` between cases. (seen in `JasonLo/best-in-slot:slots/python-web/pydantic-settings/example/tests/test_settings.py`)
- **Layered loader: secrets from `.env`/env, everything else from a YAML file** — a single `BaseSettings` class holds both credential fields and tunables, with the YAML providing the non-secret values at load. The intent is "credentials never live in the versioned file." (seen in a private eval-harness config; conveyed generically per P-7)

## Learnings

- **"`BaseSettings` lives in `pydantic`"** → **"It's a separate package now."** In pydantic v2 the settings machinery was split out into `pydantic-settings`; import `BaseSettings`/`SettingsConfigDict` from `pydantic_settings`, declare it as its own dependency. The mental shift: config-loading is an opt-in companion library, not part of core validation.
- **"Configure settings with an inner `class Config`"** → **"`model_config = SettingsConfigDict(...)`."** Same as core pydantic v2 — settings knobs (`env_file`, `env_prefix`, `secrets_dir`, `env_nested_delimiter`) are a typed config object, not a nested class.
- **"Load the YAML myself and splat it in: `Config(**yaml_dict)`"** → **"Register YAML as a ranked source via `settings_customise_sources`."** Hand-loading a file and passing it as constructor args quietly promotes file values to the *highest* precedence (init args win over env), inverting the usual "env overrides file" expectation. A `YamlConfigSettingsSource` slots the file into the priority chain where it belongs, so env vars still override it. (seen in a private eval-harness config)
- **"Enforce a required credential in `model_post_init` with a manual `raise`"** → **"Make the field required; let validation report it."** A field given `= ""` plus a post-init check reimplements what the type system already does: drop the default and a missing value surfaces as a `ValidationError` at `Settings()` with the field name, no bespoke message plumbing. Reserve `model_post_init` for cross-field derivation. (seen in a private eval-harness config)
- **"Secrets are plain `str` fields"** → **"Type them `SecretStr`."** A `str` API key prints in logs, tracebacks, and `repr`/`model_dump` by accident; `SecretStr` masks it everywhere and forces an explicit `.get_secret_value()` at the point of use. The intent — "this value must not leak" — becomes part of the type. (general best practice; user repos currently use plain `str`)
- **"Each call site builds its own `Settings()`"** → **"Build once, inject the singleton."** Re-instantiating re-reads files/env and re-validates on every use, and makes test overrides fragile. A cached factory (`@lru_cache`) makes settings a single validated value you depend on; the user's public slot already does this and is the pattern to copy.

## Agent rules

- ALWAYS import `BaseSettings`/`SettingsConfigDict` from `pydantic_settings`, and declare `pydantic-settings` as an explicit dependency — NEVER from `pydantic`.
- ALWAYS configure via `model_config = SettingsConfigDict(...)` — NEVER an inner `class Config`.
- ALWAYS add file sources (YAML/TOML/JSON) through `settings_customise_sources` with `YamlConfigSettingsSource`/etc. — NEVER hand-load a file and pass it as `Settings(**data)`, which forces file values to top precedence.
- ALWAYS make a required setting a field with no default so a missing value is a load-time `ValidationError` — NEVER default it to `""`/`None` and re-check it in `model_post_init`.
- ALWAYS type secrets as `SecretStr` and read them with `.get_secret_value()` — NEVER a plain `str` for credentials.
- ALWAYS expose settings through one cached factory (`@lru_cache def get_settings()`) and inject it (e.g. FastAPI `Depends(get_settings)`) — NEVER construct `Settings()` at each call site.
- ALWAYS model grouped keys as sub-models with `env_nested_delimiter="__"` instead of many flat prefixed names.
- ALWAYS keep secrets in `.env`/env/secrets-dir and non-secret config in a committed file; rely on the documented priority (init > env > `.env` > secrets) instead of reordering it implicitly.
- ALWAYS make tests source-deterministic with `Settings(_env_file=None)` + `monkeypatch.setenv(...)` and clear the cache between cases — NEVER let tests read a developer's local `.env`.
