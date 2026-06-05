# Vector search with pgvector

_Grounded in JasonLo's repos as of 2026-06-05; current practice per the official pgvector + pgvector-python READMEs (context7 `/pgvector/pgvector`)._

## Reference snippet

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Match dim to your embedding model (e.g. 768, 1536)
CREATE TABLE docs (
    id        bigserial PRIMARY KEY,
    content   text,
    embedding vector(768)
);

-- Operator class MUST match the metric the embeddings were trained for.
-- Cosine here -> vector_cosine_ops -> query with <=>
CREATE INDEX docs_embedding_idx
    ON docs USING hnsw (embedding vector_cosine_ops);

-- Top-5 nearest neighbors
SELECT id, content
FROM docs
ORDER BY embedding <=> '[0.1,0.2,...]'
LIMIT 5;
```

```python
import numpy as np, psycopg
from pgvector.psycopg import register_vector  # register_vector_async for async

with psycopg.connect(url) as conn:
    register_vector(conn)                       # makes vector <-> numpy work
    conn.execute("INSERT INTO docs (embedding) VALUES (%s)", (np.random.rand(768),))
    rows = conn.execute(
        "SELECT id FROM docs ORDER BY embedding <=> %s LIMIT 5",
        (np.random.rand(768),),
    ).fetchall()
```

- Operator ↔ opclass pairing: `<->`/`vector_l2_ops` (L2), `<#>`/`vector_ip_ops` (inner product, returns negative), `<=>`/`vector_cosine_ops` (cosine).
- Recall/speed at query time: `SET hnsw.ef_search = 100;` (higher = better recall, slower); `SET LOCAL` inside a txn for a single query.

## Typical usage patterns

- pgvector is the chosen vector-DB slot; reach for it instead of a standalone vector DB (Milvus/Qdrant) when Postgres is already in the stack — keeps one datastore. (`JasonLo/best-in-slot:slots/databases-vector.yaml`)
- Cosine as the default metric: `vector(768)` column + HNSW `vector_cosine_ops` index + `<=>` query operator, kept consistent end to end. (`JasonLo/best-in-slot:slots/databases/postgres-psycopg/CHEATSHEET.md`)
- pgvector-python `register_vector(conn)` over a `psycopg` v3 connection, then pass/receive plain numpy arrays — no manual `[..]` string formatting. (`JasonLo/best-in-slot:slots/databases/postgres-psycopg/CHEATSHEET.md`)
- Vector queries run through the same `psycopg` v3 pool conventions as relational ones (`AsyncConnectionPool`, `%s` params, one query-fn per op), so vector search is just another query against the app DB. (`JasonLo/best-in-slot:slots/databases/postgres-psycopg/README.md`)

## Learnings

- **"A vector column is searchable enough" → index choice is a recall/latency contract.** Without an ANN index every query is an exact full scan; HNSW (or IVFFlat) trades exact results for sub-linear search, and the opclass picks the metric.
- **"Pick any distance operator" → operator must match the embedding's training metric.** Cosine embeddings searched with `<->` (L2) silently rank wrong; use `<=>`/`vector_cosine_ops` for cosine models, and keep column-index-query all on one metric.
- **"Build the index, then load data" (IVFFlat habit) → HNSW builds incrementally; IVFFlat must see data first.** IVFFlat clusters existing rows, so its lists are meaningless on an empty table (build after load, ~rows/1000 lists). HNSW has no such ordering constraint — but for large loads, bulk-insert then index for speed.
- **"Tune recall by rebuilding the index" → recall is a runtime knob.** `hnsw.ef_search` / `ivfflat.probes` are per-session/per-transaction settings; raise them for accuracy without touching the index.
- **"Default to a dedicated vector DB" → start in Postgres.** For most app-scale corpora pgvector colocated with the relational data beats operating a separate vector service; reach for `halfvec`/quantization or a specialized store only when scale forces it.

## Agent rules

- ALWAYS run `CREATE EXTENSION IF NOT EXISTS vector;` before any vector DDL.
- ALWAYS pin the `vector(N)` dimension to the embedding model's output size.
- ALWAYS pair the query operator with the index opclass and the model's metric: `<=>`+`vector_cosine_ops` (cosine), `<->`+`vector_l2_ops` (L2), `<#>`+`vector_ip_ops` (inner product).
- ALWAYS create an ANN index (HNSW by default) before relying on nearest-neighbor latency at scale.
- ALWAYS create an IVFFlat index AFTER the table holds representative data, sized ~rows/1000 lists (≤1M rows).
- ALWAYS tune recall via `hnsw.ef_search` / `ivfflat.probes` at session or transaction scope, not by rebuilding.
- ALWAYS call `register_vector(conn)` (or `register_vector_async`) and pass numpy arrays as `%s` params.
- NEVER mix metrics across column, index, and query operator.
- NEVER build an IVFFlat index on an empty or unrepresentative table.
- NEVER hand-format embeddings into `'[...]'` strings in Python when pgvector-python can bind numpy arrays.
- NEVER reach for a separate vector database when Postgres is already in the stack and the corpus fits pgvector.
