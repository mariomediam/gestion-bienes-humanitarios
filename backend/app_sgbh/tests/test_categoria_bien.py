from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import (
    parse_categoria_bien_id,
    parse_codigo_categoria_bien,
    parse_esta_activo,
    parse_nombre_categoria_bien,
    parse_orden_categoria_bien,
)
from app_sgbh.services.categoria_bien import CategoriaBienService
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.categoria_bien_view import CategoriaBienListView


def test_list_returns_every_row_when_no_filter_is_sent():
    with patch('app_sgbh.services.categoria_bien.CategoriaBien') as model:
        queryset = model.objects.all.return_value
        queryset.order_by.return_value = 'rows'

        result = CategoriaBienService.list()

    assert result == 'rows'
    model.objects.all.assert_called_once_with()
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('orden')


def test_list_combines_filters_with_and():
    with patch('app_sgbh.services.categoria_bien.CategoriaBien') as model:
        queryset = model.objects.all.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = CategoriaBienService.list(
            categoria_bien_id=2,
            codigo='ALIM',
            nombre='alimento',
            orden=1,
            esta_activo=True,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'categoria_bien_id': 2}),
        ((), {'codigo': 'ALIM'}),
        ((), {'nombre__ilike_pattern': text_like_pattern('alimento')}),
        ((), {'orden': 1}),
        ((), {'esta_activo': True}),
    ]


@pytest.mark.parametrize(
    ('parser', 'value', 'message'),
    [
        (
            parse_categoria_bien_id,
            'abc',
            'categoria_bien_id debe ser un número entero',
        ),
        (
            parse_categoria_bien_id,
            '40000',
            'categoria_bien_id debe ser un número entero',
        ),
        (
            parse_codigo_categoria_bien,
            'x' * 31,
            'codigo no debe superar 30 caracteres',
        ),
        (
            parse_nombre_categoria_bien,
            'x' * 101,
            'nombre no debe superar 100 caracteres',
        ),
        (
            parse_orden_categoria_bien,
            'abc',
            'orden debe ser un número entero',
        ),
        (parse_esta_activo, 'si', 'esta_activo debe ser 1, 0, true o false'),
    ],
)
def test_parsers_reject_invalid_filters(parser, value, message):
    _parsed, error = parser(value)

    assert error is not None
    assert message in error


def test_get_returns_rows_when_filters_are_combined():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/categorias-bienes/',
        {
            'categoria_bien_id': '2',
            'codigo': 'ALIM',
            'nombre': 'alimento',
            'orden': '1',
            'esta_activo': '1',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [
        {
            'categoria_bien_id': 2,
            'codigo': 'ALIM',
            'nombre': 'Alimentos',
            'orden': 1,
            'esta_activo': True,
        }
    ]

    with (
        patch(
            'app_sgbh.views.categoria_bien_view.CategoriaBienService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.categoria_bien_view.CategoriaBienSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = CategoriaBienListView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    list_rows.assert_called_once_with(
        categoria_bien_id=2,
        codigo='ALIM',
        nombre='alimento',
        orden=1,
        esta_activo=True,
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/categorias-bienes/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.categoria_bien_view.CategoriaBienService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.categoria_bien_view.CategoriaBienSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = CategoriaBienListView.as_view()(request)

    assert response.status_code == 200
    list_rows.assert_called_once_with(
        categoria_bien_id=None,
        codigo=None,
        nombre=None,
        orden=None,
        esta_activo=None,
    )


def test_get_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/categorias-bienes/',
        {'categoria_bien_id': 'x'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = CategoriaBienListView.as_view()(request)

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro categoria_bien_id debe ser un número entero'
    )
