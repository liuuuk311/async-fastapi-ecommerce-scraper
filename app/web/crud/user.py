from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from web.core.security import verify_password, hash_password
from web.models.schemas import UserCreate
from web.models.user import User


class EmailAlreadyInUseException(Exception):
    pass


class UserManager:
    @classmethod
    async def get_by_email(cls, db: AsyncSession, *, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return (await db.execute(stmt)).scalar_one_or_none()

    @classmethod
    async def authenticate(
        cls, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        _user: User = await cls.get_by_email(db, email=email)
        if not _user:
            return None
        if not verify_password(password, _user.password):
            return None
        return _user

    @classmethod
    async def authenticate_for_admin(
        cls, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        _user = await cls.authenticate(db, email=email, password=password)
        if not _user or not _user.is_superuser:
            return None

        return _user

    @classmethod
    async def create(cls, db: AsyncSession, *, data: UserCreate) -> User:
        _user = await cls.get_by_email(db, email=data.email)
        if _user:
            raise EmailAlreadyInUseException()

        data.password = hash_password(data.password)

        user = User.from_orm(data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
