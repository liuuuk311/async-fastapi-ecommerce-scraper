from typing import Any, List

from starlette.requests import Request
from starlette_admin import action
from starlette_admin.contrib.sqlmodel import ModelView

from web.models.store import Store
from web.tasks.store import check_store_compatibility


class StoreView(ModelView):
    page_size = 25
    actions = ["check_compatibility", "delete"]

    searchable_fields = [
        Store.name,
        Store.website,
        Store.is_active,
        Store.is_parsable,
        Store.affiliate_id,
    ]
    exclude_fields_from_list = [
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
        Store.scrape_with_js,
        Store.search_url,
        Store.search_tag,
        Store.search_class,
        Store.search_link,
        Store.search_next_page,
        Store.search_page_param,
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
        Store.public_id,
        Store.created_at,
        Store.products,
        Store.shipping_methods,
    ]
    exclude_fields_from_detail = [
        Store.products,
        Store.shipping_methods,
    ]

    @action(
        name="check_compatibility",
        text="Check store compatibility",
        confirmation="Are you sure you want to check the compatibility for the selected stores?",
        submit_btn_text="Yes, proceed",
        submit_btn_class="btn-success",
    )
    async def make_published_action(self, request: Request, pks: List[Any]) -> str:
        await check_store_compatibility([int(pk) for pk in pks])
        return f"{len(pks)} stores were checked for compatibility"


class SuggestedStoreView(ModelView):
    pass
