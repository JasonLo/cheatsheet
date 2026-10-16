# Loading large datasets efficiently with datasets

_Grounded in JasonLo's repos as of 2026-08-31. Current practice is from HuggingFace Datasets docs (v3.6.x)._

## Reference snippet

```python
from datasets import load_dataset

# Stream from HuggingFace Hub. Do not download the full dataset.
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

- For a large public dataset, `load_dataset("owner/name", streaming=True)` returns an `IterableDataset` that fetches Hub shards only when the loop reads them and needs no disk space. Then `.with_format("torch")` gives tensors, and `.take(n)` gives a sample. (seen in `UW-Madison-DSI/pelican-data-loader:notebooks/speed_test.ipynb`)

- To stream Parquet from S3, pass `data_files="s3://bucket/prefix/**/*.parquet"` and `storage_options={"key":…, "secret":…, "client_kwargs":{"endpoint_url":…}}` to `load_dataset("parquet", …, streaming=True)`. The function forwards `storage_options` to `fsspec`/`s3fs` and returns a `DatasetDict` that you read with `ds["train"]`. (seen in `UW-Madison-DSI/pelican-data-loader:notebooks/speed_test.ipynb`)

- Without `streaming=True`, `load_dataset("csv", data_files={"train": path})` or `load_dataset("parquet", data_files=…)` downloads the full dataset and caches it as Arrow under `~/.cache/huggingface/datasets`. Use this mode for datasets that fit in RAM. (seen in `UW-Madison-DSI/pelican-data-loader:pelican_data_loader/db.py`)

## Learnings

- **Pass a custom filesystem as `fs=`** → **`load_dataset` builds the filesystem from a storage description.** All cloud authentication goes in one `storage_options` dict. You do not construct the filesystem object yourself.

- **A streamed dataset is a normal `Dataset`** → **`streaming=True` gives an `IterableDataset` with a different API.** It has no random indexing and no `.num_rows`. Its `.shuffle()` uses a buffer, so use in-memory mode for filtering, `.map()` caching, or row-level indexing.

- **`load_dataset` can glob any filesystem** → **A custom filesystem needs its own glob before `load_dataset`.** Non-standard authentication, for example Pelican/WebDAV, blocks the glob in `load_dataset`. Pass the fully-qualified URLs from `fs.glob("…/**/*.parquet")` as `data_files`. (seen in `UW-Madison-DSI/pelican-data-loader:notebooks/speed_test.ipynb`)

## Agent rules

- ALWAYS use `storage_options=` to pass cloud credentials to `load_dataset` in datasets v3+.
- NEVER pass `fs=` to `load_dataset`.
- ALWAYS use `.take(n)` to materialize samples from an `IterableDataset`.
- NEVER index an `IterableDataset` split with `ds["train"][0]`.
- NEVER call `.num_rows` on an `IterableDataset`.
- NEVER call `.shuffle()` without a buffer on an `IterableDataset`.
- NEVER use row-index slices on an `IterableDataset`.
- ALWAYS use in-memory mode when you need these operations.
- ALWAYS glob custom-filesystem paths with the authenticated `fs` object before you call `load_dataset`.
- ALWAYS pass the glob result list as `data_files` to `load_dataset`.
