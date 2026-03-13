"""
Python Background Worker with HTTP API
A job queue system that accepts tasks via HTTP and processes them asynchronously.
This demonstrates stateful application packaging for Firecracker microVMs.
"""

import asyncio
import datetime
import os
import socket
import time
import uuid
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Firecracker Worker Demo",
    description="An async job queue worker — packaged for Cloud Native Buildpacks, runs on Firecracker",
    version="1.0.0",
)

# In-memory job store (in production this would be Redis or a database)
JOBS: dict = {}


class JobRequest(BaseModel):
    task: str
    payload: Optional[dict] = {}


class Job(BaseModel):
    id: str
    task: str
    payload: dict
    status: str  # "pending" | "running" | "done" | "failed"
    result: Optional[str] = None
    created_at: str
    updated_at: str


def simulate_work(job_id: str, task: str, payload: dict):
    """Simulate processing time for different task types."""
    JOBS[job_id]["status"] = "running"
    JOBS[job_id]["updated_at"] = datetime.datetime.utcnow().isoformat()

    try:
        if task == "compute":
            # CPU-bound simulation
            count = int(payload.get("count", 100))
            result = sum(i * i for i in range(count))
            time.sleep(0.1)
            JOBS[job_id]["result"] = f"Sum of squares 0..{count} = {result}"

        elif task == "echo":
            # Simple echo task
            time.sleep(0.05)
            JOBS[job_id]["result"] = f"Echo: {payload.get('message', 'no message')}"

        elif task == "wait":
            # Simulate a slow I/O task
            duration = float(payload.get("seconds", 1))
            time.sleep(min(duration, 5))  # Cap at 5 seconds for safety
            JOBS[job_id]["result"] = f"Waited {duration}s successfully"

        else:
            JOBS[job_id]["status"] = "failed"
            JOBS[job_id]["result"] = f"Unknown task type: {task}"
            return

        JOBS[job_id]["status"] = "done"

    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["result"] = str(e)
    finally:
        JOBS[job_id]["updated_at"] = datetime.datetime.utcnow().isoformat()


@app.post("/jobs", status_code=202)
async def submit_job(req: JobRequest, background_tasks: BackgroundTasks):
    """Submit a job to the queue. Returns immediately with the job ID."""
    job_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow().isoformat()
    JOBS[job_id] = {
        "id": job_id,
        "task": req.task,
        "payload": req.payload,
        "status": "pending",
        "result": None,
        "created_at": now,
        "updated_at": now,
    }
    background_tasks.add_task(simulate_work, job_id, req.task, req.payload)
    return {"job_id": job_id, "status": "pending"}


@app.get("/jobs")
async def list_jobs():
    """List all jobs and their current status."""
    return list(JOBS.values())


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get the status and result of a specific job."""
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.delete("/jobs/{job_id}", status_code=204)
async def delete_job(job_id: str):
    """Remove a completed job from the queue."""
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    JOBS.pop(job_id)


@app.get("/health")
async def health():
    return {
        "status": "OK",
        "host": socket.gethostname(),
        "jobs_in_queue": len(JOBS),
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


@app.get("/")
async def root():
    return {
        "message": "Python Worker — Packaged for Firecracker via Cloud Native Buildpacks",
        "docs": "/docs",
        "health": "/health",
        "submit_job": "POST /jobs",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
