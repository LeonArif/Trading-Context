import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db

# Use in-memory sqlite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create schema for tests
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client():
    # override dependency
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def test_token_wrong_password(client):
    resp = client.post(
        "/api/token", data={"username": "LeonArif", "password": "wrongpass"}
    )
    assert resp.status_code == 401


def test_token_wrong_username(client):
    resp = client.post(
        "/api/token", data={"username": "WrongUser", "password": "password123"}
    )
    assert resp.status_code == 401
