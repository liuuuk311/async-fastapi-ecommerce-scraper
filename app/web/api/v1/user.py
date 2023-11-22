from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select
from starlette import status

from web.api import deps
from web.api.deps import get_current_active_user
from web.logger import get_logger
from web.manager.product import ProductManager
from web.manager.user import EmailAlreadyInUseException, UserManager
from web.models.product import Product
from web.models.schemas import (
    UserRead,
    UserCreate,
    UserCreateResponse,
    ProductRead,
)
from web.models.user import User, FavoriteProduct
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
    await db.refresh(user)
    await EmailNotification(db, user=user).send_email_verification(
        code=email_verification.code
    )
    return data


@router.post("/users/favorites/{product_id}")
async def toggle_product_as_favorite(
    product_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(deps.get_db),
):
    product = await ProductManager.get_product(db, public_id=product_id)
    try:
        favorite_product = FavoriteProduct(user=current_user, product=product)
        db.add(favorite_product)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        stmt = select(FavoriteProduct).where(
            FavoriteProduct.user == current_user, FavoriteProduct.product == product
        )
        favorite_product = (await db.execute(stmt)).scalar_one_or_none()
        if favorite_product:
            await db.delete(favorite_product)
            await db.commit()


@router.get("/users/favorites/{product_id}")
async def is_product_a_user_favorite(
    product_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(deps.get_db),
):
    product = await ProductManager.get_product(db, public_id=product_id)
    stmt = select(FavoriteProduct).where(
        FavoriteProduct.user == current_user, FavoriteProduct.product == product
    )
    if not bool((await db.execute(stmt)).scalar_one_or_none()):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get("/users/favorites", response_model=List[ProductRead])
async def user_favorites(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(deps.get_db),
):
    stmt = (
        select(Product)
        .join(FavoriteProduct, FavoriteProduct.product_id == Product.id)
        .where(FavoriteProduct.user_id == current_user.id)
        .options(selectinload(Product.store))
        .options(selectinload(Product.best_shipping_method))
    )
    return (await db.execute(stmt)).scalars().all()
