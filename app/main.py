import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# ── Logging setup ─────────────────────────────────────────────────────────────
_fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_fmt)

logger = logging.getLogger("chargehub.api")
logger.setLevel(logging.INFO)
logger.addHandler(_console_handler)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="ChargeHub API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()

    # Prefer X-Forwarded-For (behind reverse proxy), fall back to direct client
    forwarded_for = request.headers.get("X-Forwarded-For")
    client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else (
        request.client.host if request.client else "unknown"
    )

    response = await call_next(request)

    duration_ms = round((time.perf_counter() - start) * 1000)
    logger.info(
        '%s "%s %s" %d %dms ip=%s ua="%s"',
        client_ip,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        client_ip,
        request.headers.get("user-agent", "-"),
    )

    return response


from app.routers import vehicles, employees, activities, notifications, auth, dashboard, job_titles
app.include_router(vehicles.router)
app.include_router(employees.router)
app.include_router(activities.router)
app.include_router(notifications.router)
app.include_router(auth.router)
app.include_router(auth.users_router)
app.include_router(dashboard.router)
app.include_router(job_titles.router)


@app.get("/health")
def health():
    return {"status": "ok"}
