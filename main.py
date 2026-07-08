from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time
import uuid

EMAIL = "24f2001122@ds.study.iitm.ac.in"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()

REQUEST_COUNTER = Counter(
    "http_requests_total",
    "Total HTTP Requests"
)

logs = []


@app.middleware("http")
async def log_requests(request: Request, call_next):
    REQUEST_COUNTER.inc()

    request_id = str(uuid.uuid4())

    logs.append({
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id
    })

    if len(logs) > 500:
        logs.pop(0)

    response = await call_next(request)
    return response


@app.get("/work")
def work(n: int = 1):
    x = 0
    for i in range(n):
        x += 1

    return {
        "email": EMAIL,
        "done": n
    }


@app.get("/healthz")
def health():
    return {
        "status": "ok",
        "uptime_s": time.time() - START_TIME
    }


@app.get("/logs/tail")
def tail(limit: int = 10):
    return logs[-limit:]


@app.get("/metrics")
def metrics():
    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST
    )
