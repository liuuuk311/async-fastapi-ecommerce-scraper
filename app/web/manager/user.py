from datetime import datetime
from random import randint
from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from web.core.config import settings
from web.core.security import verify_password, hash_password
from web.models.product import Product
from web.models.schemas import UserCreate
from web.models.user import User, EmailVerificationCode, FavoriteProduct, UserSettings
from web.notifications.telegram import send_log_to_telegram


class EmailAlreadyInUseException(Exception):
    pass


class UserManager:
    @classmethod
    async def get_by_email(
        cls, db: AsyncSession, *, email: str, get_settings: bool = False
    ) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        if get_settings:
            stmt = stmt.options(selectinload(User.settings))
        return (await db.execute(stmt)).scalar_one_or_none()

    @classmethod
    async def authenticate(
        cls, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        _user: User = await cls.get_by_email(db, email=email)
        if not _user:
            return

        if not verify_password(password, _user.password):
            return

        return _user

    @classmethod
    async def authenticate_for_admin(
        cls, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        _user = await cls.authenticate(db, email=email, password=password)
        if not _user or not _user.is_superuser:
            return

        return _user

    @classmethod
    async def create(cls, db: AsyncSession, *, data: UserCreate) -> User:
        _user = await cls.get_by_email(db, email=data.email)
        if _user:
            raise EmailAlreadyInUseException()

        data.password = hash_password(data.password)

        user = User.from_orm(data)
        db.add(user)
        db.add(UserSettings(user=user, language=data.language))
        await db.commit()
        await db.refresh(user)
        return user

    @classmethod
    async def create_email_verification_code(
        cls, db: AsyncSession, *, user: User
    ) -> EmailVerificationCode:
        random_code = randint(10**5, (10**6) - 1)  # Create a 6 digit random code

        verification_code = EmailVerificationCode(
            user=user,
            code=random_code,
        )
        db.add(verification_code)
        await db.commit()
        await db.refresh(verification_code)
        return verification_code

    @classmethod
    async def verify_email(cls, db: AsyncSession, *, email: str, code: str) -> bool:
        stmt = (
            select(EmailVerificationCode)
            .join(User)
            .where(
                User.email == email,
                EmailVerificationCode.code == code,
                EmailVerificationCode.expiration_date >= datetime.today(),
            )
        )
        return bool((await db.execute(stmt)).scalar_one_or_none())
