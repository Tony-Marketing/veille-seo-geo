"""Configuration Pytest."""

import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.database import Base, get_db
from backend.app.core.security import create_access_token, hash_password
from backend.app.main import app
from backend.app.models import User

DESKTOP_PATH = Path(__file__).resolve().parents[1] / "desktop"
if str(DESKTOP_PATH) not in sys.path:
    sys.path.insert(0, str(DESKTOP_PATH))


@pytest.fixture()
def db_session() -> Generator[Session]:
    """Return an isolated in-memory database session."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def admin_user(db_session: Session) -> User:
    """Create a superadmin user."""

    user = User(
        email="admin@example.com",
        password_hash=hash_password("Password123"),
        first_name="Admin",
        is_active=True,
        is_superadmin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient]:
    """Return a TestClient wired to the test database."""

    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def admin_headers(admin_user: User) -> dict[str, str]:
    """Return Authorization headers for the superadmin."""

    token = create_access_token(str(admin_user.id))
    return {"Authorization": f"Bearer {token}"}
