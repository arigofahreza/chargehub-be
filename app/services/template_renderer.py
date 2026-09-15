from jinja2 import Environment, BaseLoader, StrictUndefined


_env = Environment(loader=BaseLoader(), undefined=StrictUndefined)


def render_notification(template_message: str, activity) -> str:
    template = _env.from_string(template_message)
    supervisor_list = (
        activity.get_supervisor_list()
        if hasattr(activity, "get_supervisor_list")
        else []
    )
    context = {
        "vehicle_name": activity.vehicle_name,
        "vehicle_id": activity.vehicle_id,
        "driver": activity.driver,
        "supervisor": ", ".join(supervisor_list),
        "supervisors": supervisor_list,
        "service_type": activity.service_type,
        "status": activity.status,
        "date_time": activity.date_time,
        "km_driven": activity.km_driven or 0,
        "energy_kwh": activity.energy_kwh or 0,
        "duration_minutes": activity.duration_minutes or 0,
        "cost_rupiah": activity.cost_rupiah or 0,
    }
    return template.render(**context)
