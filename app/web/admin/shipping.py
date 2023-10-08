from starlette_admin.contrib.sqlmodel import ModelView


class ShippingMethodView(ModelView):
    exclude_fields_from_list = [
        "created_at",
        "products",
        "min_shipping_time",
        "max_shipping_time",
        "min_price_shipping_condition",
        "is_vat_included",
        "is_weight_dependent",
    ]
    exclude_fields_from_detail = ["store", "products"]
    exclude_fields_from_edit = ["store", "products"]
    exclude_fields_from_create = ["products"]
