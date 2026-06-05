# Time-series data with InfluxDB

_Grounded in JasonLo's repos as of 2026-06-05; current practice per context7 `/influxdata/influxdb-client-python` (InfluxDB 2.x official docs)._

## Reference snippet

```python
from datetime import datetime, timezone
from influxdb_client import InfluxDBClient, Point, WriteOptions

# Config from env: INFLUXDB_V2_URL / INFLUXDB_V2_TOKEN / INFLUXDB_V2_ORG
with InfluxDBClient.from_env_properties() as client:
    # Batched writer — non-blocking, auto-retry, flushed on context exit
    with client.write_api(write_options=WriteOptions(batch_size=500, flush_interval=10_000)) as write_api:
        p = (
            Point("gpu_usage")
            .tag("host", "dgx-01")            # indexed metadata
            .field("util_pct", 87.0)          # measured value
            .field("mem_mb", 23000)
            .time(datetime.now(timezone.utc)) # explicit UTC timestamp
        )
        write_api.write(bucket="metrics", record=p)

    # Read back with Flux
    flux = '''
    from(bucket:"metrics")
      |> range(start: -1h)
      |> filter(fn: (r) => r._measurement == "gpu_usage" and r.host == "dgx-01")
      |> mean()
    '''
    for table in client.query_api().query(flux):
        for r in table.records:
            print(r.get_time(), r.get_field(), r.get_value())
```

## Typical usage patterns

- **Metric collector → InfluxDB:** parse a script/sensor reading into `Point` objects, write a list via `write_api`, one process run = one batch. (`JasonLo/server-usage-monitor:send_gpu_usage.py`, `JasonLo/server-usage-monitor:utils.py`)
- **`Point` builder for structured metrics:** `Point(measurement).tag(...).field(...)`; tags = indexed dimensions (host, user, sensor), fields = numeric values. (`JasonLo/best-in-slot:slots/databases/influxdb/example/influxdb_example/__init__.py`)
- **Config from env via dotenv:** url/token/org/bucket pulled from `os.getenv` with `load_dotenv()`; never inlined. (`JasonLo/server-usage-monitor:utils.py`, `JasonLo/dazzo-monitor:server/push.py`)
- **Client as context manager:** `with InfluxDBClient(...) as client:` for guaranteed cleanup. (`JasonLo/server-usage-monitor:send_gpu_usage.py`)
- **Raw line protocol over HTTP for constrained writers:** `POST /api/v2/write?org=&bucket=&precision=s` with `Authorization: Token <tok>`, body = hand-built line protocol. Used where the SDK is unavailable (ESP32/CircuitPython, tiny scripts). (`JasonLo/dazzo-monitor:server/push.py`; also seen in private device/ingest repos — generalized)
- **Flux for reads:** `from(bucket) |> range() |> filter() |> aggregate`; iterate `tables[].records`. (`JasonLo/best-in-slot:slots/databases/influxdb/CHEATSHEET.md`)

## Learnings

- **String-formatted line protocol as the default write path** → **`Point` builder as the default; raw line protocol only for SDK-less writers.** Manual `f"{m},{tags} {fields} {ts}"` silently mis-types fields (int vs float vs string) and breaks on escaping; `Point` enforces the type/escaping contract. Drop to raw strings only on devices that can't run the SDK. (seen in `JasonLo/dazzo-monitor:server/push.py`)
- **`SYNCHRONOUS` write_api for every workload** → **batched `WriteOptions` for any stream/high-volume source.** Synchronous = one HTTP round-trip per write, fine for a once-per-run collector but a bottleneck for sensor streams; the batching writer coalesces points and retries in the background. (seen in `JasonLo/server-usage-monitor:send_gpu_usage.py`)
- **Commenting out / omitting the timestamp** → **always set an explicit UTC `.time()`.** Letting the server stamp arrival time conflates event time with ingest time and makes backfill/replay wrong; time-series correctness depends on the producer's clock. (seen in `JasonLo/server-usage-monitor:send_gpu_usage.py`)
- **Hand-rolling the v2 write via `requests`/`httpx`** → **use the official client; reach for raw HTTP only when the SDK can't run.** The raw call reimplements auth, batching, retry, and gzip that the client already provides; on a normal Python host it's strictly more to maintain. (generalized from private repos; public echo in `JasonLo/dazzo-monitor:server/push.py`)
- **Tags vs fields chosen ad hoc** → **tags = low-cardinality indexed labels, fields = the measured values.** High-cardinality tags (ids, timestamps) explode the series index; this is a schema decision, not a syntax one.

## Agent rules

- ALWAYS build write payloads with `Point(...).tag().field().time()` on any host that can run `influxdb-client`.
- ALWAYS set an explicit UTC timestamp via `.time(datetime.now(timezone.utc))` (or the event's own time).
- ALWAYS use batched `WriteOptions(batch_size=..., flush_interval=...)` for streaming/high-volume writes; reserve `SYNCHRONOUS` for one-shot collectors.
- ALWAYS load url/token/org/bucket from env (`from_env_properties()` or `os.getenv` + dotenv); NEVER hardcode them.
- ALWAYS open `InfluxDBClient` and the batching `write_api` as context managers so buffers flush and connections close.
- ALWAYS make tags low-cardinality dimensions and put measured numbers in fields.
- NEVER hand-build line protocol strings on a host that can run the SDK; reserve raw `/api/v2/write` POSTs for SDK-less writers (ESP32/CircuitPython).
- NEVER let the server assign the timestamp when event time matters.
- NEVER commit a real InfluxDB token.
```
