import hashlib
import secrets
from datetime import timedelta, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select
from starlette import status

from web.api import deps
from web.core.config import settings
from web.core.security import create_access_token, hash_password
from web.crud.user import UserManager
from web.logger import get_logger
from web.models.schemas import Token, RequestResetPassword, ResetPassword
from web.models.user import PasswordResetToken
from web.notifications.email import EmailNotification

router = APIRouter()

logger = get_logger(__name__)


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
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


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
            detail="The token provided is not valid",
        )

    if token.expiration_date < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The token provided is expired",
        )

    token.user.password = hash_password(data.password)
    await db.commit()
    return {"status": "ok"}
