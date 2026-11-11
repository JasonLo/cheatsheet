# Multi-provider LLM routing with openrouter

_Grounded in JasonLo's repos as of 2026-11-11. Current practice is from openrouter.ai/docs._

## Reference snippet

```python
# Install: pip install openai
# OpenRouter is fully OpenAI-API-compatible.
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="sk-or-v1-...",  # read from env, never hardcode
)

# Fallback routing: OpenRouter tries each model in order on failure.
response = client.chat.completions.create(
    extra_body={
        "models": ["openai/gpt-4o", "anthropic/claude-3-5-sonnet", "google/gemini-flash-1.5"],
        "reasoning": {"effort": "low"},  # controls thinking time
    },
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": "Reply in JSON."},
        {"role": "user", "content": "..."},
    ],
)
content = response.choices[0].message.content
```

## Typical usage patterns

- **OpenAI SDK entry point.** Use the `openai` Python package with `base_url="https://openrouter.ai/api/v1"`. All existing `openai` calls work without changes.
- **Config-driven model selection.** Store the model ID in app settings and accept an optional `model` override parameter in each call. This lets you switch models at runtime.
- **JSON mode with reasoning budget.** Use `response_format={"type": "json_object"}` to get structured JSON output. Set `"reasoning": {"effort": "low"}` for calls that need fast answers.

## Learnings

- **Raw HTTP client** → **OpenAI SDK with custom `base_url`.** OpenRouter is fully OpenAI-API-compatible, so use `OpenAI(base_url="https://openrouter.ai/api/v1")` to connect to it directly. You get streaming, retries, and type hints without custom code.
- **Single hardcoded model** → **Fallback model list.** A single hardcoded model makes your app dependent on one provider. Use `extra_body={"models": [...]}` with two or more models to let OpenRouter route to the next one on failure.
- **`:thinking` model suffix** → **`reasoning` effort parameter.** The `:thinking` model-name suffix is deprecated. Use `"reasoning": {"effort": "low|medium|high|max|none"}` for precise thinking-budget control.

## Agent rules

- ALWAYS use the `openai` SDK with `base_url="https://openrouter.ai/api/v1"` instead of raw HTTP calls to OpenRouter.
- ALWAYS pass `extra_body={"models": [...]}` with two or more models when resilience matters.
- ALWAYS read the API key from an environment variable or secret store, not from code.
- NEVER hardcode a model ID; read it from app configuration.
- NEVER use the `:thinking` model-name suffix; use `"reasoning": {"effort": "..."}` instead.
- ALWAYS check for `null` content in the API response before parsing JSON.
