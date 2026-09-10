from unittest.mock import patch, MagicMock
from app.services.telegram import send_telegram_message

def test_send_returns_true_on_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}

    with patch("app.services.telegram.settings.telegram_bot_token", "test-token"):
        with patch("app.services.telegram.httpx.post", return_value=mock_response):
            result = send_telegram_message("123456789", "Hello!")
    assert result is True

def test_send_returns_false_on_failure():
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"ok": False, "description": "Bad Request"}

    with patch("app.services.telegram.settings.telegram_bot_token", "test-token"):
        with patch("app.services.telegram.httpx.post", return_value=mock_response):
            result = send_telegram_message("123456789", "Hello!")
    assert result is False

def test_send_returns_false_on_exception():
    with patch("app.services.telegram.settings.telegram_bot_token", "test-token"):
        with patch("app.services.telegram.httpx.post", side_effect=Exception("network error")):
            result = send_telegram_message("123456789", "Hello!")
    assert result is False
