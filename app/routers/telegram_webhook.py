import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.employee import Employee
from app.services.telegram import send_telegram_message

logger = logging.getLogger("chargehub.telegram_webhook")

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


@router.post("/webhook")
async def telegram_webhook(request: Request, db: Session = Depends(get_db)):
    if settings.telegram_webhook_secret:
        incoming = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if incoming != settings.telegram_webhook_secret:
            logger.warning("Webhook rejected: invalid secret token from %s", request.client.host if request.client else "unknown")
            return {"ok": True}
    try:
        data = await request.json()
    except Exception:
        return {"ok": True}

    message = data.get("message") or data.get("edited_message")
    if not message:
        return {"ok": True}

    chat_id = str(message.get("chat", {}).get("id", ""))
    text = (message.get("text") or "").strip()

    if not chat_id or not text:
        return {"ok": True}

    if text.startswith("/subscribe"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            send_telegram_message(chat_id, "Format salah. Gunakan: /subscribe <TOKEN>")
            return {"ok": True}

        token = parts[1].strip().upper()
        employee = db.query(Employee).filter(Employee.subscribe_token == token).first()

        if not employee:
            send_telegram_message(chat_id, "Token tidak valid atau sudah digunakan. Minta token baru ke admin.")
            return {"ok": True}

        employee.chat_id = chat_id
        employee.subscribed = True
        employee.subscribe_token = None
        db.commit()

        send_telegram_message(
            chat_id,
            f"Berhasil! Akun {employee.name} sekarang terdaftar untuk menerima notifikasi AMEV."
        )
        return {"ok": True}

    if text == "/unsubscribe":
        employee = db.query(Employee).filter(Employee.chat_id == chat_id).first()
        if employee:
            employee.subscribed = False
            db.commit()
            send_telegram_message(chat_id, f"Akun {employee.name} berhenti menerima notifikasi.")
        else:
            send_telegram_message(chat_id, "Akun tidak ditemukan.")
        return {"ok": True}

    if text == "/status":
        employee = db.query(Employee).filter(Employee.chat_id == chat_id).first()
        if employee and employee.subscribed:
            send_telegram_message(chat_id, f"Status: Aktif. Notifikasi dikirim ke akun {employee.name}.")
        else:
            send_telegram_message(chat_id, "Status: Tidak aktif. Hubungi admin untuk mendapat token.")
        return {"ok": True}

    return {"ok": True}
