from datetime import timedelta, datetime
from typing import Optional, Tuple

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from web.core.config import settings
from web.logger import get_logger
from web.models.schemas import TokenData
from web.models.user import User, RefreshToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = get_logger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_access_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            return

        token_expiration: datetime = datetime.utcfromtimestamp(payload.get('exp', 0))
        if token_expiration < datetime.utcnow():
            return

        return TokenData(email=email)
    except JWTError:
        return


def create_tokens(user: User) -> Tuple[str, str]:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_access_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )
    return access_token, refresh_token


async def json_response_with_access_tokens(
    db: AsyncSession, user: User
) -> JSONResponse:
    access_token, refresh_token = create_tokens(user)

    db.add(RefreshToken(user=user, refresh_token=refresh_token))
    await db.commit()

    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        path="/",
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )
    return response
