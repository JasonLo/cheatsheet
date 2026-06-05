# LLM API clients with the OpenAI SDK

_Grounded in JasonLo's repos as of 2026-06-05; current practice per the openai-python README + helpers.md (context7 `/openai/openai-python`)._

## Reference snippet

```python
import asyncio
import os

from openai import AsyncOpenAI, OpenAI
from pydantic import BaseModel

# Key is read from OPENAI_API_KEY automatically; pass base_url for
# OpenAI-compatible backends (vLLM, DashScope, Ollama, local gateways).
client = OpenAI()  # api_key=os.environ["OPENAI_API_KEY"] implied

# --- current default: Responses API ---
resp = client.responses.create(
    model="gpt-5.5",
    instructions="You are concise.",
    input="One-line summary of the OpenAI Python SDK.",
)
print(resp.output_text)

# --- structured output: pass a Pydantic model, get a typed object back ---
class Summary(BaseModel):
    title: str
    bullets: list[str]

parsed = client.responses.parse(
    model="gpt-5.5",
    input="Summarize transformers.",
    text_format=Summary,
)
summary: Summary = parsed.output_parsed   # validated, no manual json.loads

# --- async + concurrency: AsyncOpenAI + asyncio.gather, not threads ---
aclient = AsyncOpenAI()

async def ask(q: str) -> str:
    r = await aclient.responses.create(model="gpt-5.5", input=q)
    return r.output_text

async def main() -> None:
    answers = await asyncio.gather(*(ask(q) for q in ["a?", "b?", "c?"]))

asyncio.run(main())
```

## Typical usage patterns

_All Python OpenAI-SDK usage mined lives in private repos, so patterns below are described generically with no repo cites (P-7)._

- **Cached lazy client singleton** — module-global `_client`, built once inside a `_get_client()` helper (thread-locked for the sync `OpenAI`), reused across calls. Reach for it so config is read once and the HTTP pool is shared.
- **Config from env, not literals** — `api_key`, `base_url`, and model name pulled from environment (`OPENAI_API_KEY` and project-specific vars); `base_url=... or None` lets the same code hit OpenAI proper or a self-hosted OpenAI-compatible endpoint.
- **`AsyncOpenAI` for eval/throughput backends** — async client constructed with explicit `timeout` and `max_retries`; calls use `await client.chat.completions.create(...)`. Used where many model calls fan out.

## Learnings

- **Module-level `openai.api_key` + `openai.ChatCompletion.create`** → **instantiate an `OpenAI()`/`AsyncOpenAI()` client.** The pre-v1 module-global API is gone in v1+; state (key, base_url, org, retries, timeout) now lives on a client object you construct and pass around, not on the `openai` module.
- **JSON mode + manual `json.loads` + hand-rolled validation** → **`responses.parse()` / `chat.completions.parse()` with a Pydantic model.** Intent shifted from "ask for JSON, then defensively parse and re-check shape" to "declare the schema once and get a validated typed object (`output_parsed`)"; the SDK derives the JSON schema and enforces it.
- **Chat Completions as the default surface** → **Responses API is the current default.** The SDK now leads with `client.responses.create`; treat Chat Completions as the previous standard. New work starts on Responses (`input`/`instructions`/`output_text`); migrate when touching old call sites, not blindly.

## Agent rules

- ALWAYS instantiate an `OpenAI()` or `AsyncOpenAI()` client; pass it around explicitly.
- NEVER use `openai.api_key`, `openai.organization`, or `openai.ChatCompletion.*` (pre-v1 module API).
- ALWAYS let the client read the key from `OPENAI_API_KEY` (env/`.env`); pass `api_key`/`base_url` from environment variables.
- NEVER hard-code an API key or store it on a module global; never commit a real key.
- ALWAYS use `responses.parse()` / `chat.completions.parse()` with a Pydantic `text_format`/`response_format` for structured output; read `.output_parsed`.
- NEVER request `{"type": "json_object"}` and then `json.loads` + hand-validate when a Pydantic schema will do.
- ALWAYS reach for the Responses API (`client.responses.create`) on new code; treat Chat Completions as legacy-but-supported.
- ALWAYS use `AsyncOpenAI` with `asyncio.gather` for concurrent calls; NEVER wrap the sync client in a `ThreadPoolExecutor` for parallelism.
- ALWAYS build the client once (cached/lazy singleton) and reuse it; set `timeout` and `max_retries` on construction.
- ALWAYS set `base_url` from config to target OpenAI-compatible backends instead of forking the client code.
