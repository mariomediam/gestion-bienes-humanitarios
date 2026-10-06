from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import (
    parse_codigo_formulario_material_piso,
    parse_esta_activo,
    parse_material_piso_id,
    parse_nombre_material_piso,
)
from app_sgbh.services.material_piso import MaterialPisoService
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.material_piso_view import MaterialPisoListView


def test_list_returns_every_row_when_no_filter_is_sent():
    with patch('app_sgbh.services.material_piso.MaterialPiso') as model:
        queryset = model.objects.all.return_value
        queryset.order_by.return_value = 'rows'

        result = MaterialPisoService.list()

    assert result == 'rows'
    model.objects.all.assert_called_once_with()
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('nombre')


def test_list_combines_filters_with_and():
    with patch('app_sgbh.services.material_piso.MaterialPiso') as model:
        queryset = model.objects.all.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = MaterialPisoService.list(
            material_piso_id=2,
            codigo_formulario=3,
            nombre='cemento',
            esta_activo=True,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'material_piso_id': 2}),
        ((), {'codigo_formulario': 3}),
        ((), {'nombre__ilike_pattern': text_like_pattern('cemento')}),
        ((), {'esta_activo': True}),
    ]


@pytest.mark.parametrize(
    ('parser', 'value', 'message'),
    [
        (
            parse_material_piso_id,
            'abc',
            'material_piso_id debe ser un número entero',
        ),
        (
            parse_material_piso_id,
            '40000',
            'material_piso_id debe ser un número entero',
        ),
        (
            parse_codigo_formulario_material_piso,
            'abc',
            'codigo_formulario debe ser un número entero',
        ),
        (
            parse_nombre_material_piso,
            'x' * 201,
            'nombre no debe superar 200 caracteres',
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
        '/api/sgbh/materiales-piso/',
        {
            'material_piso_id': '2',
            'codigo_formulario': '3',
            'nombre': 'cemento',
            'esta_activo': '1',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [
        {
            'material_piso_id': 2,
            'codigo_formulario': 3,
            'nombre': 'Cemento',
            'esta_activo': True,
        }
    ]

    with (
        patch(
            'app_sgbh.views.material_piso_view.MaterialPisoService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.material_piso_view.MaterialPisoSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = MaterialPisoListView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    list_rows.assert_called_once_with(
        material_piso_id=2,
        codigo_formulario=3,
        nombre='cemento',
        esta_activo=True,
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/materiales-piso/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.material_piso_view.MaterialPisoService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.material_piso_view.MaterialPisoSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = MaterialPisoListView.as_view()(request)

    assert response.status_code == 200
    list_rows.assert_called_once_with(
        material_piso_id=None,
        codigo_formulario=None,
        nombre=None,
        esta_activo=None,
    )


def test_get_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/materiales-piso/',
        {'material_piso_id': 'x'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = MaterialPisoListView.as_view()(request)

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro material_piso_id debe ser un número entero'
    )
