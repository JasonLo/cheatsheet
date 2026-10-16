# Multi-service local dev with Docker Compose with docker-compose

_Grounded in JasonLo's repos as of 2026-08-31. Current practice is from [docs.docker.com/compose](https://docs.docker.com/compose/) and the Compose Specification._

## Reference snippet

```yaml
# compose.yaml: local development for many services, with Postgres data in a named volume
services:
  db:
    image: postgres:17
    restart: unless-stopped
    environment:
      POSTGRES_USER: myapp
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp_dev
    volumes:
      - db-data:/var/lib/postgresql/data   # named volume, not a bind mount. This path is for Postgres 17 and earlier.
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
        condition: service_healthy   # waits until pg_isready passes, not only until the container starts
    environment:
      DATABASE_URL: postgres://myapp:secret@db:5432/myapp_dev

volumes:
  db-data:
```

## Typical usage patterns

- **Named volumes for stateful services.** A top-level `volumes: db-data:` entry declares the volume, and the service mounts it with `db-data:/var/lib/postgresql/data`. Docker manages ownership, and the data stays after `docker compose down` unless you add `-v`. (seen in `JasonLo/dazzo-monitor:docker-compose.yml`, `JasonLo/server-usage-monitor:compose.yaml`)
- **`restart: unless-stopped` for long-running infrastructure.** The service restarts after a crash or a daemon restart. A manual `docker compose stop` continues to apply after a daemon restart, but `always` ignores manual stops. (seen in `JasonLo/dazzo-monitor`, `JasonLo/server-usage-monitor`, `JasonLo/md-render`)
- **External network for a reverse proxy that serves many stacks.** Run Traefik in its own compose stack, so that the services need no host ports. App services join with `networks: traefik_network: external: true` and activate routing with labels, for example `traefik.http.routers.<name>.rule=Host(...)`. (seen in `JasonLo/server-usage-monitor:compose.yaml`)

## Learnings

- **A started container is a ready dependency** → **A dependent service waits for a passing healthcheck.** The old V1 `depends_on: [db]` waited only for the container start. Now `depends_on: db: condition: service_healthy` waits for the healthcheck, so no shell sleep is necessary. (seen in `JasonLo/undock:docker_client.py`)
- **Any mount path for Postgres keeps the data** → **The mount path must match the `PGDATA` of the pinned major version.** For Postgres ≤17 the path is `/var/lib/postgresql/data`, and for Postgres 18 it is `/var/lib/postgresql/18/docker`. A mount at the parent `/var/lib/postgresql` puts the data in an anonymous volume, and a re-created container does not get that data.
- **Compose passes `$POSTGRES_USER` in a healthcheck to the container shell** → **Compose interpolates variables first, and `$$` sends a variable to the container unchanged.** Compose expands a single `$POSTGRES_USER` at parse time, usually to an empty string. Compose changes `$$POSTGRES_USER` to the literal `$POSTGRES_USER`, and the container shell then expands it. (seen in `JasonLo/md-render:compose.yaml`)

## Agent rules

- ALWAYS use the `docker compose` V2 plugin command.
- NEVER use the old `docker-compose` command with the hyphen.
- ALWAYS use a named volume in the top-level `volumes:` block for Postgres data.
- NEVER use a host-directory bind mount for Postgres data.
- ALWAYS pin the Postgres major version, for example `postgres:17`, not `postgres:latest`.
- ALWAYS match the volume mount path to the `PGDATA` path of the pinned version.
- ALWAYS add a `pg_isready` healthcheck to each Postgres service.
- ALWAYS add `depends_on: condition: service_healthy` to each service that needs a ready Postgres.
- NEVER use `restart: always` for local dev infrastructure.
- ALWAYS use `restart: unless-stopped`.
- NEVER include a top-level `version:` field in compose files.
- ALWAYS name the Compose file `compose.yaml`.
