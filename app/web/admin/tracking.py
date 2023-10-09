from starlette_admin.contrib.sqlmodel import ModelView


class ClickedProductView(ModelView):
    fields_default_sort = [("created_at", True)]
    exclude_fields_from_list = [
        "id",
        "page",
        "ip_address",
        "client_continent",
    ]
