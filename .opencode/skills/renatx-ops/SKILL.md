---
name: Renatx Container & Traefik Ops
description: Use this skill when starting, stopping, rebuilding, or debugging Podman containers, Traefik v3 routing, or PostgreSQL database operations in the Renatx platform.
---

# Renatx Container & Traefik Operations (`renatx-ops`)

## Architecture Rules
1. **Podman Rootless First:**
   - Never require `sudo` for container runtime commands.
   - Local orchestration uses `podman-compose` via `compose.yaml` (web/api/db/traefik) and `compose.rustdesk.yaml` (hbbs/hbbr).
   - Always pass `--force-recreate` when rebuilding containers (`podman-compose up -d --build --force-recreate`) because `podman-compose` does not automatically recreate running containers when an image tag is rebuilt.

2. **Traefik v3 Security & Routing (`infra-platform/traefik/`):**
   - Never mount `/var/run/docker.sock` or the rootless Podman socket into Traefik unless explicitly requested. Use the **File Provider** (`infra-platform/traefik/dynamic.yml`).
   - Routing rules:
     - `/api/*` strips `/api` (`strip-api-prefix` middleware) and forwards to `http://service-api:8000` over `proxy_net`.
     - `/*` forwards to `http://service-web:3000` over `proxy_net`.
   - Local HTTP port is `8080` (`http://renatx.localhost:8080`), dashboard on `8081`.

3. **PostgreSQL Isolation (`db_net`):**
   - `renatx-postgres` lives strictly inside `db_net` (`internal: true`).
   - **Never** add a `ports:` mapping to `postgres` in `compose.yaml`.
   - Use `make db-shell` or `make db-backup` to interact with the database via `podman exec`.

4. **FastAPI + `uv` Container Rules (`service-api/`):**
   - Do not declare `readme = "README.md"` or `[build-system]` in `service-api/pyproject.toml` unless `README.md` is copied into the container.
   - Always run `uvicorn` with `uv run --no-project uvicorn app.main:app --host 0.0.0.0 --port 8000` so `uv` does not attempt an editable build at container startup.
