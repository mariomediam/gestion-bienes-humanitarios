"""Reusable case-insensitive text search for SQL Server."""

import re

from django.db.models import CharField, Lookup


class CaseInsensitiveLike(Lookup):
    """Case-insensitive LIKE. The right-hand side is the full pattern."""

    lookup_name = 'ilike_pattern'

    def as_sql(self, compiler, connection):
        lhs_sql, lhs_params = self.process_lhs(compiler, connection)
        rhs_sql, rhs_params = self.process_rhs(compiler, connection)
        params = (*lhs_params, *rhs_params)
        return f'UPPER({lhs_sql}) LIKE UPPER({rhs_sql})', params


def register_text_search_lookups():
    """Register the shared text search lookup on character fields."""
    CharField.register_lookup(CaseInsensitiveLike)


def text_like_pattern(text):
    """Build a LIKE pattern with '%' at both ends and in place of whitespace.

    'Tsunami maremoto' becomes '%Tsunami%maremoto%'. Literal LIKE wildcards
    typed by the user are escaped with the SQL Server convention.
    """
    escaped = (
        text.replace('\\', '\\\\')
        .replace('[', '[[]')
        .replace('%', '[%]')
        .replace('_', '[_]')
    )
    with_gaps = re.sub(r'\s', '%', escaped)
    return f'%{with_gaps}%'


def filter_text_like(queryset, field_name, text):
    """Filter queryset by a case-insensitive LIKE on field_name.

    Spaces in text match any text between the words. The comparison does
    not distinguish uppercase from lowercase.
    """
    pattern = text_like_pattern(text)
    return queryset.filter(**{f'{field_name}__ilike_pattern': pattern})
