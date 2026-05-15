"""
Authentication tests - Milestone M1.3
"""
import pytest
import datetime
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from app.api.v1.auth import login, get_me, verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_user
from app.schemas.user import UserLogin
from app.models.user import User, UserRole
from app.core.config import settings


@pytest.mark.asyncio
async def test_password_hashing():
    """Test bcrypt password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


@pytest.mark.asyncio
async def test_create_access_token():
    """Test JWT token creation contains correct payload."""
    token = create_access_token(user_id=1)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload.get("sub") == "1"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_login_success(db_session: AsyncSession):
    """Test successful login returns valid token and user info."""
    user = User(
        username="logintest",
        password_hash=get_password_hash("testpass"),
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    data = UserLogin(username="logintest", password="testpass")
    response = await login(data=data, db=db_session)

    assert response.access_token is not None
    assert response.token_type == "bearer"
    assert response.user.username == "logintest"
    assert response.user.role == "user"
    assert response.expires_in > 0

    # Validate token can be decoded and points to correct user
    payload = jwt.decode(
        response.access_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload.get("sub") == str(user.id)


@pytest.mark.asyncio
async def test_login_wrong_password(db_session: AsyncSession):
    """Test login with wrong password returns 401."""
    user = User(
        username="wrongpasstest",
        password_hash=get_password_hash("correctpass"),
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    data = UserLogin(username="wrongpasstest", password="wrongpass")
    with pytest.raises(HTTPException) as exc_info:
        await login(data=data, db=db_session)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_login_inactive_user(db_session: AsyncSession):
    """Test login with inactive user returns 403."""
    user = User(
        username="inactivetest",
        password_hash=get_password_hash("testpass"),
        role=UserRole.USER,
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()

    data = UserLogin(username="inactivetest", password="testpass")
    with pytest.raises(HTTPException) as exc_info:
        await login(data=data, db=db_session)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_get_me_returns_user_info(db_session: AsyncSession):
    """Test /me returns current user info with correct role."""
    user = User(
        username="metest",
        password_hash=get_password_hash("testpass"),
        role=UserRole.LEADER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    response = await get_me(current_user=user)
    assert response.id == user.id
    assert response.username == "metest"
    assert response.role == "leader"
    assert response.is_active is True


@pytest.mark.asyncio
async def test_all_roles_created_correctly(db_session: AsyncSession):
    """Test database contains 3 roles and role field is correct."""
    admin = User(
        username="role_admin",
        password_hash=get_password_hash("pass"),
        role=UserRole.ADMIN,
    )
    leader = User(
        username="role_leader",
        password_hash=get_password_hash("pass"),
        role=UserRole.LEADER,
    )
    user = User(
        username="role_user",
        password_hash=get_password_hash("pass"),
        role=UserRole.USER,
    )

    db_session.add_all([admin, leader, user])
    await db_session.commit()

    assert admin.role == "admin"
    assert leader.role == "leader"
    assert user.role == "user"


from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_expired_token_rejected(db_session: AsyncSession):
    """Test expired token returns 401."""
    expire = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)
    payload = {"sub": "1", "exp": expire}
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token)
    mock_request = MagicMock()
    mock_request.query_params = {}

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request=mock_request, credentials=credentials, db=db_session)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_rejected(db_session: AsyncSession):
    """Test invalid token returns 401."""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.here")
    mock_request = MagicMock()
    mock_request.query_params = {}

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request=mock_request, credentials=credentials, db=db_session)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_missing_credentials_rejected(db_session: AsyncSession):
    """Test missing credentials returns 401."""
    mock_request = MagicMock()
    mock_request.query_params = {}

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request=mock_request, credentials=None, db=db_session)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_query_param_token_accepted(db_session: AsyncSession):
    """Test token from query param is accepted."""
    user = User(
        username="queryuser",
        password_hash="hashed",
        role=UserRole.USER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = create_access_token(user.id)
    mock_request = MagicMock()
    mock_request.query_params = {"token": token}

    result = await get_current_user(request=mock_request, credentials=None, db=db_session)
    assert result.id == user.id
