from starlette.requests import Request
from starlette_admin.contrib.sqlmodel import ModelView

from web.logger import get_logger
from web.models.product import Product, Brand

logger = get_logger(__name__)


class BrandView(ModelView):
    fields = [
        Brand.is_active,
        Brand.name,
        Brand.description,
        Brand.logo,
        Brand.is_hot,
    ]
    exclude_fields_from_list = [Brand.logo]


class ProductView(ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pk_attr = "public_id"
        self._pk_column = Product.public_id
        self._pk_coerce = str

    fields = [
        Product.name,
        Product.description,
        Product.price,
        Product.currency,
        Product.image,
        Product.link,
        Product.store,
        Product.is_available,
        Product.category,
        Product.sub_category,
    ]
    exclude_fields_from_list = [
        "description",
        "image",
        "link",
        "brand",
        "search_vector",
        "category",
        "sub_category",
    ]
    exclude_fields_from_create = [
        "search_vector",
        "clicks",
        "price_history",
    ]
    exclude_fields_from_edit = [
        "search_vector",
        "clicks",
        "price_history",
    ]
    exclude_fields_from_detail = [
        "search_vector",
        "clicks",
        "price_history",
    ]

    def can_create(self, request: Request) -> bool:
        return False


class CategoryView(ModelView):
    label = "Categories"
    fields = ["created_at", "is_active", "slug", "name", "name_it", "parent"]
    exclude_fields_from_list = ["created_at", "is_active", "parent"]
