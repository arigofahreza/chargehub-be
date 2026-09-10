from jinja2 import Environment, BaseLoader, StrictUndefined


_env = Environment(loader=BaseLoader(), undefined=StrictUndefined)


def render_notification(template_message: str, activity) -> str:
    template = _env.from_string(template_message)
    context = {
        "vehicle_name": activity.vehicle_name,
        "vehicle_id": activity.vehicle_id,
        "driver": activity.driver,
        "supervisor": activity.supervisor or "",
        "service_type": activity.service_type,
        "status": activity.status,
        "date_time": activity.date_time,
        "km_driven": activity.km_driven or 0,
        "energy_kwh": activity.energy_kwh or 0,
        "duration_minutes": activity.duration_minutes or 0,
    }
    return template.render(**context)
