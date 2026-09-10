import csv
import io
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, require_permission
from app.limiter import limiter
from app.models.notification import NotificationTemplate
from app.models.notification_log import NotificationLog
from app.models.user import User
from app.schemas.notification import (
    NotificationTemplateCreate, NotificationTemplatePatch, NotificationTemplateOut,
    NotificationLogCreate, NotificationLogOut,
)

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("")
def list_templates(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(NotificationTemplate)
    if status:
        q = q.filter(NotificationTemplate.status == status)
    if category:
        q = q.filter(NotificationTemplate.category == category)
    templates = q.all()
    return [NotificationTemplateOut.from_orm_model(t).model_dump_camel() for t in templates]


@router.post("", status_code=201)
def create_template(
    body: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("notifications", "write")),
):
    last_sent_dt = datetime.fromisoformat(body.last_sent.replace("Z", "+00:00")) if body.last_sent else datetime.utcnow()
    t = NotificationTemplate(
        name=body.name, message=body.message, status=body.status,
        employee_count=0, phone_count=body.phone_count,
        last_sent=last_sent_dt, category=body.category,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return NotificationTemplateOut.from_orm_model(t).model_dump_camel()


# ── Notification Logs ────────────────────────────────────────────────
# These MUST be declared before /{template_id} to avoid wildcard capture.

@router.get("/logs/download")
@limiter.limit("1/30seconds")
def download_logs(
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("notifications", "read")),
):
    logs = db.query(NotificationLog).order_by(NotificationLog.sent_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Tanggal & Waktu", "Nomor Tujuan", "Pesan", "Status", "Template", "Catatan"])
    for log in logs:
        dt = log.sent_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        writer.writerow([
            dt.strftime("%Y-%m-%d %H:%M:%S"),
            log.to_phone,
            log.message,
            "Terkirim" if log.status == "sent" else "Gagal",
            log.template_name or "",
            log.note or "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=notification_logs.csv"},
    )


@router.get("/logs")
def list_logs(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("notifications", "read")),
):
    logs = db.query(NotificationLog).order_by(NotificationLog.sent_at.desc()).all()
    return [NotificationLogOut.from_orm(log).model_dump_camel() for log in logs]


@router.post("/logs", status_code=201)
def create_log(
    body: NotificationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("notifications", "write")),
):
    log = NotificationLog(
        to_phone=body.to_phone,
        message=body.message,
        template_id=body.template_id,
        template_name=body.template_name,
        status=body.status,
        sent_at=datetime.now(timezone.utc),
        sent_by_id=current_user.id,
        note=body.note,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return NotificationLogOut.from_orm(log).model_dump_camel()


# ── Templates (wildcard must come last) ─────────────────────────────

@router.get("/{template_id}")
def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    t = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return NotificationTemplateOut.from_orm_model(t).model_dump_camel()


@router.patch("/{template_id}")
def patch_template(
    template_id: str,
    body: NotificationTemplatePatch,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("notifications", "write")),
):
    t = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    data = body.model_dump(exclude_unset=True, by_alias=False)
    if "last_sent" in data and isinstance(data["last_sent"], str):
        data["last_sent"] = datetime.fromisoformat(data["last_sent"].replace("Z", "+00:00"))
    for key, value in data.items():
        setattr(t, key, value)
    db.commit()
    db.refresh(t)
    return NotificationTemplateOut.from_orm_model(t).model_dump_camel()
