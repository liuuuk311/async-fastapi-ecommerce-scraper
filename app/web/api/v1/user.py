from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from web.api import deps
from web.api.deps import get_current_active_user
from web.core.security import json_response_with_access_tokens
from web.crud.user import EmailAlreadyInUseException, UserManager
from web.logger import get_logger
from web.models.schemas import UserRead, UserCreate, UserCreateResponse, VerifyUserEmail
from web.models.user import User
from web.notifications.email import EmailNotification

router = APIRouter()

logger = get_logger(__name__)


@router.get("/users/me", response_model=UserRead)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.post("/users", response_model=UserCreateResponse)
async def create_user(data: UserCreate, db: AsyncSession = Depends(deps.get_db)):
    try:
        user = await UserManager.create(db, data=data)
    except EmailAlreadyInUseException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="email-already-present"
        )

    email_verification = await UserManager.create_email_verification_code(db, user=user)
    await EmailNotification.send_email_verification(
        to=data.email, code=email_verification.code
    )
    return data


@router.post("/verify-email", response_model=UserRead)
async def verify_email(data: VerifyUserEmail, db: AsyncSession = Depends(deps.get_db)):
    success = await UserManager.verify_email(db, email=data.email, code=data.code)

    if not success:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    user = await UserManager.get_by_email(db, email=data.email)
    return await json_response_with_access_tokens(db, user)
