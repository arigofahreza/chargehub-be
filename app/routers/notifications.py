from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import require_admin
from app.models.notification import NotificationTemplate
from app.schemas.notification import NotificationTemplateCreate, NotificationTemplatePatch, NotificationTemplateOut

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"], dependencies=[Depends(require_admin)])


@router.get("")
def list_templates(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(NotificationTemplate)
    if status:
        q = q.filter(NotificationTemplate.status == status)
    if category:
        q = q.filter(NotificationTemplate.category == category)
    templates = q.all()
    return [NotificationTemplateOut.from_orm_model(t).model_dump_camel() for t in templates]


@router.get("/{template_id}")
def get_template(template_id: str, db: Session = Depends(get_db)):
    t = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return NotificationTemplateOut.from_orm_model(t).model_dump_camel()


@router.post("", status_code=201)
def create_template(body: NotificationTemplateCreate, db: Session = Depends(get_db)):
    from datetime import datetime
    last_sent_dt = datetime.fromisoformat(body.last_sent.replace("Z", "+00:00")) if body.last_sent else datetime.utcnow()
    t = NotificationTemplate(
        name=body.name, message=body.message, status=body.status,
        employee_count=body.employee_count, phone_count=body.phone_count,
        last_sent=last_sent_dt, category=body.category,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return NotificationTemplateOut.from_orm_model(t).model_dump_camel()


@router.patch("/{template_id}")
def patch_template(template_id: str, body: NotificationTemplatePatch, db: Session = Depends(get_db)):
    from datetime import datetime
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
