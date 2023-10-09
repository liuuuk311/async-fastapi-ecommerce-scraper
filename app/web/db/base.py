# Import all the models, so that Base has them before being imported by Alembic
from web.db.base_class import Base  # noqa
from web.models.product import Product, Brand  # noqa
from web.models.shipping import ShippingMethod  # noqa
from web.models.store import Store  # noqa
from web.models.tracking import ClickedProduct  # noqa
from web.models.user import User  # noqa
