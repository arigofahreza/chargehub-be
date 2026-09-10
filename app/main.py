import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.database import engine, Base
from app.limiter import limiter
# Import all models to register them with Base.metadata
from app.models import Vehicle, Employee, ActivityLog, NotificationTemplate, NotificationLog, NotificationSchedule, User, VehicleCategory, EmployeeCategory, BatteryDrainRate  # noqa: F401
from app.services.scheduler import scheduler, dispatch_due_schedules

# ── Logging setup ─────────────────────────────────────────────────────────────
_fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_fmt)

logger = logging.getLogger("chargehub.api")
logger.setLevel(logging.INFO)
logger.addHandler(_console_handler)


# ── Lifespan ──────────────────────────────────────────────────────────────────
def _seed_notification_templates(db_session):
    from datetime import datetime
    templates = [
        {
            "name": "Peringatan Baterai 30%",
            "message": "⚠️ Peringatan: Baterai kendaraan Anda tersisa *30%*. Ini adalah batas minimum — segera lakukan pengisian daya untuk menghindari kehabisan baterai.",
            "status": "active",
            "category": "Alert",
        },
        {
            "name": "Baterai Hampir Penuh",
            "message": "🔋 Baterai kendaraan Anda sudah *85% terisi* (tersisa 15% lagi untuk penuh). Silakan bersiap — kendaraan akan segera siap digunakan.",
            "status": "active",
            "category": "Reminder",
        },
    ]
    for t in templates:
        exists = db_session.query(NotificationTemplate).filter(NotificationTemplate.name == t["name"]).first()
        if not exists:
            db_session.add(NotificationTemplate(
                name=t["name"],
                message=t["message"],
                status=t["status"],
                category=t["category"],
                phone_count=0,
                last_sent=datetime.utcnow(),
            ))
    db_session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        _seed_notification_templates(db)
    finally:
        db.close()
    scheduler.add_job(dispatch_due_schedules, "interval", minutes=5, id="telegram_broadcast")
    scheduler.start()
    logger.info("Scheduler started — telegram_broadcast every 5 minutes")
    yield
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="ChargeHub API", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Database ──────────────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# Add subscribe_token column if not exists (backward compat for existing DBs)
from sqlalchemy import text, inspect as sa_inspect
_insp = sa_inspect(engine)
if "employees" in _insp.get_table_names():
    _cols = [c["name"] for c in _insp.get_columns("employees")]
    if "subscribe_token" not in _cols:
        with engine.connect() as _conn:
            _conn.execute(text("ALTER TABLE employees ADD COLUMN subscribe_token VARCHAR"))
            _conn.commit()

from app.rbac.enforcer import get_enforcer as _get_enforcer
_get_enforcer()  # warm up enforcer + create casbin_rule table if missing


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


from app.routers import vehicles, employees, activities, notifications, auth, dashboard, job_titles, users, categories, notification_schedules, telegram_webhook
app.include_router(vehicles.router)
app.include_router(employees.router)
app.include_router(activities.router)
app.include_router(notifications.router)
app.include_router(notification_schedules.router)
app.include_router(auth.router)
app.include_router(auth.users_router)
app.include_router(dashboard.router)
app.include_router(job_titles.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(telegram_webhook.router)


@app.get("/health")
def health():
    return {"status": "ok"}
