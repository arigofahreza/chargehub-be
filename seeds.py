"""
Seed default data: notification templates + app config.
Run once (idempotent): python seeds.py
"""
from datetime import datetime
from app.database import SessionLocal
from app.models.notification import NotificationTemplate
from app.models.app_config import AppConfig
from app.utils.tz import WIB

db = SessionLocal()
try:
    templates = [
        {
            "name": "Peringatan Baterai 30%",
            "message": "⚠️ Peringatan: Baterai kendaraan Anda tersisa *30%*. Ini adalah batas minimum — segera lakukan pengisian daya untuk menghindari kehabisan baterai.",
            "status": "active",
            "category": "Alert",
        },
        {
            "name": "Baterai Hampir Penuh",
            "message": "🔋 *{{ vehicle_name }}* pengisian hampir selesai! Baterai sudah mencapai 90%. Silakan bersiap untuk mengambil kendaraan.\nDriver: {{ driver }}",
            "status": "active",
            "category": "Charging",
        },
        {
            "name": "Baterai Penuh",
            "message": "✅ *{{ vehicle_name }}* pengisian selesai! Baterai sudah 100%. Kendaraan siap digunakan.\nDriver: {{ driver }}",
            "status": "active",
            "category": "Charging",
        },
    ]
    added = 0
    for t in templates:
        if not db.query(NotificationTemplate).filter(NotificationTemplate.name == t["name"]).first():
            db.add(NotificationTemplate(
                name=t["name"],
                message=t["message"],
                status=t["status"],
                category=t["category"],
                phone_count=0,
                last_sent=datetime.now(WIB),
            ))
            added += 1
    print(f"Templates: {added} inserted, {len(templates) - added} already exist.")

    config_defaults = [
        ("tariff_kwh_rupiah", "1114", "Tarif listrik per kWh dalam Rupiah"),
    ]
    cfg_added = 0
    for key, value, desc in config_defaults:
        if not db.query(AppConfig).filter(AppConfig.key == key).first():
            db.add(AppConfig(key=key, value=value, description=desc, updated_at=datetime.now(WIB)))
            cfg_added += 1
    print(f"AppConfig: {cfg_added} inserted, {len(config_defaults) - cfg_added} already exist.")

    db.commit()
    print("Done.")
finally:
    db.close()
