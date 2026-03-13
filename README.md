# mikrom-apps

A curated catalog of applications ready to be packaged with [Cloud Native Buildpacks](https://buildpacks.io/) and deployed on [Firecracker](https://firecracker-microvm.github.io/) microVMs. This repository is the primary testing ground for applications running on the **Mikrom** environment.

> **What is Mikrom?** Mikrom is an orchestration layer for Firecracker microVMs. These apps are designed to demonstrate real-world workloads running inside isolated, lightweight virtual machines — with fast boot times and minimal memory overhead.

---

## Application Catalog

### Simple Microservices

These lightweight services demonstrate per-language buildpack packaging. Each starts in milliseconds and exposes `/` and `/health` endpoints.

| App | Language / Framework | Directory |
| :-- | :-- | :-- |
| HTTP API | Go 1.21 (stdlib) | [`apps/go-app`](./apps/go-app) |
| HTTP API | Node.js 20 + Fastify | [`apps/node-app`](./apps/node-app) |
| HTTP API | Rust + Axum 0.7 | [`apps/rust-app`](./apps/rust-app) |
| HTTP API | Python 3.11 + FastAPI | [`apps/python-app`](./apps/python-app) |
| HTTP API | Java 17 + Quarkus | [`apps/java-app`](./apps/java-app) |

### Complex Applications

These are production-style workloads that demonstrate real-world patterns inside a Firecracker microVM.

| App | Description | Directory |
| :-- | :-- | :-- |
| **Task Manager API** | Full CRUD REST API in Go with SQLite persistence. Shows stateful storage inside a microVM. | [`apps/go-task-api`](./apps/go-task-api) |
| **Job Queue Worker** | Python async worker (FastAPI + BackgroundTasks) with full job lifecycle: submit/poll/delete. | [`apps/python-worker`](./apps/python-worker) |

---

## Prerequisites

Install the `pack` CLI:

```bash
# Linux (via script)
curl -sSL "https://github.com/buildpacks/pack/releases/latest/download/pack-linux.tgz" | tar xz
sudo mv pack /usr/local/bin/pack
pack --version
```

---

## Building an App

Navigate to any app directory and run `pack build`:

```bash
cd apps/go-app
pack build my-go-app --builder paketobuildpacks/builder:base
```

> **Note for Rust apps**: the Rust buildpack uses `paketobuildpacks/builder:full` because it includes the C compiler toolchain needed by cargo:
> ```bash
> cd apps/rust-app
> pack build my-rust-app --builder paketobuildpacks/builder:full
> ```

### Run Locally with Docker

After building, run the image with Docker to verify it works before deploying to Firecracker:

```bash
docker run --rm -p 8080:8080 my-go-app
curl http://localhost:8080/health
```

### Try the Task Manager API

```bash
# Build
cd apps/go-task-api
pack build mikrom-task-api --builder paketobuildpacks/builder:base

# Run
docker run --rm -p 8080:8080 mikrom-task-api

# Create a task
curl -X POST http://localhost:8080/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test inside Firecracker"}'

# List tasks
curl http://localhost:8080/tasks
```

### Try the Job Queue Worker

```bash
# Build
cd apps/python-worker
pack build mikrom-worker --builder paketobuildpacks/builder:base

# Run
docker run --rm -p 8080:8080 mikrom-worker

# Submit a job
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{"task": "compute", "payload": {"count": 1000}}'

# Poll the result (replace JOB_ID)
curl http://localhost:8080/jobs/<JOB_ID>

# Interactive API docs
open http://localhost:8080/docs
```

---

## Deploying to Firecracker

Firecracker cannot run OCI images directly — it needs a **kernel** and a **root filesystem image (ext4)**. The steps below show how to extract the filesystem from a buildpack-produced image.

### 1. Extract the Root Filesystem

```bash
# Create a container from the image (don't start it)
docker create --name extract-rootfs my-go-app

# Export the filesystem as a TAR archive
docker export extract-rootfs -o rootfs.tar
docker rm extract-rootfs

# Create a blank ext4 image (512 MB)
truncate -s 512M rootfs.ext4
mkfs.ext4 rootfs.ext4

# Mount and copy the filesystem
mkdir -p /tmp/mnt
sudo mount rootfs.ext4 /tmp/mnt
sudo tar -xf rootfs.tar -C /tmp/mnt
sudo umount /tmp/mnt
```

### 2. Launch with Firecracker

Create a `vm-config.json`:

```json
{
  "boot-source": {
    "kernel_image_path": "/path/to/vmlinux",
    "boot_args": "console=ttyS0 reboot=k panic=1 pci=off"
  },
  "drives": [
    {
      "drive_id": "rootfs",
      "path_on_host": "rootfs.ext4",
      "is_root_device": true,
      "is_read_only": false
    }
  ],
  "machine-config": {
    "vcpu_count": 1,
    "mem_size_mib": 128
  }
}
```

Then start the VM:

```bash
firecracker --api-sock /tmp/firecracker.socket --config-file vm-config.json
```

---

## Project Structure

```
mikrom-apps/
├── README.md
└── apps/
    ├── go-app/            # Simple Go HTTP service
    │   ├── main.go
    │   ├── go.mod
    │   ├── project.toml   # Buildpack config
    │   └── Procfile       # Process entrypoint
    ├── node-app/          # Simple Node.js Fastify service
    ├── rust-app/          # Simple Rust Axum service
    ├── python-app/        # Simple Python FastAPI service
    ├── java-app/          # Simple Java Quarkus service
    ├── go-task-api/       # Complex: CRUD REST API + SQLite
    └── python-worker/     # Complex: Async job queue worker
```

Each app includes:
- **Source code** — functional, production-style implementation
- **`project.toml`** — buildpack-specific build environment variables
- **`Procfile`** — tells the buildpack how to start the application

---

## Health Checks

All applications expose a `GET /health` endpoint that returns `200 OK`. Mikrom uses these endpoints to verify that the microVM booted successfully and the application is ready to serve traffic.

```bash
curl http://<VM_IP>:8080/health
```

---

## License

MIT
