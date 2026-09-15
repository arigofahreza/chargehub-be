import logging
import httpx
from app.config import settings

logger = logging.getLogger("chargehub.ml_client")

_VALID_ACTIVITIES = {"heavy_stacking", "light_stacking", "inspection", "loading"}


def normalize_activity(service_type: str) -> str | None:
    normalized = service_type.lower().strip().replace(" ", "_")
    return normalized if normalized in _VALID_ACTIVITIES else None


def get_shift(hour: int) -> str:
    return "shift_1" if 7 <= hour < 19 else "shift_2"


def predict_battery_after(
    truck_id: str,
    activity: str,
    duration_minutes: float,
    battery_before_pct: float,
    shift: str,
) -> float | None:
    url = f"{settings.ml_api_url}/predict"
    headers = {}
    if settings.ml_api_key:
        headers["X-API-Key"] = settings.ml_api_key
    payload = {
        "truck_id": truck_id,
        "activity": activity,
        "duration_minutes": duration_minutes,
        "battery_before_pct": battery_before_pct,
        "shift": shift,
    }
    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=10.0)
        if resp.status_code == 200:
            return float(resp.json().get("predicted_battery_after_pct", 0.0))
        logger.warning("ML API returned %d: %s", resp.status_code, resp.text[:200])
    except Exception as exc:
        logger.error("ML API call failed: %s", exc)
    return None
