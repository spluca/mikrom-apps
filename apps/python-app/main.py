from fastapi import FastAPI
import datetime
import os
import socket

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "Hello from Python (FastAPI) - Optimized for Firecracker",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "host": socket.gethostname()
    }

@app.get("/health")
async def health():
    return {"status": "OK"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
