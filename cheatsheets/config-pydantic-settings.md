# Typed config loading with pydantic-settings

_Grounded in JasonLo's repos as of 2026-06-05. Current practice is from pydantic-settings official docs (context7 `/pydantic/pydantic-settings`)._

## Reference snippet

```python
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MYAPP_",
        env_nested_delimiter="__",   # MYAPP_DB__URL sets db.url
        extra="ignore",
    )

    # Required. There is no default. A missing value causes a ValidationError at load time.
    api_key: SecretStr
    db_url: str = "sqlite:///./app.db"
    debug: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()  # One validated and cached instance for each process
```

## Typical usage patterns

- **One `Settings(BaseSettings)` + `SettingsConfigDict(env_file, env_prefix, extra="ignore")`.** The typed class defines the config, and `Settings()` loads it. Use it for any service or CLI that reads the environment and `.env`. (seen in `JasonLo/best-in-slot:slots/python-web/pydantic-settings/example/pydantic_settings_example/__init__.py`)
- **`@lru_cache def get_settings()`.** The app validates the settings one time and then uses the same instance again. FastAPI `Depends(get_settings)` gives this instance to handlers, and tests can replace it. (seen in `JasonLo/best-in-slot:slots/python-web/pydantic-settings/CHEATSHEET.md`)
- **Nested config with `env_nested_delimiter="__"`.** Put related keys, for example `db.url` and `db.pool_size`, in a sub-model that `MYAPP_DB__URL` fills. Use it when flat env names become hard to read. (seen in `JasonLo/best-in-slot:slots/python-web/pydantic-settings/CHEATSHEET.md`)

## Learnings

- **Config loading is part of core pydantic** → **Config loading is a separate, optional library.** Import `BaseSettings` and `SettingsConfigDict` from `pydantic_settings`. Declare `pydantic-settings` as its own dependency.
- **Code loads the YAML by hand and passes it as `Config(**yaml_dict)`** → **Rank each file as a source.** Values that you load by hand become constructor args, and they override env vars. A `YamlConfigSettingsSource` in `settings_customise_sources` puts the file at the correct rank, and env vars still override it. (seen in a private eval-harness config)
- **Secrets are plain `str` fields** → **A secret has a type that keeps the value secret.** A `str` API key can show in logs, tracebacks, `repr`, and `model_dump`. The `SecretStr` type masks the value everywhere and requires `.get_secret_value()` at the point of use.

## Agent rules

- ALWAYS import `BaseSettings` and `SettingsConfigDict` from `pydantic_settings`.
- NEVER import `BaseSettings` from `pydantic`.
- ALWAYS declare `pydantic-settings` as its own dependency.
- ALWAYS configure settings with `model_config = SettingsConfigDict(...)`.
- NEVER configure settings with an inner `class Config`.
- ALWAYS add YAML, TOML, or JSON file sources through `settings_customise_sources` with `YamlConfigSettingsSource` or a similar source.
- NEVER load a file by hand and pass it as `Settings(**data)`.
- ALWAYS give a required setting no default.
- NEVER give a required setting a `""` or `None` default and check it again in `model_post_init`.
- ALWAYS type secrets as `SecretStr`.
- ALWAYS read a secret value with `.get_secret_value()`.
- NEVER use a plain `str` for credentials.
- ALWAYS expose settings through one cached factory, `@lru_cache def get_settings()`.
- ALWAYS inject the settings factory, for example with FastAPI `Depends(get_settings)`.
- NEVER construct `Settings()` at each call site.
- ALWAYS model grouped keys as sub-models with `env_nested_delimiter="__"`, not as many flat prefixed names.
- ALWAYS keep secrets in `.env`, in env vars, or in the secrets directory.
- ALWAYS keep non-secret config in a committed file.
- ALWAYS use the documented source priority: init > env > `.env` > secrets.
- NEVER change the source order implicitly.
- ALWAYS make test sources deterministic with `Settings(_env_file=None)` and `monkeypatch.setenv(...)`.
- ALWAYS clear the settings cache between test cases.
- NEVER let tests read the local `.env` file of a developer.
