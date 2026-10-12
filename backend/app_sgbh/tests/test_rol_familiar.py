from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import (
    parse_codigo_rol_familiar,
    parse_esta_activo,
    parse_nombre_rol_familiar,
    parse_rol_familiar_id,
)
from app_sgbh.services.rol_familiar import RolFamiliarService
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.rol_familiar_view import RolFamiliarListView


def test_list_returns_every_row_when_no_filter_is_sent():
    with patch('app_sgbh.services.rol_familiar.RolFamiliar') as model:
        queryset = model.objects.all.return_value
        queryset.order_by.return_value = 'rows'

        result = RolFamiliarService.list()

    assert result == 'rows'
    model.objects.all.assert_called_once_with()
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('rol_familiar_id')


def test_list_combines_filters_with_and():
    with patch('app_sgbh.services.rol_familiar.RolFamiliar') as model:
        queryset = model.objects.all.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = RolFamiliarService.list(
            rol_familiar_id=2,
            codigo='JEFE',
            nombre='jefe',
            esta_activo=True,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'rol_familiar_id': 2}),
        ((), {'codigo': 'JEFE'}),
        ((), {'nombre__ilike_pattern': text_like_pattern('jefe')}),
        ((), {'esta_activo': True}),
    ]


@pytest.mark.parametrize(
    ('parser', 'value', 'message'),
    [
        (
            parse_rol_familiar_id,
            'abc',
            'rol_familiar_id debe ser un número entero',
        ),
        (
            parse_rol_familiar_id,
            '40000',
            'rol_familiar_id debe ser un número entero',
        ),
        (
            parse_codigo_rol_familiar,
            'x' * 31,
            'codigo no debe superar 30 caracteres',
        ),
        (
            parse_nombre_rol_familiar,
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
        '/api/sgbh/roles-familiares/',
        {
            'rol_familiar_id': '2',
            'codigo': 'JEFE',
            'nombre': 'jefe',
            'esta_activo': '1',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [
        {
            'rol_familiar_id': 2,
            'codigo': 'JEFE',
            'nombre': 'Jefe de familia',
            'esta_activo': True,
        }
    ]

    with (
        patch(
            'app_sgbh.views.rol_familiar_view.RolFamiliarService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.rol_familiar_view.RolFamiliarSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = RolFamiliarListView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    list_rows.assert_called_once_with(
        rol_familiar_id=2,
        codigo='JEFE',
        nombre='jefe',
        esta_activo=True,
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/roles-familiares/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.rol_familiar_view.RolFamiliarService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.rol_familiar_view.RolFamiliarSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = RolFamiliarListView.as_view()(request)

    assert response.status_code == 200
    list_rows.assert_called_once_with(
        rol_familiar_id=None,
        codigo=None,
        nombre=None,
        esta_activo=None,
    )


def test_get_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/roles-familiares/',
        {'rol_familiar_id': 'x'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = RolFamiliarListView.as_view()(request)

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro rol_familiar_id debe ser un número entero'
    )
