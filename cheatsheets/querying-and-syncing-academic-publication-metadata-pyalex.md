# Querying and syncing academic publication metadata with pyalex

_Grounded in JasonLo's repos as of 2026-11-03. Current practice is from github.com/J535D165/pyalex._

## Reference snippet

```python
# Set the API key before any request. Required since 2026-02-13.
import pyalex
pyalex.config.api_key = "<YOUR_API_KEY>"

from pyalex import Works, Authors

# Fetch all works for one author, sorted by citation count.
works = (
    Works()
    .filter(authorships={"author": {"id": "A5021047469"}})
    .sort(cited_by_count="desc")
    .paginate(per_page=200)
)
for page in works:
    for work in page:
        print(work["doi"], work["cited_by_count"])
```

## Typical usage patterns

- **Fuse ORCID and OpenAlex into one record set.** Fetch publications from both sources, then deduplicate by DOI and fall back to a title slug. Prefer OpenAlex fields when both sides exist, and prefer ORCID when a date is more specific (seen in `JasonLo/jasonlo.dev:scripts/sync-publications-fused.ts`).

- **Guard against partial API responses.** Compare the fetched count with the count of existing records before writing any output. If the count is below 80% of existing records, stop with an error to prevent deleting valid local data.

- **Use `.filter_or(doi=[...])` for batch DOI lookup.** Pass up to 100 DOIs in one call instead of making one call for each DOI. This keeps the script within the daily credit budget.

## Learnings

- **No API key (email-based polite pool)** → **mandatory `pyalex.config.api_key`**. Without a key, the daily limit is 100 credits, which is too low for any sync script. Get a free API key and set it with `pyalex.config.api_key` before the first request.

- **Fetching all fields for every work** → **use `.select(["id", "doi", "cited_by_count", ...])` to request only needed fields**. Requesting all fields increases response size and can exhaust page limits faster. Selecting fields reduces payload size and keeps the query within rate limits on large author corpora.

- **Making one request for each DOI** → **batch DOIs with `.filter_or(doi=[...])`**. Single-DOI requests each cost one credit. A batch request costs one credit for the whole list.

## Agent rules

- ALWAYS set `pyalex.config.api_key` before making any request.
- ALWAYS use `.paginate(per_page=200)` for author corpora larger than 200 works.
- ALWAYS add a floor-ratio guard before overwriting local records from a paginated sync.
- NEVER look up DOIs one at a time; use `.filter_or(doi=[...])` to batch the list.
- ALWAYS use `.select([...])` to limit returned fields when you do not need the full work object.
