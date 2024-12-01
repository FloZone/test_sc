import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.database import get_session
from src.main import app
from src.modules.users.models import Role, UserInDb
from src.security import get_current_user, hash_password


@pytest.fixture
def session():
    """Database session fixture with in memory database."""
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(session):
    """Test API client that depends on the session fixture."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client_user(session, base_user):
    """Test API client that depends on the session fixture, authenticated with 'base_user' user."""

    def get_current_user_override():
        return base_user

    def get_session_override():
        return session

    app.dependency_overrides[get_current_user] = get_current_user_override
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client_admin(session, base_admin):
    """Test API client that depends on the session fixture, authenticated with 'base_admin' user."""

    def get_current_user_override():
        return base_admin

    def get_session_override():
        return session

    app.dependency_overrides[get_current_user] = get_current_user_override
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def base_user(session) -> UserInDb:
    user = UserInDb(name="User", email="user@test.com", password=hash_password("password"))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture()
def base_admin(session) -> UserInDb:
    user = UserInDb(name="Admin", email="admin@test.com", password=hash_password("password"), role=Role.ADMIN)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
