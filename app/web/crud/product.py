from fastapi.encoders import jsonable_encoder
from sqlmodel.ext.asyncio.session import AsyncSession

from web.crud.base import CRUDBase
from web.models.product import Product
from web.models.schemas import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    async def merge(self, db: AsyncSession, *, obj_in: ProductCreate) -> Product:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        await db.merge(db_obj)
        # await db.refresh(db_obj)
        return db_obj


crud_product = CRUDProduct(Product)
