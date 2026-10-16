# Converting scraped web content to markdown for LLM pipelines with markitdown

_Grounded in JasonLo's repos as of 2026-10-15. Current practice is from markitdown v0.1.8 (microsoft/markitdown)._

## Reference snippet

```python
import io
from markitdown import MarkItDown, StreamInfo  # StreamInfo is public

_md = MarkItDown()  # One instance at module level, used for all calls

def to_markdown(html_bytes: bytes, url: str) -> str:
    info = StreamInfo(mimetype="text/html", url=url)
    result = _md.convert_stream(io.BytesIO(html_bytes), stream_info=info)
    return result.markdown  # Not .text_content, which is an old alias
```

## Typical usage patterns

- **One instance and `convert_stream` for pipelines.** Make one `MarkItDown()` at module level and use it for all pages. Give the raw bytes as `io.BytesIO` with a `StreamInfo` that holds the mimetype, extension, and URL for format detection and link resolution. (seen in `UW-Madison-DSI/agentic-web-extraction:agentic_web_extraction/normalize.py`)
- **Remove boilerplate with BeautifulSoup first.** Remove `<script>`, `<style>`, `<nav>`, `<header>`, `<footer>`, and `<aside>` before markitdown, but keep a `<header>` inside `<main>` or `<article>`. Use the stdlib `html.parser`, because `lxml` can change the output of test fixtures. (seen in `UW-Madison-DSI/agentic-web-extraction:agentic_web_extraction/normalize.py`)
- **Text filters after the conversion.** Apply a sequence of pure `str → str` functions to `result.markdown` in order. Each filter removes tokens that change between visits, for example timestamps or session IDs, so the pipeline stays general. (seen in `UW-Madison-DSI/agentic-web-extraction:agentic_web_extraction/normalize.py`)

## Learnings

- **An internal module path is a stable import** → **Import only the public names of the package**. `StreamInfo` is now in `__all__`, so `from markitdown import StreamInfo` is correct. A path such as `markitdown._stream_info` can break in a minor release.
- **The result is plain text** → **The result is structured markdown**. Read `result.markdown`, because `text_content` is now only an old alias.
- **Each type of source needs its own method** → **One `convert()` method accepts all sources**. It accepts a path or URL string, a `Path`, a `requests.Response`, or a binary file object, so do not use `convert_url()` in new code.

## Agent rules

- ALWAYS import `StreamInfo` from `markitdown`, not from `markitdown._stream_info`.
- ALWAYS read `result.markdown`, not `result.text_content`.
- ALWAYS make one `MarkItDown()` instance at module level and use it for all calls.
- ALWAYS give a `StreamInfo(mimetype=..., url=...)` to `convert_stream`.
- NEVER give raw HTML to markitdown for LLM input before you remove the boilerplate elements.
