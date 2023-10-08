from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.contrib.sqlmodel import Admin

from web.admin.auth import MyAuthProvider
from web.admin.geo import ContinentView, CountryView, ShippingZoneView
from web.admin.import_query import ImportQueryView
from web.admin.product import ProductView, BrandView
from web.admin.shipping import ShippingMethodView
from web.admin.store import StoreView, SuggestedStoreView, StoreSitemapView
from web.admin.tracking import ClickedProductView
from web.core.config import settings
from web.db import engine
from web.db.base import *
from web.main import app
from web.models.geo import Continent, Country, ShippingZone
from web.models.shipping import ShippingMethod
from web.models.store import SuggestedStore, StoreSitemap
from web.models.tracking import ClickedProduct

admin = Admin(
    engine,
    # base_url="/secret-admin-panel",
    title=settings.PROJECT_NAME,
    auth_provider=MyAuthProvider(),
    middlewares=[
        # Middleware(HTTPSRedirectMiddleware),
        Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY),
    ],
)

# Add view
admin.add_view(BrandView(model=Brand))
admin.add_view(ProductView(model=Product))
admin.add_view(ClickedProductView(model=ClickedProduct))
admin.add_view(StoreView(model=Store))
admin.add_view(StoreSitemapView(model=StoreSitemap))
admin.add_view(SuggestedStoreView(model=SuggestedStore))
admin.add_view(ShippingMethodView(model=ShippingMethod))
admin.add_view(ContinentView(model=Continent))
admin.add_view(CountryView(model=Country))
admin.add_view(ShippingZoneView(model=ShippingZone))

# Mount admin to your app
admin.mount_to(app)
