# Loading large datasets efficiently with datasets

_Grounded in JasonLo's repos as of 2026-08-31; current practice per HuggingFace Datasets docs (v3.6.x)._

## Reference snippet

```python
from datasets import load_dataset

# Stream from HuggingFace Hub without downloading the full dataset
ds = load_dataset("bigcode/the-stack-dedup", split="train", streaming=True)
for sample in ds.with_format("torch").take(5):
    print(sample)

# Stream from S3-compatible storage with credentials
storage_options = {
    "key": "ACCESS_KEY",
    "secret": "SECRET_KEY",
    "client_kwargs": {"endpoint_url": "https://s3.example.com"},
}
ds = load_dataset(
    "parquet",
    data_files="s3://bucket/data/**/*.parquet",
    storage_options=storage_options,
    streaming=True,
)
for sample in ds["train"].take(5):
    print(sample)
```

## Typical usage patterns

- **Hub streaming for large public datasets** — `load_dataset("owner/name", streaming=True)` returns an `IterableDataset` that fetches shards on demand; no disk budget required and time-to-first-sample is ~5 s vs. a multi-hour full download. Call `.take(n)` to consume a sample, `.with_format("torch")` before the loop to get tensors. (seen in `UW-Madison-DSI/pelican-data-loader:notebooks/speed_test.ipynb`)

- **Parquet glob over S3 with `storage_options`** — pass `data_files="s3://bucket/prefix/**/*.parquet"` and `storage_options={"key":…, "secret":…, "client_kwargs":{"endpoint_url":…}}` to `load_dataset("parquet", …, streaming=True)`. The `storage_options` dict is forwarded to `fsspec`/`s3fs`; result is a `DatasetDict` keyed by split so access via `ds["train"]`. (seen in `UW-Madison-DSI/pelican-data-loader:notebooks/speed_test.ipynb`)

- **In-memory load for small/local files** — `load_dataset("csv", data_files={"train": path})` or `load_dataset("parquet", data_files=…)` without `streaming=True` downloads and caches the full dataset in Arrow format under `~/.cache/huggingface/datasets`. Cached on-disk format makes repeat loads fast; use for datasets that fit in RAM. (seen in `UW-Madison-DSI/pelican-data-loader:pelican_data_loader/db.py`)

## Learnings

- **`fs=` is gone in v3.0** → **pass credentials via `storage_options=`**. The old `fs` parameter (a custom fsspec filesystem object) was deprecated in v2.8 and removed in v3.0; all cloud-storage auth now goes in the `storage_options` dict directly on `load_dataset`. Same intent, different surface — you no longer construct the filesystem object yourself.

- **`streaming=True` returns `IterableDataset`, not `Dataset`** → **these are different types with different APIs**. `IterableDataset` has no random indexing, no `.shuffle()` with a buffer size default of the whole dataset, and no `.num_rows`. Use `.take(n)` to consume a sample; use in-memory mode when you need filtering, `.map()` caching, or row-level indexing.

- **Custom-filesystem path globbing must happen before `load_dataset`** → **glob separately, then pass the explicit list as `data_files`**. When the storage backend needs non-standard auth (e.g. Pelican/WebDAV), `load_dataset` can't drive the glob itself; call `fs.glob("…/**/*.parquet")` first, build a list of fully-qualified URLs, then pass that list. (seen in `UW-Madison-DSI/pelican-data-loader:notebooks/speed_test.ipynb`)

## Agent rules

- ALWAYS use `storage_options=` (not `fs=`) to pass cloud credentials to `load_dataset` in datasets v3+.
- ALWAYS access split results with `ds["train"]` (not `ds["train"][0]`) when the dataset is an `IterableDataset` — use `.take(n)` to materialize samples.
- NEVER call `.num_rows`, `.shuffle()` without a buffer, or row-index slices on an `IterableDataset` — switch to in-memory mode if those operations are needed.
- ALWAYS glob custom-filesystem paths with the authenticated `fs` object first, then pass the result list as `data_files` to `load_dataset`.
