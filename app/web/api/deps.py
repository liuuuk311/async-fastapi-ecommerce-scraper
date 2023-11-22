from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status
from starlette.requests import Request

from web.core.config import settings
from web.core.security import verify_access_token
from web.manager.user import UserManager
from web.db import engine
from web.logger import get_logger
from web.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/token")
logger = get_logger(__name__)

optional_oauth2_schema = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/token", auto_error=False
)


async def get_db():
    async with AsyncSession(engine) as session:
        yield session


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token)
    if not token_data:
        raise credentials_exception

    user = await UserManager.get_by_email(db, email=token_data.email, get_settings=True)

    if user is None:
        raise credentials_exception

    return user


async def current_user_or_none(
    token: Annotated[Optional[str], Depends(optional_oauth2_schema)] = None,
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not token:
        return

    token_data = verify_access_token(token)
    if not token_data:
        return

    user = await UserManager.get_by_email(db, email=token_data.email)

    if user is None:
        return

    if not user.is_active:
        return

    if not user.is_email_verified:
        return

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    if not current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not verified"
        )

    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't have enough privileges",
        )
    return current_user
