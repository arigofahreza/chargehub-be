"""Seed operational user accounts (pengawas, operator eksa, operator WL)."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User
from app.auth import hash_password

ACCOUNTS = [
    # ── PENGAWAS ────────────────────────────────────────────────────
    ("jepri_victor",         "Jepri",      "Victor",         "pengawas"),
    ("khoirul_anam",         "Khoirul",    "Anam",           "pengawas"),
    ("andis_purnomo",        "Andis",      "Purnomo",        "pengawas"),
    ("heri_p_sitompul",      "Heri",       "P Sitompul",     "pengawas"),
    ("aditya_aldy",          "Aditya",     "Aldy",           "pengawas"),
    ("fransiskus_agung",     "Fransiskus", "Agung",          "pengawas"),
    ("rony_gunawan",         "Rony",       "Gunawan",        "pengawas"),

    # ── OPERATOR EKSKAVATOR ─────────────────────────────────────────
    ("noor_faizal",          "Noor",       "Faizal",         "operator"),
    ("deni_januardi",        "Deni",       "Januardi",       "operator"),
    ("m_yahya_ari_rusandy",  "M Yahya",    "Ari Rusandy",    "operator"),
    ("ari_wibowo",           "Ari",        "Wibowo",         "operator"),
    ("hasan",                "Hasan",      "",               "operator"),
    ("adrian_tarno",         "Adrian",     "Tarno",          "operator"),

    # ── OPERATOR WHEEL LOADER ───────────────────────────────────────
    ("asa_zakaria_habibi",   "Asa",        "Zakaria Habibi", "operator"),
    ("pedro",                "Pedro",      "",               "operator"),
    ("angga_irawan",         "Angga",      "Irawan",         "operator"),
    ("ikhwal_ramadhan",      "Ikhwal",     "Ramadhan",       "operator"),
    ("agung_prasetyo",       "Agung",      "Prasetyo",       "operator"),
    ("fauzi_fathur_rohim",   "Fauzi",      "Fathur Rohim",   "operator"),
    ("beni_wijaya",          "Beni",       "Wijaya",         "operator"),
    ("okta_matius_noellik",  "Okta",       "Matius Noellik", "operator"),
    ("bayu_segara",          "Bayu",       "Segara",         "operator"),
    ("bambang_hartanto",     "Bambang",    "Hartanto",       "operator"),
]

DEFAULT_PASSWORD = "Chargehub@123"


def seed_accounts():
    db = SessionLocal()
    created = 0
    skipped = 0
    try:
        for username, first_name, last_name, role in ACCOUNTS:
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                skipped += 1
                continue
            db.add(User(
                username=username,
                hashed_password=hash_password(DEFAULT_PASSWORD),
                first_name=first_name,
                last_name=last_name,
                role=role,
            ))
            created += 1
        db.commit()
        print(f"Done. {created} akun dibuat, {skipped} dilewati (sudah ada).")
    finally:
        db.close()


if __name__ == "__main__":
    seed_accounts()
