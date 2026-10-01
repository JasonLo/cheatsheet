# LLM client (Python) with anthropic

_Grounded in JasonLo's repos as of 2026-10-01; current practice per [platform.claude.com/docs/en/about-claude/models/overview](https://platform.claude.com/docs/en/about-claude/models/overview) and anthropic-sdk-python MIGRATION.md (Aug 2026)._

## Reference snippet

```python
from anthropic import Anthropic

client = Anthropic()  # reads ANTHROPIC_API_KEY from env automatically

# One-shot call
msg = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=1024,
    system=[
        {"type": "text", "text": "You are a helpful assistant.",
         "cache_control": {"type": "ephemeral"}},
    ],
    messages=[{"role": "user", "content": "Hello"}],
)
print(msg.content[0].text)

# Streaming
with client.messages.stream(
    model="claude-opus-5-5", max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a story"}],
) as stream:
    for chunk in stream.text_stream:
        print(chunk, end="", flush=True)
```

## Typical usage patterns

- `Anthropic()` (reads `ANTHROPIC_API_KEY` from env) with `client.messages.create(model, max_tokens, system=..., messages=[...])` — always set `max_tokens` explicitly; `system=` is a top-level kwarg, not a `role: "system"` entry in the messages list (seen in `JasonLo/best-in-slot:slots/python-ai/anthropic-sdk/`)
- Prompt caching on stable system prompt: pass `system=` as a list of blocks with `cache_control: {type: ephemeral}` on the stable block; place the breakpoint at the stable/variable content boundary; track cache hits via `usage.cache_read_input_tokens` (seen in `JasonLo/best-in-slot:slots/python-ai/anthropic-sdk/CHEATSHEET.md`)
- `client.messages.stream()` context manager + `stream.text_stream` for UI-facing calls; `AsyncAnthropic` + `await client.messages.create()` for async code paths; tool use requires a `tool_result` round-trip — POST back the `tool_use_id` with results in a new user turn (seen in `JasonLo/best-in-slot:slots/python-ai/anthropic-sdk/CHEATSHEET.md`)

## Learnings

- **Model ladder updated — `claude-opus-5-5` and `claude-sonnet-5-5` are the current stable IDs** → as of Sep 2026, the `.5` suffix revision is the released form; `claude-fable-5-1` is the top-tier reasoning model (~$10/MTok out); `claude-haiku-4-5-20251001` remains current for speed/cost; retire bare `claude-opus-5`, `claude-sonnet-5`, or any 4.x references
- **SDK 1.0 removed `temperature`, `top_p`, `top_k` as first-class kwargs** → SDK 1.0+ (Aug 2026) dropped these from `messages.create()` and `messages.stream()` signatures; current models (Opus 5.5, Sonnet 5.5) do not support sampling control at all; for legacy model compatibility only, pass via `extra_body={"temperature": 0.7}` — do not add these to code targeting current models
- **Manual cache breakpoints vs. automatic** → explicit `cache_control` per block (up to 4 breakpoints) is right for stable system prompts with a hard boundary; for multi-turn conversations, pass `cache_control={"type": "ephemeral"}` at the request level and the SDK advances the breakpoint automatically — avoids manual tracking across turns

## Agent rules

- ALWAYS set `max_tokens` explicitly in every `messages.create()` call; NEVER rely on a default.
- ALWAYS pass `system=` as a top-level kwarg; NEVER use `{"role": "system", ...}` inside the `messages` list.
- ALWAYS use current model IDs (`claude-opus-5-5` for complex/agentic work, `claude-fable-5-1` for maximum reasoning capability, `claude-haiku-4-5-20251001` for cost/latency); NEVER write new code that references `claude-opus-5`, `claude-sonnet-5`, `claude-opus-4-8`, `claude-sonnet-4-6`, or any other legacy name.
- NEVER pass `temperature`, `top_p`, or `top_k` as direct kwargs to `messages.create()` or `messages.stream()`; use `extra_body={"temperature": ...}` only when targeting a legacy model that supports it.
- ALWAYS add `cache_control: {type: ephemeral}` to stable system prompt blocks when the prompt exceeds the model's minimum cacheable token threshold; NEVER skip caching for large, repeated system prompts.
- NEVER include a `role: "system"` entry in the `messages` list; NEVER skip the `tool_result` round-trip when `stop_reason == "tool_use"`.
