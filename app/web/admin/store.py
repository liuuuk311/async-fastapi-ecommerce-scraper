from typing import Dict, Any, List

from web.models.store import Store
from starlette.requests import Request
from starlette_admin import RelationField, RequestAction, HasOne, action
from starlette_admin.contrib.sqlmodel import ModelView
from web.tasks.store import check_store_compatibility


class StoreView(ModelView):
    actions = ["check_compatibility", "delete"]

    searchable_fields = [
        Store.name,
        Store.website,
        Store.is_active,
        Store.is_parsable,
    ]
    exclude_fields_from_list = [
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
    ]
    exclude_fields_from_create = [
        Store.public_id,
        Store.created_at,
        Store.last_check,
        Store.products,
        Store.country,
        Store.shipping_methods,
    ]
    exclude_fields_from_edit = [
        Store.public_id,
        Store.created_at,
        Store.products,
        Store.country,
        Store.shipping_methods,
    ]
    exclude_fields_from_detail = [
        Store.products,
        Store.country,
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

    async def serialize(
        self,
        obj: Any,
        request: Request,
        action: RequestAction,
        include_relationships: bool = True,
        include_select2: bool = False,
    ) -> Dict[str, Any]:
        obj_serialized: Dict[str, Any] = {}
        for field in self.fields:
            if isinstance(field, RelationField) and include_relationships:
                value = getattr(obj, field.name, None)
                foreign_model = self._find_foreign_model(field.identity)  # type: ignore
                assert foreign_model.pk_attr is not None
                if value is None:
                    obj_serialized[field.name] = None
                elif isinstance(field, HasOne):
                    if action == RequestAction.EDIT:
                        obj_serialized[field.name] = getattr(
                            value, foreign_model.pk_attr
                        )
                    else:
                        obj_serialized[field.name] = await foreign_model.serialize(
                            value, request, action, include_relationships=False
                        )
                else:
                    if action == RequestAction.EDIT:
                        obj_serialized[field.name] = [
                            getattr(v, foreign_model.pk_attr) for v in value
                        ]
            elif not isinstance(field, RelationField):
                value = await field.parse_obj(request, obj)
                obj_serialized[field.name] = await self.serialize_field_value(
                    value, field, action, request
                )
        if include_select2:
            obj_serialized["_select2_selection"] = await self.select2_selection(
                obj, request
            )
            obj_serialized["_select2_result"] = await self.select2_result(obj, request)
        obj_serialized["_repr"] = await self.repr(obj, request)
        assert self.pk_attr is not None
        pk = getattr(obj, self.pk_attr)
        obj_serialized[self.pk_attr] = obj_serialized.get(
            self.pk_attr, str(pk)  # Make sure the primary key is always available
        )
        route_name = request.app.state.ROUTE_NAME
        obj_serialized["_detail_url"] = str(
            request.url_for(route_name + ":detail", identity=self.identity, pk=pk)
        )
        obj_serialized["_edit_url"] = str(
            request.url_for(route_name + ":edit", identity=self.identity, pk=pk)
        )
        return obj_serialized
