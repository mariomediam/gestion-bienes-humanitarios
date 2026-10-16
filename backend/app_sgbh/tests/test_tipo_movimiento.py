from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import (
    parse_codigo_tipo_movimiento,
    parse_esta_activo,
    parse_naturaleza_tipo_movimiento,
    parse_nombre_tipo_movimiento,
    parse_requiere_movimiento_origen,
    parse_tipo_movimiento_id,
)
from app_sgbh.services.tipo_movimiento import TipoMovimientoService
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.tipo_movimiento_view import TipoMovimientoListView


def test_list_returns_every_row_when_no_filter_is_sent():
    with patch('app_sgbh.services.tipo_movimiento.TipoMovimiento') as model:
        queryset = model.objects.all.return_value
        queryset.order_by.return_value = 'rows'

        result = TipoMovimientoService.list()

    assert result == 'rows'
    model.objects.all.assert_called_once_with()
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('nombre')


def test_list_combines_filters_with_and():
    with patch('app_sgbh.services.tipo_movimiento.TipoMovimiento') as model:
        queryset = model.objects.all.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = TipoMovimientoService.list(
            tipo_movimiento_id=2,
            codigo='PRESTAMO',
            nombre='préstamo',
            naturaleza='S',
            requiere_movimiento_origen=False,
            esta_activo=True,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'tipo_movimiento_id': 2}),
        ((), {'codigo': 'PRESTAMO'}),
        ((), {'nombre__ilike_pattern': text_like_pattern('préstamo')}),
        ((), {'naturaleza': 'S'}),
        ((), {'requiere_movimiento_origen': False}),
        ((), {'esta_activo': True}),
    ]


@pytest.mark.parametrize(
    ('parser', 'value', 'message'),
    [
        (
            parse_tipo_movimiento_id,
            'abc',
            'tipo_movimiento_id debe ser un número entero',
        ),
        (
            parse_tipo_movimiento_id,
            '40000',
            'tipo_movimiento_id debe ser un número entero',
        ),
        (
            parse_codigo_tipo_movimiento,
            'x' * 51,
            'codigo no debe superar 50 caracteres',
        ),
        (
            parse_nombre_tipo_movimiento,
            'x' * 151,
            'nombre no debe superar 150 caracteres',
        ),
        (
            parse_naturaleza_tipo_movimiento,
            'X',
            'naturaleza debe ser E, S o M',
        ),
        (
            parse_requiere_movimiento_origen,
            'si',
            'requiere_movimiento_origen debe ser 1, 0, true o false',
        ),
        (parse_esta_activo, 'si', 'esta_activo debe ser 1, 0, true o false'),
    ],
)
def test_parsers_reject_invalid_filters(parser, value, message):
    _parsed, error = parser(value)

    assert error is not None
    assert message in error


def test_naturaleza_parser_accepts_lowercase():
    value, error = parse_naturaleza_tipo_movimiento('m')

    assert error is None
    assert value == 'M'


def test_get_returns_rows_when_filters_are_combined():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/tipos-movimiento/',
        {
            'tipo_movimiento_id': '2',
            'codigo': 'PRESTAMO',
            'nombre': 'préstamo',
            'naturaleza': 's',
            'requiere_movimiento_origen': '0',
            'esta_activo': '1',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [
        {
            'tipo_movimiento_id': 2,
            'codigo': 'PRESTAMO',
            'nombre': 'Préstamo',
            'naturaleza': 'S',
            'requiere_movimiento_origen': False,
            'esta_activo': True,
        }
    ]

    with (
        patch(
            'app_sgbh.views.tipo_movimiento_view.TipoMovimientoService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.tipo_movimiento_view.TipoMovimientoSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = TipoMovimientoListView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    list_rows.assert_called_once_with(
        tipo_movimiento_id=2,
        codigo='PRESTAMO',
        nombre='préstamo',
        naturaleza='S',
        requiere_movimiento_origen=False,
        esta_activo=True,
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/tipos-movimiento/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.tipo_movimiento_view.TipoMovimientoService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.tipo_movimiento_view.TipoMovimientoSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = TipoMovimientoListView.as_view()(request)

    assert response.status_code == 200
    list_rows.assert_called_once_with(
        tipo_movimiento_id=None,
        codigo=None,
        nombre=None,
        naturaleza=None,
        requiere_movimiento_origen=None,
        esta_activo=None,
    )


def test_get_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/tipos-movimiento/',
        {'tipo_movimiento_id': 'x'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = TipoMovimientoListView.as_view()(request)

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro tipo_movimiento_id debe ser un número entero'
    )
