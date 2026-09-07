import pytest
from app.models.employee import Employee

def test_employee_has_chat_id_field():
    e = Employee(
        name="Test", job_title="Driver", phone="08123",
        status="active", initials="T",
    )
    assert hasattr(e, "chat_id")
    assert e.chat_id is None

def test_employee_has_subscribed_field():
    e = Employee(
        name="Test", job_title="Driver", phone="08123",
        status="active", initials="T",
    )
    assert hasattr(e, "subscribed")
    assert e.subscribed is False
