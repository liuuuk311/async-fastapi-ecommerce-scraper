from starlette_admin.contrib.sqlmodel import ModelView

from web.models.geo import Continent, Country


class ContinentView(ModelView):
    fields = [
        Continent.is_active,
        Continent.name,
    ]


class CountryView(ModelView):
    label = "Countries"
    fields = [
        Country.is_active,
        Country.name,
        Country.continent,
    ]


class ShippingZoneView(ModelView):
    pass
