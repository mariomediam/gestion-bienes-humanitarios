from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import (
    parse_abreviatura_unidad_medida,
    parse_codigo_unidad_medida,
    parse_esta_activo,
    parse_nombre_unidad_medida,
    parse_unidad_medida_id,
)
from app_sgbh.services.unidad_medida import UnidadMedidaService
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.unidad_medida_view import UnidadMedidaListView


def test_list_returns_every_row_when_no_filter_is_sent():
    with patch('app_sgbh.services.unidad_medida.UnidadMedida') as model:
        queryset = model.objects.all.return_value
        queryset.order_by.return_value = 'rows'

        result = UnidadMedidaService.list()

    assert result == 'rows'
    model.objects.all.assert_called_once_with()
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('nombre')


def test_list_combines_filters_with_and():
    with patch('app_sgbh.services.unidad_medida.UnidadMedida') as model:
        queryset = model.objects.all.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = UnidadMedidaService.list(
            unidad_medida_id=2,
            codigo='KG',
            nombre='kilo',
            abreviatura='kg',
            esta_activo=True,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'unidad_medida_id': 2}),
        ((), {'codigo': 'KG'}),
        ((), {'nombre__ilike_pattern': text_like_pattern('kilo')}),
        ((), {'abreviatura__ilike_pattern': text_like_pattern('kg')}),
        ((), {'esta_activo': True}),
    ]


@pytest.mark.parametrize(
    ('parser', 'value', 'message'),
    [
        (
            parse_unidad_medida_id,
            'abc',
            'unidad_medida_id debe ser un número entero',
        ),
        (
            parse_unidad_medida_id,
            '40000',
            'unidad_medida_id debe ser un número entero',
        ),
        (
            parse_codigo_unidad_medida,
            'x' * 21,
            'codigo no debe superar 20 caracteres',
        ),
        (
            parse_nombre_unidad_medida,
            'x' * 101,
            'nombre no debe superar 100 caracteres',
        ),
        (
            parse_abreviatura_unidad_medida,
            'x' * 21,
            'abreviatura no debe superar 20 caracteres',
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
        '/api/sgbh/unidades-medida/',
        {
            'unidad_medida_id': '2',
            'codigo': 'KG',
            'nombre': 'kilo',
            'abreviatura': 'kg',
            'esta_activo': '1',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [
        {
            'unidad_medida_id': 2,
            'codigo': 'KG',
            'nombre': 'Kilogramo',
            'abreviatura': 'kg',
            'esta_activo': True,
        }
    ]

    with (
        patch(
            'app_sgbh.views.unidad_medida_view.UnidadMedidaService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.unidad_medida_view.UnidadMedidaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = UnidadMedidaListView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    list_rows.assert_called_once_with(
        unidad_medida_id=2,
        codigo='KG',
        nombre='kilo',
        abreviatura='kg',
        esta_activo=True,
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/unidades-medida/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.unidad_medida_view.UnidadMedidaService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.unidad_medida_view.UnidadMedidaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = UnidadMedidaListView.as_view()(request)

    assert response.status_code == 200
    list_rows.assert_called_once_with(
        unidad_medida_id=None,
        codigo=None,
        nombre=None,
        abreviatura=None,
        esta_activo=None,
    )


def test_get_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/unidades-medida/',
        {'unidad_medida_id': 'x'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = UnidadMedidaListView.as_view()(request)

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro unidad_medida_id debe ser un número entero'
    )
