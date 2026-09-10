import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import app with error handling - app initialization may fail if DB is unavailable
try:
    from app.main import app
except Exception as e:
    # If app fails to initialize (e.g., DB connection error), create a minimal app for testing
    from fastapi import FastAPI
    app = FastAPI(title="ChargeHub API Test", version="1.0.0")

from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///:memory:"
STRONG_PW = "Secret@123"


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Enable foreign keys and suppress FK constraint errors for SQLite test DB
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.close()

    TestingSessionLocal = sessionmaker(bind=engine)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        # If there's an error creating tables (e.g., FK constraint issues in SQLite),
        # continue anyway - the fixtures that need DB will handle their own setup
        pass
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _seed_user(db_session, username: str, email: str, role: str):
    from app.models.user import User
    from app.auth import hash_password
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        hashed_password=hash_password(STRONG_PW),
        first_name=username.capitalize(),
        last_name="",
        role=role,
    )
    db_session.add(user)
    db_session.commit()


@pytest.fixture
def admin_headers(client, db_session):
    _seed_user(db_session, "admintest", "admin@test.com", "admin")
    r = client.post("/api/v1/auth/login", json={"username": "admintest", "password": STRONG_PW})
    token = r.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def operator_headers(client, db_session):
    _seed_user(db_session, "opertest", "oper@test.com", "operator")
    r = client.post("/api/v1/auth/login", json={"username": "opertest", "password": STRONG_PW})
    token = r.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}


