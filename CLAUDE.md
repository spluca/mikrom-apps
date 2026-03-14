# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a catalog of sample applications packaged with **Cloud Native Buildpacks (CNB)** and designed to run on **Firecracker microVMs**. Each app in `apps/` is independent and self-contained — no shared libraries, no monorepo workspace.

## Building Applications

The primary build tool is [`pack`](https://buildpacks.io/docs/tools/pack/). Each app is built independently:

```bash
# Most apps (Go, Node, Python, Java)
cd apps/<app-name>
pack build <image-name> --builder paketobuildpacks/builder:base

# Rust (requires full builder for C compiler)
cd apps/rust-app
pack build my-rust-app --builder paketobuildpacks/builder:full
```

**Test locally after building:**
```bash
docker run --rm -p 8080:8080 <image-name>
curl http://localhost:8080/health
```

## App Catalog

| App | Language/Framework | Notes |
|-----|-------------------|-------|
| `go-app` | Go stdlib | Simple HTTP service |
| `node-app` | Node.js + Fastify 4 | Simple HTTP service |
| `rust-app` | Rust + Axum 0.7 + Tokio | Needs `:full` builder |
| `python-app` | Python + FastAPI + Uvicorn | Simple HTTP service |
| `java-app` | Java 17 + Quarkus 3.2 | Built as uber-jar |
| `go-task-api` | Go + SQLite (CGO) | CRUD REST API with persistence |
| `python-worker` | Python + FastAPI | Async job queue with background tasks |

## App Structure Convention

Every app follows the same three-file pattern for CNB packaging:

- **`project.toml`** — CNB build environment variables (Go flags, language versions, etc.)
- **`Procfile`** — Runtime entrypoint (`web: <start-command>`)
- Language manifest (`go.mod`, `package.json`, `Cargo.toml`, `pom.xml`, `requirements.txt`)

All apps expose port **8080** (configurable via `PORT` env var) with:
- `GET /` — JSON response with message, timestamp, hostname
- `GET /health` — Health check (`200 OK`)

## Key Build Configurations

- **Go apps**: Strip binaries with `-ldflags='-s -w'` set in `project.toml`
- **go-task-api**: Requires `CGO_ENABLED=1` (SQLite via `go-sqlite3`) — set in `project.toml`
- **Rust**: Uses `BP_CARGO_TINI=true` (process init)
- **Java**: Maven uber-jar (`quarkus-maven-plugin`)

## Firecracker Deployment

After building a container image, extract rootfs for Firecracker:
```bash
docker create --name tmp <image-name>
docker export tmp | tar -xf - -C rootfs/
docker rm tmp
# Then create ext4 filesystem and vm-config.json
```

See `README.md` for the full deployment workflow.
