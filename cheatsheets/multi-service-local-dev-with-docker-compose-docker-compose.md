# Multi-service local dev with Docker Compose with docker-compose

_Grounded in JasonLo's repos as of 2026-08-31; current practice per [docs.docker.com/compose](https://docs.docker.com/compose/) and the Compose Specification._

## Reference snippet

```yaml
# compose.yaml — multi-service local dev with named-volume Postgres
services:
  db:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp_dev
    volumes:
      - db-data:/var/lib/postgresql/data   # named volume, not bind mount; Postgres ≤17 path
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 10s
      timeout: 10s
      retries: 5
      start_period: 30s

  app:
    build: .
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy   # waits for pg_isready to pass, not just container start
    environment:
      DATABASE_URL: postgres://myapp:secret@db:5432/myapp_dev

volumes:
  db-data:
```

## Typical usage patterns

- **Named volumes for stateful services**: declare `volumes: db-data:` at the top level and mount with `db-data:/var/lib/postgresql/data`; Docker manages ownership and survives `docker compose down` (purged only with `-v`). Used in `JasonLo/dazzo-monitor:docker-compose.yml` (InfluxDB) and `JasonLo/server-usage-monitor:compose.yaml` (InfluxDB + Grafana).
- **`restart: unless-stopped` for long-running infrastructure**: auto-restarts on crash or daemon restart, but respects `docker compose stop` — the stopped state persists across daemon restarts, unlike `always` which ignores manual stops. Consistent across `JasonLo/dazzo-monitor`, `JasonLo/server-usage-monitor`, and `JasonLo/md-render`.
- **External network for multi-stack reverse proxy (Traefik pattern)**: run Traefik in its own compose stack; app services join via `networks: traefik_network: external: true` and opt into routing with labels (`traefik.http.routers.<name>.rule=Host(...)`). No host port exposure needed per service. Used in `JasonLo/server-usage-monitor:compose.yaml`.

## Learnings

- **The `version:` top-level key and the legacy `docker-compose` command (V1) are EOL** → **omit `version:`, use `docker compose` (space, V2 plugin), and name the file `compose.yaml`**. V1's `depends_on: [db]` only waited for container start; V2's `depends_on: db: condition: service_healthy` actually waits for the healthcheck to pass, eliminating shell sleep hacks. (`JasonLo/undock:docker_client.py` already calls `["docker", "compose", ...]`, not the legacy binary)
- **Mounting Postgres data at the wrong path causes silent data loss or a startup refusal** → **pin the Postgres major version and mount at its exact `PGDATA` path**. For Postgres ≤17 this is `/var/lib/postgresql/data`; mounting at the parent `/var/lib/postgresql` silently creates an anonymous volume at the data subpath, so data is written there and lost on container re-creation. Postgres 18 changed the default `PGDATA` to `/var/lib/postgresql/18/docker` — upgrading without updating the mount path triggers a startup error and requires a `pg_dump` / restore cycle.
- **`$$` (double-dollar) in YAML healthcheck strings** → **escape Compose-interpolated variables with `$$` to pass them literally to the shell inside the container**. A single `$POSTGRES_USER` in the YAML is expanded by Compose at parse time (usually to empty string in a healthcheck context), while `$$POSTGRES_USER` becomes the literal `$POSTGRES_USER` that the container shell then expands against the running environment. (visible in `JasonLo/md-render:compose.yaml` healthcheck pattern)

## Agent rules

- ALWAYS use `docker compose` (space, V2 plugin) — never the legacy `docker-compose` (hyphen) command.
- ALWAYS use a named volume (top-level `volumes:` block) for Postgres data, never a host-directory bind mount.
- ALWAYS pin the Postgres major version (`postgres:17`, not `postgres:latest`) and match the volume mount path to that version's `PGDATA`.
- ALWAYS add a `pg_isready` healthcheck and `depends_on: condition: service_healthy` on any service that depends on Postgres being ready.
- NEVER use `restart: always` for local dev infrastructure — use `restart: unless-stopped` so manual stops persist across daemon restarts.
- NEVER include a top-level `version:` field in compose files — it is ignored and signals V1 lineage.
