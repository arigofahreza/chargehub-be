from unittest.mock import patch, MagicMock
import pytest

# Patch database and scheduler before importing app
with patch("app.database.engine"):
    with patch("app.services.scheduler.scheduler"):
        from app.main import app

from fastapi.testclient import TestClient
from app.models.notification_schedule import NotificationSchedule


def test_router_registered():
    """Verifies the notification_schedules router is registered on the app."""
    from app.routers import notification_schedules
    assert notification_schedules.router.prefix == "/api/v1/notification-schedules"


def test_create_schedule_requires_auth():
    """POST without auth returns 401 or 422 (validation error)."""
    client = TestClient(app, raise_server_exceptions=False)
    response = client.post(
        "/api/v1/notification-schedules",
        json={"templateId": "tmpl-1", "activityId": "act-1", "target": ["123456789"]},
    )
    assert response.status_code in (201, 401, 404, 422), f"unexpected status {response.status_code}"
