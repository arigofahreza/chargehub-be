import json
from app.models.notification_schedule import NotificationSchedule

def test_notification_schedule_has_required_fields():
    s = NotificationSchedule()
    for field in ["id", "template_id", "activity_id", "target", "created_at", "send_at", "status"]:
        assert hasattr(s, field), f"missing field: {field}"

def test_notification_schedule_status_default():
    s = NotificationSchedule()
    assert s.status == "pending"
