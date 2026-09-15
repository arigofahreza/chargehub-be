import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from app.utils.tz import WIB
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
        now = datetime.now(WIB)
        due = (
            db.query(NotificationSchedule)
            .filter(
                NotificationSchedule.status == "pending",
                NotificationSchedule.send_at.isnot(None),
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
                schedule.send_at = None
                db.commit()
                continue

            try:
                rendered_message = render_notification(template.message, activity)
            except Exception as exc:
                logger.error("Template render failed for schedule %s: %s", schedule.id, exc)
                schedule.status = "failed"
                schedule.send_at = None
                db.commit()
                continue

            targets = schedule.get_target_list()
            if not targets:
                logger.warning("Schedule %s has no targets, marking failed", schedule.id)
                schedule.status = "failed"
                schedule.send_at = None
                db.commit()
                continue
            results = []
            for chat_id in targets:
                success = send_telegram_message(chat_id, rendered_message)
                results.append(success)

            # Commit schedule status FIRST — prevents re-dispatch even if log insert fails
            schedule.status = "sent" if any(results) else "failed"
            schedule.send_at = None
            db.commit()
            logger.info(
                "Schedule %s processed: %d/%d sent",
                schedule.id, sum(results), len(results)
            )

            # Insert logs separately — FK may fail if template was deleted/replaced
            for chat_id, success in zip(targets, results):
                try:
                    log = NotificationLog(
                        to_phone=chat_id,
                        message=rendered_message,
                        template_id=template.id,
                        template_name=template.name,
                        status="sent" if success else "failed",
                        note=f"schedule_id={schedule.id}",
                    )
                    db.add(log)
                    db.commit()
                except Exception as log_exc:
                    db.rollback()
                    logger.error("Failed to insert notification_log for schedule %s: %s", schedule.id, log_exc)
    except Exception as exc:
        logger.error("dispatch_due_schedules error: %s", exc)
        db.rollback()
    finally:
        db.close()
