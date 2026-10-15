# Converting scraped web content to markdown for LLM pipelines with markitdown

_Grounded in JasonLo's repos as of 2026-10-15; current practice per markitdown v0.1.8 (microsoft/markitdown)._

## Reference snippet

```python
import io
from markitdown import MarkItDown, StreamInfo  # StreamInfo is now public

_md = MarkItDown()  # module-level singleton; reuse across all calls

def to_markdown(html_bytes: bytes, url: str) -> str:
    info = StreamInfo(mimetype="text/html", url=url)
    result = _md.convert_stream(io.BytesIO(html_bytes), stream_info=info)
    return result.markdown  # not .text_content (soft-deprecated)
```

## Typical usage patterns

- **Singleton + `convert_stream` for pipelines.** Instantiate `MarkItDown()` once at module level; pass raw HTML/PDF bytes as `io.BytesIO` with a `StreamInfo` that carries mimetype, extension, and URL — markitdown uses these for format detection and link resolution. Reusing the singleton avoids repeated converter registration overhead across thousands of pages. (seen in `UW-Madison-DSI/agentic-web-extraction:agentic_web_extraction/normalize.py`)

- **Strip boilerplate with BeautifulSoup before markitdown.** Remove `<script>`, `<style>`, `<nav>`, `<header>`, `<footer>`, `<aside>` with BeautifulSoup *before* handing bytes to markitdown; this cuts LLM token cost without losing content. Pin to `html.parser` (stdlib) over `lxml` to avoid hash-instability in test fixtures. Preserve `<header>` elements *inside* `<main>`/`<article>` — they carry title and date. (seen in `UW-Madison-DSI/agentic-web-extraction:agentic_web_extraction/normalize.py`)

- **Post-process with caller-supplied `str → str` text filters.** Pass an optional sequence of pure string-transformation functions after markitdown conversion to strip site-specific volatile tokens (timestamps, session IDs, ad fragments) without coupling the pipeline to any particular site. Apply them in order on `result.markdown`. (seen in `UW-Madison-DSI/agentic-web-extraction:agentic_web_extraction/normalize.py`)

## Learnings

- **Importing `StreamInfo` from a private submodule** → **import it from the top-level package.** `from markitdown._stream_info import StreamInfo` reached into an internal module; `StreamInfo` is now in `__all__` and importable as `from markitdown import StreamInfo`. Relying on private submodule paths breaks across minor releases. (seen in `UW-Madison-DSI/agentic-web-extraction:agentic_web_extraction/normalize.py`)

- **Reading `.text_content` from the result** → **read `.markdown` instead.** `DocumentConverterResult.text_content` is a soft-deprecated alias; `.markdown` is now the primary field (and `str(result)` also works). The change signals that the result type is richer than plain text — it's structured markdown — so new code should treat `.markdown` as the canonical attribute name.

- **Using `convert_url()` for remote pages** → **use `convert()` or `convert_uri()`.** `convert_url` is flagged for future deprecation in favor of the universal `convert()` dispatcher, which accepts a `str` path-or-URL, a `Path`, a `requests.Response`, or any binary file-like — reducing the surface area you need to know.

## Agent rules

- ALWAYS import `StreamInfo` from `markitdown` directly (`from markitdown import MarkItDown, StreamInfo`), not from `markitdown._stream_info`.
- ALWAYS access `result.markdown` (not `result.text_content`) on `DocumentConverterResult` objects.
- ALWAYS create a single `MarkItDown()` instance at module level and reuse it; never instantiate per-call.
- ALWAYS supply a `StreamInfo(mimetype=..., url=...)` when calling `convert_stream` so markitdown can detect format and resolve relative links correctly.
- NEVER pass raw HTML bytes to markitdown without stripping boilerplate first when the goal is LLM input — nav/footer/script elements inflate token count without adding signal.
