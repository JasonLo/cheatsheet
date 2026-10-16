# LLM client (Python) with anthropic

_Grounded in JasonLo's repos as of 2026-10-01. Current practice is from [platform.claude.com/docs/en/about-claude/models/overview](https://platform.claude.com/docs/en/about-claude/models/overview) and the anthropic-sdk-python MIGRATION.md (Aug 2026)._

## Reference snippet

```python
from anthropic import Anthropic

client = Anthropic()  # Reads ANTHROPIC_API_KEY from the environment automatically

# Single call
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

# Stream the response
with client.messages.stream(
    model="claude-opus-5-5", max_tokens=1024,
    messages=[{"role": "user", "content": "Tell me a story"}],
) as stream:
    for chunk in stream.text_stream:
        print(chunk, end="", flush=True)
```

## Typical usage patterns

- **Basic call.** The client `Anthropic()` reads `ANTHROPIC_API_KEY` from the environment, and `client.messages.create(model, max_tokens, system=..., messages=[...])` sends the request. The `system=` argument is top-level, not a `role: "system"` entry in the messages list. (seen in `JasonLo/best-in-slot:slots/python-ai/anthropic-sdk/`)
- **Prompt caching on a stable system prompt.** Pass `system=` as a list of blocks with `cache_control: {type: ephemeral}` on the stable block. Check cache hits with `usage.cache_read_input_tokens`. (seen in `JasonLo/best-in-slot:slots/python-ai/anthropic-sdk/CHEATSHEET.md`)
- **Streaming, async, and tools.** UI calls use the `client.messages.stream()` context manager with `stream.text_stream`, and async code uses `AsyncAnthropic`. For tool use, send each result with its `tool_use_id` in a new user turn. (seen in `JasonLo/best-in-slot:slots/python-ai/anthropic-sdk/CHEATSHEET.md`)

## Learnings

- **A hard-coded model ID stays correct** → **Select the model from the current models list**. Model IDs become old when Anthropic releases a new revision. Update old IDs in new and existing code to a model of the correct task tier.
- **You control the output with sampling arguments** → **Current models have no sampling control**. SDK 1.0 removed `temperature`, `top_p`, and `top_k` from `messages.create()` and `messages.stream()`. Use `extra_body={"temperature": ...}` only for an old model that supports it.
- **A cache breakpoint is a fixed marker that you place one time** → **The cache boundary moves with the conversation**. For a multi-turn conversation, request-level `cache_control={"type": "ephemeral"}` moves the breakpoint forward automatically. Use breakpoints on single blocks only for a stable prompt with a fixed boundary.

## Agent rules

- ALWAYS set `max_tokens` in every `messages.create()` call.
- NEVER expect a default value for `max_tokens`.
- ALWAYS pass `system=` as a top-level argument.
- NEVER put a `{"role": "system", ...}` entry inside the `messages` list.
- ALWAYS use current model IDs: `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-fable-5-1`, or `claude-haiku-4-5-20251001`.
- NEVER write new code that uses old model IDs, for example `claude-opus-5`, `claude-sonnet-5`, or `claude-opus-4-8`.
- NEVER pass `temperature`, `top_p`, or `top_k` as direct arguments to `messages.create()` or `messages.stream()`.
- ALWAYS add `cache_control: {type: ephemeral}` to a stable system prompt that is above the minimum cacheable size.
- NEVER skip the `tool_result` message when `stop_reason == "tool_use"`.
