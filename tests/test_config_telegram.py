import pytest


def test_settings_has_telegram_bot_token():
    """Test that settings has telegram_bot_token field as a string."""
    # Import here to avoid loading the app which triggers DB initialization
    from app.config import settings
    assert hasattr(settings, "telegram_bot_token")
    assert isinstance(settings.telegram_bot_token, str)


@pytest.mark.no_header
def test_telegram_bot_token_defaults_to_empty_string():
    """Test that telegram_bot_token defaults to empty string."""
    from app.config import Settings
    # Create a fresh settings instance with minimal env
    test_settings = Settings()
    assert test_settings.telegram_bot_token == ""
