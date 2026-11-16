# Web content extraction for LLM pipelines with trafilatura

_Grounded in JasonLo's repos as of 2026-11-16. Current practice is from trafilatura 2.3.1 docs._

## Reference snippet

```python
import trafilatura

def extract_page(url: str, max_chars: int = 1000) -> dict:
    # fetch_url sets browser-like headers and follows redirects for news sites.
    html = trafilatura.fetch_url(url)
    if html is None:
        return {"text": "", "date": None}
    # bare_extraction parses the HTML one time and returns text and metadata.
    doc = trafilatura.bare_extraction(html, url=url, favor_precision=True)
    if doc is None:
        return {"text": "", "date": None}
    return {"text": (doc.text or "")[:max_chars], "date": doc.date}
```

## Typical usage patterns

- **Article text extraction for LLM context.** Pass raw HTML to `trafilatura.extract(html)` and always use `(result or "")` before you truncate or send the result to a prompt. Use a char limit (for example, 1000) to keep the text within the token budget.

- **Combined text and date extraction in one pass.** Call `bare_extraction(html, url=url)` to get a Document object with both `.text` and `.date` from a single HTML parse. Use `.date` as a fallback when the search API does not return a publication date.

- **Parallel fetch-and-extract with error isolation.** Run one `read_page()` worker for each URL in a `ThreadPoolExecutor` and wrap each worker in a broad `try/except`. One failed page must not stop the full batch.

## Learnings

- **Calling extract() and extract_metadata() separately for text and date** → **Using bare_extraction() for one HTML parse.** A call to `bare_extraction()` returns a Document with both `.text` and `.date` from one HTML parse. Two separate calls do the same parse work twice and add latency to the pipeline.

- **Fetching news pages with a plain HTTP client** → **Using trafilatura.fetch_url() for page downloads.** `fetch_url()` sets browser-like headers and follows redirects that many news sites require. A plain `httpx.get()` without custom headers often gets a redirect wall or empty body on those sites.

- **Trusting extract() to return a string** → **Guarding against None from extract().** `extract()` returns None when it finds no main content on a page (login wall, paywall, or mostly-script page). Without a guard, any string operation on the result raises `TypeError`.

## Agent rules

- NEVER use the return value of `trafilatura.extract()` without guarding against None.
- ALWAYS use `bare_extraction()` when you need both the article text and the metadata in one call.
- ALWAYS use `trafilatura.fetch_url()` instead of a plain HTTP client when fetching pages for extraction.
- ALWAYS wrap each fetch-and-extract call in a try/except when you process multiple URLs in parallel.
- NEVER pass the full article text to an LLM without truncating it first.
