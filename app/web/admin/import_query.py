from web.models.import_query import ImportQuery
from starlette_admin.contrib.sqlmodel import ModelView


class ImportQueryView(ModelView):
    fields = [
        ImportQuery.is_active,
        ImportQuery.text,
        ImportQuery.priority,
        ImportQuery.products_clicks,
        ImportQuery.priority_score,
        ImportQuery.brand,
    ]
    exclude_fields_from_create = [
        ImportQuery.products_clicks,
        ImportQuery.priority_score,
        ImportQuery.created_at,
    ]
    exclude_fields_from_edit = [
        ImportQuery.products_clicks,
        ImportQuery.priority_score,
        ImportQuery.created_at,
    ]
