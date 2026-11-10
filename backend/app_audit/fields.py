"""JSON values stored as text so the audit table can live on SQL Server 2008 R2."""

import json

from django.db import models


class JsonTextField(models.TextField):
    """Persist JSON in nvarchar(max) without the ISJSON check."""

    def to_python(self, value):
        if value is None or value == '' or isinstance(value, (dict, list)):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except ValueError:
                return value
        return value

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)

    def get_prep_value(self, value):
        if value is None or isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False, default=str)
