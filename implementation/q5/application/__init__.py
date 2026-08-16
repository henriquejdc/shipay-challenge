from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import application.app as create_user_app_module
from application.database import Base
from application.models import Role


def test_create_user_api_creates_user_with_auto_generated_password(tmp_path, monkeypatch):
    db_path = Path(tmp_path) / "test_create_user.db"
    engine = create_engine(f"sqlite:///{db_path}")
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    with TestingSessionLocal() as session:
        session.add(Role(id=1, description="admin"))
        session.commit()

    monkeypatch.setattr(create_user_app_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(create_user_app_module.Settings, "API_TOKEN", "create_user-secret-token")
    client = TestClient(create_user_app_module.app)

    response = client.post(
        "/v1/users",
        json={"name": "Maria", "email": "maria@example.com", "role_id": 1},
        headers={"Authorization": "Bearer create_user-secret-token"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Maria"
    assert payload["email"] == "maria@example.com"
    assert payload["auto_generated_password"] is True


def test_create_user_api_rejects_duplicate_email(tmp_path, monkeypatch):
    db_path = Path(tmp_path) / "test_create_user_dup.db"
    engine = create_engine(f"sqlite:///{db_path}")
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    with TestingSessionLocal() as session:
        session.add(Role(id=1, description="admin"))
        session.commit()

    monkeypatch.setattr(create_user_app_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(create_user_app_module.Settings, "API_TOKEN", "create_user-secret-token")
    client = TestClient(create_user_app_module.app)

    first = client.post(
        "/v1/users",
        json={"name": "Maria", "email": "maria@example.com", "role_id": 1},
        headers={"Authorization": "Bearer create_user-secret-token"},
    )
    second = client.post(
        "/v1/users",
        json={"name": "Maria 2", "email": "maria@example.com", "role_id": 1},
        headers={"Authorization": "Bearer create_user-secret-token"},
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_create_user_api_rejects_missing_token(tmp_path, monkeypatch):
    db_path = Path(tmp_path) / "test_create_user_missing_token.db"
    engine = create_engine(f"sqlite:///{db_path}")
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(engine)

    with TestingSessionLocal() as session:
        session.add(Role(id=1, description="admin"))
        session.commit()

    monkeypatch.setattr(create_user_app_module, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(create_user_app_module.Settings, "API_TOKEN", "create_user-secret-token")
    client = TestClient(create_user_app_module.app)

    response = client.post(
        "/v1/users",
        json={"name": "Maria", "email": "maria@example.com", "role_id": 1},
    )

    assert response.status_code == 401

