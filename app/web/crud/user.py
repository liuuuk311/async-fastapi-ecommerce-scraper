from typing import Optional

from web.core.security import verify_password
from web.models.user import User
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


class CRUDUser:
    @staticmethod
    async def get_by_email(db: AsyncSession, *, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return (await db.execute(stmt)).scalar_one_or_none()

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        _user: User = await self.get_by_email(db, email=email)
        if not _user:
            return None
        if not verify_password(password, _user.password):
            return None
        return _user

    async def authenticate_for_admin(
        self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        _user = await self.authenticate(db, email=email, password=password)
        if not _user or not _user.is_superuser:
            return None

        return _user


user_crud = CRUDUser()
