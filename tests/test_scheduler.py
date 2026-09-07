from unittest.mock import patch, MagicMock, call
from datetime import datetime, timezone
import json
from app.services.scheduler import dispatch_due_schedules


def make_schedule(chat_ids=None, template_msg="Hello {{ driver }}", driver="Budi"):
    schedule = MagicMock()
    schedule.id = "sched-1"
    schedule.template_id = "tmpl-1"
    schedule.activity_id = "act-1"
    schedule.status = "pending"
    schedule.get_target_list.return_value = chat_ids or ["111", "222"]

    template = MagicMock()
    template.message = template_msg
    template.name = "Test Template"

    activity = MagicMock()
    activity.vehicle_name = "Tesla"
    activity.vehicle_id = "VH-1"
    activity.driver = driver
    activity.supervisor = None
    activity.service_type = "Charging"
    activity.status = "completed"
    activity.date_time = datetime(2026, 9, 7, 10, 0)
    activity.km_driven = 0
    activity.energy_kwh = 0
    activity.duration_minutes = 0

    return schedule, template, activity


def test_dispatch_sends_to_all_targets():
    schedule, template, activity = make_schedule()

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = [schedule]
    mock_db.query.return_value.filter.return_value.first.side_effect = [template, activity]

    with patch("app.services.scheduler.SessionLocal", return_value=mock_db), \
         patch("app.services.scheduler.send_telegram_message", return_value=True) as mock_send, \
         patch("app.services.scheduler.render_notification", return_value="Hello Budi") as mock_render:
        dispatch_due_schedules()

    assert mock_send.call_count == 2
    mock_send.assert_any_call("111", "Hello Budi")
    mock_send.assert_any_call("222", "Hello Budi")


def test_dispatch_marks_schedule_sent():
    schedule, template, activity = make_schedule()

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = [schedule]
    mock_db.query.return_value.filter.return_value.first.side_effect = [template, activity]

    with patch("app.services.scheduler.SessionLocal", return_value=mock_db), \
         patch("app.services.scheduler.send_telegram_message", return_value=True), \
         patch("app.services.scheduler.render_notification", return_value="msg"):
        dispatch_due_schedules()

    assert schedule.status == "sent"
    mock_db.commit.assert_called()


def test_dispatch_marks_failed_when_all_sends_fail():
    schedule, template, activity = make_schedule()

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = [schedule]
    mock_db.query.return_value.filter.return_value.first.side_effect = [template, activity]

    with patch("app.services.scheduler.SessionLocal", return_value=mock_db), \
         patch("app.services.scheduler.send_telegram_message", return_value=False), \
         patch("app.services.scheduler.render_notification", return_value="msg"):
        dispatch_due_schedules()

    assert schedule.status == "failed"
