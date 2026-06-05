# Tabular data with Polars

_Grounded in JasonLo's repos as of 2026-06-05; current practice per Polars user guide (context7 `/pola-rs/polars`)._

## Reference snippet

```python
import polars as pl

# Lazy: scan, not read — the optimizer pushes filter/projection into the reader.
lf = (
    pl.scan_parquet("data/*.parquet")          # or scan_csv; lazy by default
    .filter(pl.col("active"))
    .with_columns(
        year=pl.col("created_at").dt.year(),    # parallel expressions
        score_z=(pl.col("score") - pl.col("score").mean()) / pl.col("score").std(),
    )
    .group_by("topic")
    .agg(
        n=pl.len(),
        avg_score=pl.col("score").mean(),
    )
)

df = lf.collect()                               # one execution, optimized
# huge result? lf.sink_parquet("out.parquet")  # stream straight to disk
```

## Typical usage patterns

_Docs-based: the user's repos show essentially no first-party Polars API code yet — dataframe work to date is pandas (`.loc`/`.query`/`.groupby`/`.merge`) and R/dplyr (`group_by` in analysis scripts). Polars is the chosen `python-data` framework going forward, so patterns below are the current-practice target, not mined idioms._

- Reach for `scan_*` + `collect()` for any file-backed ETL; reserve eager `pl.DataFrame` / `read_*` for small in-memory tables and quick inspection.
- Crossover path documented as `polars.from_pandas(df)` for migrating existing pandas frames (`JasonLo/best-in-slot:slots/python-data/pandas/CHEATSHEET.md`).
- Existing aggregation habits are dplyr-style `group_by` + summarise in R analysis scripts — directly transferable to `pl.col(...).agg(...)`.

## Learnings

- **Pandas/R indexing mindset (`df.loc[...]`, `df[mask]`, `df["x"] = ...`)** → **expressions as the unit of work.** Describe *what* a column should be with `pl.col(...)` inside `select`/`with_columns`/`filter`/`group_by().agg()`; Polars parallelizes and optimizes the whole expression set, which positional indexing can't.
- **`read_csv` then transform (pandas-style eager load)** → **`scan_*` + `collect()`.** Scanning is lazy; the optimizer prunes columns/rows at the reader, so you never materialize data you immediately drop.
- **In-place mutation / chained reassignment (`df["c"] = ...`)** → **immutable transforms returning new frames.** Build a single chain; each step yields a new frame, so there is no `SettingWithCopy` ambiguity and the chain stays one optimizable plan.

## Agent rules

- ALWAYS express column logic with `pl.col(...)` inside `select` / `with_columns` / `filter` / `agg`.
- ALWAYS use `pl.scan_csv` / `pl.scan_parquet` for file-backed pipelines, ending in a single `.collect()`.
- ALWAYS batch independent column derivations into one `with_columns` call so they run in parallel.
- ALWAYS use `expr.over("key")` for group-aligned per-row results instead of group-then-merge-back.
- ALWAYS express conditionals as `pl.when().then().otherwise()` within an expression.
- ALWAYS prefer `sink_parquet`/`sink_csv` when writing large lazy results.
- NEVER use positional/label indexing (`df.loc`, `df.iloc`, `df[mask]`) for transforms.
- NEVER use eager `read_*` for large file ETL when a `scan_*` will do.
- NEVER mutate a frame in place or reassign columns via `df["c"] = ...`.
- NEVER call `.collect()` mid-pipeline just to inspect; keep the plan lazy until the final result.
