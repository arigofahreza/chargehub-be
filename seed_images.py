"""Upload local image assets to MinIO and update vehicle photo_url / employee avatar_url."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import mimetypes
from pathlib import Path
from app.database import SessionLocal
from app.models.vehicle import Vehicle
from app.models.employee import Employee
from app.services.storage import upload_asset

ASSETS_DIR = Path(__file__).parent.parent / "assets"

VEHICLE_IMAGES = {
    "veh-001": "vehicle-hero.jpg",
    "veh-002": "vehicle-2.jpg",
    "veh-003": "vehicle-3.jpg",
    "veh-004": "vehicle-4.jpg",
    "veh-005": "vehicle-5.jpg",
}

EMPLOYEE_AVATARS = {
    "emp-001": "avatar-emp1.jpg",
    "emp-002": "avatar-user.jpg",
    "emp-003": "avatar-user2.jpg",
}


def _upload(filename: str, prefix: str) -> str:
    path = ASSETS_DIR / filename
    data = path.read_bytes()
    content_type, _ = mimetypes.guess_type(filename)
    return upload_asset(data, content_type or "image/jpeg", Path(filename).suffix, prefix)


def seed_images():
    db = SessionLocal()
    try:
        print("Uploading vehicle photos...")
        for vid, fname in VEHICLE_IMAGES.items():
            url = _upload(fname, "vehicles")
            db.query(Vehicle).filter(Vehicle.id == vid).update({"photo_url": url})
            print(f"  {vid} ({fname}) → {url}")

        print("Uploading employee avatars...")
        for eid, fname in EMPLOYEE_AVATARS.items():
            url = _upload(fname, "employees")
            db.query(Employee).filter(Employee.id == eid).update({"avatar_url": url})
            print(f"  {eid} ({fname}) → {url}")

        db.commit()
        print("Image seed complete.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_images()
