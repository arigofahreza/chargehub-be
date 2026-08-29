import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
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
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
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
