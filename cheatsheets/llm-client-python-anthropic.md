# LLM client (Python) with anthropic

_Grounded in JasonLo's repos as of 2026-07-03; current practice per [platform.claude.com/docs](https://platform.claude.com/docs/en/api/sdks/python)._

## Reference snippet

```python
from anthropic import Anthropic

client = Anthropic()  # reads ANTHROPIC_API_KEY from env automatically

# One-shot call
msg = client.messages.create(
    model="claude-opus-4-8",
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
    model="claude-opus-4-8", max_tokens=1024,
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

- **Model ladder is outdated** → the prior hierarchy (`claude-sonnet-4-6` default / `claude-opus-4-7` max / `claude-haiku-4-5-20251001` cheap) has been superseded; current recommended hierarchy: `claude-opus-4-8` (complex/agentic default), `claude-fable-5` (max capability), `claude-haiku-4-5` (latency/cost) — migrate model IDs in new and existing code
- **New tokenizer in Opus 4.7+ produces ~30% more tokens for the same text** → recalibrate `max_tokens` values, context window budgets, and cost estimates when upgrading to any model from the 4.7+ generation; the same prompt costs more tokens than before
- **Manual cache breakpoints vs. automatic** → explicit `cache_control` per block (up to 4 breakpoints) is right for stable system prompts with a hard boundary; for multi-turn conversations, pass `cache_control={"type": "ephemeral"}` at the request level and the SDK advances the breakpoint automatically — avoids manual tracking across turns

## Agent rules

- ALWAYS set `max_tokens` explicitly in every `messages.create()` call; NEVER rely on a default.
- ALWAYS pass `system=` as a top-level kwarg; NEVER use `{"role": "system", ...}` inside the `messages` list.
- ALWAYS use current model IDs (`claude-opus-4-8`, `claude-fable-5`, `claude-haiku-4-5`); NEVER write new code that references legacy names like `claude-sonnet-4-6` or `claude-opus-4-7`.
- ALWAYS add `cache_control: {type: ephemeral}` to stable system prompt blocks when the prompt exceeds the model's minimum cacheable token threshold; NEVER skip caching for large, repeated system prompts.
- NEVER include a `role: "system"` entry in the `messages` list; NEVER skip the `tool_result` round-trip when `stop_reason == "tool_use"`.
