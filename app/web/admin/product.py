from starlette.requests import Request
from starlette_admin.contrib.sqlmodel import ModelView

from web.models.product import Product, Brand


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
    fields = [
        Product.name,
        Product.description,
        Product.price,
        Product.currency,
        Product.image,
        Product.link,
        Product.store,
        Product.is_available,
        Product.import_date,
        Product.brand,
    ]

    exclude_fields_from_list = [
        "description",
        "image",
        "link",
        "brand",
        "import_query",
        "search_vector",
    ]
    exclude_fields_from_create = [
        "import_query",
        "search_vector",
        "clicks",
        "price_history",
    ]
    exclude_fields_from_edit = [
        "import_query",
        "search_vector",
        "clicks",
        "price_history",
    ]
    exclude_fields_from_detail = [
        "import_query",
        "search_vector",
        "clicks",
        "price_history",
    ]

    def can_create(self, request: Request) -> bool:
        return False
