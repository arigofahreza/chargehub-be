import logging
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.models.notification_schedule import NotificationSchedule
from app.models.notification import NotificationTemplate
from app.models.activity import ActivityLog
from app.models.notification_log import NotificationLog
from app.services.telegram import send_telegram_message
from app.services.template_renderer import render_notification

logger = logging.getLogger("chargehub.scheduler")

scheduler = BackgroundScheduler()


def dispatch_due_schedules() -> None:
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        due = (
            db.query(NotificationSchedule)
            .filter(
                NotificationSchedule.status == "pending",
                NotificationSchedule.send_at <= now,
            )
            .all()
        )

        for schedule in due:
            template = (
                db.query(NotificationTemplate)
                .filter(NotificationTemplate.id == schedule.template_id)
                .first()
            )
            activity = (
                db.query(ActivityLog)
                .filter(ActivityLog.id == schedule.activity_id)
                .first()
            )

            if not template or not activity:
                logger.warning("Schedule %s missing template or activity, skipping", schedule.id)
                schedule.status = "failed"
                db.commit()
                continue

            try:
                rendered_message = render_notification(template.message, activity)
            except Exception as exc:
                logger.error("Template render failed for schedule %s: %s", schedule.id, exc)
                schedule.status = "failed"
                db.commit()
                continue

            targets = schedule.get_target_list()
            results = []
            for chat_id in targets:
                success = send_telegram_message(chat_id, rendered_message)
                results.append(success)
                log = NotificationLog(
                    to_phone=chat_id,
                    message=rendered_message,
                    template_id=schedule.template_id,
                    template_name=template.name,
                    status="sent" if success else "failed",
                    note=f"schedule_id={schedule.id}",
                )
                db.add(log)

            schedule.status = "sent" if any(results) else "failed"
            db.commit()
            logger.info(
                "Schedule %s processed: %d/%d sent",
                schedule.id, sum(results), len(results)
            )
    except Exception as exc:
        logger.error("dispatch_due_schedules error: %s", exc)
        db.rollback()
    finally:
        db.close()
