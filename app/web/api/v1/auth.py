import hashlib
import secrets
from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select
from starlette import status
from starlette.responses import JSONResponse

from web.api import deps
from web.core.config import settings
from web.core.security import (
    create_access_token,
    hash_password,
    verify_access_token,
    json_response_with_access_tokens,
)
from web.crud.user import UserManager
from web.logger import get_logger
from web.models.schemas import Token, RequestResetPassword, ResetPassword
from web.models.user import PasswordResetToken, RefreshToken, User
from web.notifications.email import EmailNotification

router = APIRouter()

logger = get_logger(__name__)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(deps.get_db),
):
    user = await UserManager.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="wrong-credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="inactive-user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # If the user has a refresh token, delete it
    stmt = select(RefreshToken).where(RefreshToken.user_id == user.id)
    refresh_token = (await db.execute(stmt)).scalar_one_or_none()
    if refresh_token:
        await db.delete(refresh_token)

    return await json_response_with_access_tokens(db, user)


@router.get("/refresh", status_code=status.HTTP_200_OK)
async def get_new_access_token(
    db: AsyncSession = Depends(deps.get_db),
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    # 0. Get refresh token from cookies
    if not refresh_token:
        raise credentials_exception

    # 1. Verify refresh token
    token_data = verify_access_token(refresh_token)

    if not token_data:
        raise credentials_exception

    stmt = (
        select(RefreshToken)
        .join(User)
        .where(
            RefreshToken.refresh_token == refresh_token, User.email == token_data.email
        )
    )
    token_exists = (await db.execute(stmt)).scalar_one_or_none()

    if not token_exists:
        raise credentials_exception

    # 2. Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": token_data.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def create_user(
    current_user: Annotated[User, Depends(deps.get_current_active_user)],
    db: AsyncSession = Depends(deps.get_db),
):
    stmt = select(RefreshToken).where(RefreshToken.user_id == current_user.id)
    refresh_token = (await db.execute(stmt)).scalar_one_or_none()

    if not refresh_token:
        logger.debug(f"No refresh token found for {current_user}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Refresh token not found"
        )

    await db.delete(refresh_token)
    await db.commit()
    response = JSONResponse(content={"status": "ok"})
    response.set_cookie(
        key="refresh_token",
        value="",
        httponly=True,
        path="/",
        expires=datetime.min.replace(tzinfo=timezone.utc),
    )
    return response


@router.post("/reset-password")
async def request_reset_password(
    data: RequestResetPassword, db: AsyncSession = Depends(deps.get_db)
):
    user = await UserManager.get_by_email(db, email=data.email)

    if not user:
        logger.warning("Attempted to reset password for user that does not exist")
        return {"status": "ok"}

    token = secrets.token_urlsafe()
    reset_token = PasswordResetToken(
        user=user, token=hashlib.sha256(token.encode("utf-8")).hexdigest()
    )
    db.add(reset_token)
    await db.commit()
    await EmailNotification.send_reset_password(to=data.email, token=token)
    return {"status": "ok"}


@router.post("/reset-password/{token}")
async def reset_password(
    token: str, data: ResetPassword, db: AsyncSession = Depends(deps.get_db)
):
    stmt = (
        select(PasswordResetToken)
        .where(
            PasswordResetToken.token
            == hashlib.sha256(token.encode("utf-8")).hexdigest()
        )
        .options(selectinload(PasswordResetToken.user))
    )
    token: PasswordResetToken = (await db.execute(stmt)).scalar_one_or_none()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="reset-password-token-invalid",
        )

    if token.expiration_date < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="reset-password-token-expired",
        )

    stmt = select(RefreshToken).where(RefreshToken.user_id == token.user_id)
    user_sessions = (await db.execute(stmt)).scalars().all()
    for user_session in user_sessions:
        await db.delete(user_session)  # Invalidate all existing sessions

    await db.delete(token)
    token.user.password = hash_password(data.password)
    return await json_response_with_access_tokens(db, token.user)
