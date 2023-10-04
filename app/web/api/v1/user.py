from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from web.api import deps
from web.api.deps import get_current_active_user
from web.crud.user import EmailAlreadyInUseException, UserManager
from web.logger import get_logger
from web.models.schemas import UserRead, UserCreate
from web.models.user import User

router = APIRouter()

logger = get_logger(__name__)


@router.get("/users/me", response_model=UserRead)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@router.post("/users", response_model=UserRead)
async def create_user(data: UserCreate, db: AsyncSession = Depends(deps.get_db)):
    try:
        return await UserManager.create(db, data=data)
    except EmailAlreadyInUseException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use"
        )
