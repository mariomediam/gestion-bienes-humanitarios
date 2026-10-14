from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import (
    parse_categoria_medio_vida_id,
    parse_codigo_categoria_medio_vida,
    parse_esta_activo,
    parse_nombre_categoria_medio_vida,
)
from app_sgbh.services.categoria_medio_vida import CategoriaMedioVidaService
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.categoria_medio_vida_view import CategoriaMedioVidaListView


def test_list_returns_every_row_when_no_filter_is_sent():
    with patch('app_sgbh.services.categoria_medio_vida.CategoriaMedioVida') as model:
        queryset = model.objects.all.return_value
        queryset.order_by.return_value = 'rows'

        result = CategoriaMedioVidaService.list()

    assert result == 'rows'
    model.objects.all.assert_called_once_with()
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('categoria_medio_vida_id')


def test_list_combines_filters_with_and():
    with patch('app_sgbh.services.categoria_medio_vida.CategoriaMedioVida') as model:
        queryset = model.objects.all.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = CategoriaMedioVidaService.list(
            categoria_medio_vida_id=2,
            codigo='AGRO',
            nombre='agricola',
            esta_activo=True,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'categoria_medio_vida_id': 2}),
        ((), {'codigo': 'AGRO'}),
        ((), {'nombre__ilike_pattern': text_like_pattern('agricola')}),
        ((), {'esta_activo': True}),
    ]


@pytest.mark.parametrize(
    ('parser', 'value', 'message'),
    [
        (
            parse_categoria_medio_vida_id,
            'abc',
            'categoria_medio_vida_id debe ser un número entero',
        ),
        (
            parse_categoria_medio_vida_id,
            '40000',
            'categoria_medio_vida_id debe ser un número entero',
        ),
        (
            parse_codigo_categoria_medio_vida,
            'x' * 31,
            'codigo no debe superar 30 caracteres',
        ),
        (
            parse_nombre_categoria_medio_vida,
            'x' * 101,
            'nombre no debe superar 100 caracteres',
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
        '/api/sgbh/categorias-medios-vida/',
        {
            'categoria_medio_vida_id': '2',
            'codigo': 'AGRO',
            'nombre': 'agricola',
            'esta_activo': '1',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [
        {
            'categoria_medio_vida_id': 2,
            'codigo': 'AGRO',
            'nombre': 'Agrícola',
            'esta_activo': True,
        }
    ]

    with (
        patch(
            'app_sgbh.views.categoria_medio_vida_view.CategoriaMedioVidaService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.categoria_medio_vida_view.CategoriaMedioVidaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = CategoriaMedioVidaListView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    list_rows.assert_called_once_with(
        categoria_medio_vida_id=2,
        codigo='AGRO',
        nombre='agricola',
        esta_activo=True,
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/categorias-medios-vida/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.categoria_medio_vida_view.CategoriaMedioVidaService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.categoria_medio_vida_view.CategoriaMedioVidaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = CategoriaMedioVidaListView.as_view()(request)

    assert response.status_code == 200
    list_rows.assert_called_once_with(
        categoria_medio_vida_id=None,
        codigo=None,
        nombre=None,
        esta_activo=None,
    )


def test_get_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/categorias-medios-vida/',
        {'categoria_medio_vida_id': 'x'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = CategoriaMedioVidaListView.as_view()(request)

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro categoria_medio_vida_id debe ser un número entero'
    )
