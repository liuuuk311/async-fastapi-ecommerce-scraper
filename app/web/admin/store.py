from starlette_admin.contrib.sqlmodel import ModelView

from web.logger import get_logger
from web.models.store import Store

logger = get_logger(__name__)


class StoreView(ModelView):
    page_size = 25
    actions = ["delete"]

    searchable_fields = [
        Store.name,
        Store.website,
        Store.is_active,
        Store.is_parsable,
        Store.affiliate_id,
    ]
    exclude_fields_from_list = [
        Store.search_link,
        Store.created_at,
        Store.public_id,
        Store.products,
        Store.country,
        Store.shipping_methods,
        Store.id,
        Store.logo,
        Store.locale,
        Store.country,
        Store.currency,
        Store.affiliate_id,
        Store.reason_could_not_be_parsed,
        Store.search_url,
        Store.search_tag,
        Store.search_class,
        Store.search_next_page,
        Store.search_page_param,
        Store.scrape_with_js,
        Store.product_name_class,
        Store.product_name_css_is_class,
        Store.product_name_tag,
        Store.product_price_class,
        Store.product_price_css_is_class,
        Store.product_price_tag,
        Store.product_image_class,
        Store.product_image_css_is_class,
        Store.product_image_tag,
        Store.product_thumb_class,
        Store.product_thumb_css_is_class,
        Store.product_thumb_tag,
        Store.product_is_available_class,
        Store.product_is_available_css_is_class,
        Store.product_is_available_tag,
        Store.product_is_available_match,
        Store.product_variations_class,
        Store.product_variations_css_is_class,
        Store.product_variations_tag,
        Store.product_description_class,
        Store.product_description_css_is_class,
        Store.product_description_tag,
        Store.country,
    ]
    exclude_fields_from_create = [
        Store.public_id,
        Store.created_at,
        Store.last_check,
        Store.products,
        Store.shipping_methods,
    ]
    exclude_fields_from_edit = [
        Store.search_link,
        Store.search_page_param,
        Store.search_next_page,
        Store.search_class,
        Store.search_tag,
        Store.search_url,
        Store.public_id,
        Store.created_at,
        Store.products,
        Store.shipping_methods,
    ]
    exclude_fields_from_detail = [
        Store.products,
        Store.shipping_methods,
    ]


class SuggestedStoreView(ModelView):
    pass


class StoreSitemapView(ModelView):
    exclude_fields_from_create = ["created_at", "is_active"]
