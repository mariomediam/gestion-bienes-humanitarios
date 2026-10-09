from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import parse_familia_id
from app_sgbh.serializers.formulario_2a_familia import FamiliaBusquedaSerializer
from app_sgbh.services.formulario_2a_familia import Formulario2AFamiliaService
from app_sgbh.views.formulario_2a_familia_view import Formulario2AFamiliaBuscarView


def test_search_returns_every_row_when_no_filter_is_sent():
    with patch(
        'app_sgbh.services.formulario_2a_familia.Formulario2AFamilia'
    ) as model:
        queryset = model.objects.select_related.return_value
        queryset.order_by.return_value = 'rows'

        result = Formulario2AFamiliaService.search()

    assert result == 'rows'
    model.objects.select_related.assert_called_once_with(
        'vivienda',
        'vivienda__formulario_2a',
    )
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with(
        'vivienda__numero_orden',
        'numero_orden',
    )


def test_search_combines_filters_with_and():
    with patch(
        'app_sgbh.services.formulario_2a_familia.Formulario2AFamilia'
    ) as model:
        queryset = model.objects.select_related.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = Formulario2AFamiliaService.search(
            familia_id=33,
            vivienda_id=8,
            formulario_2a_id=10,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'familia_id': 33}),
        ((), {'vivienda_id': 8}),
        ((), {'vivienda__formulario_2a_id': 10}),
    ]
    queryset.order_by.assert_called_once_with(
        'vivienda__numero_orden',
        'numero_orden',
    )


def test_serializer_returns_formulario_from_the_parent_vivienda():
    familia = SimpleNamespace(
        familia_id=33,
        vivienda_id=8,
        numero_orden=2,
        fecha_creacion=datetime(2026, 3, 1, 8, 0, tzinfo=timezone.utc),
        vivienda=SimpleNamespace(formulario_2a_id=10),
    )

    data = FamiliaBusquedaSerializer(familia).data

    assert data['familia_id'] == 33
    assert data['vivienda_id'] == 8
    assert data['numero_orden'] == 2
    assert data['formulario_2a_id'] == 10


@pytest.mark.parametrize(
    ('value', 'message'),
    [
        ('abc', 'familia_id debe ser un número entero'),
        ('2147483648', 'familia_id debe ser un número entero'),
    ],
)
def test_parse_familia_id_rejects_invalid_values(value, message):
    _parsed, error = parse_familia_id(value)

    assert error is not None
    assert message in error


def test_get_familias_buscar_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/familias/buscar/',
        {'familia_id': '33', 'vivienda_id': '8', 'formulario_2a_id': '10'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'familia_id': 33, 'vivienda_id': 8, 'formulario_2a_id': 10}]

    with (
        patch(
            'app_sgbh.views.formulario_2a_familia_view.Formulario2AFamiliaService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.formulario_2a_familia_view.FamiliaBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = Formulario2AFamiliaBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        familia_id=33,
        vivienda_id=8,
        formulario_2a_id=10,
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_familias_buscar_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/familias/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.formulario_2a_familia_view.Formulario2AFamiliaService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.formulario_2a_familia_view.FamiliaBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = Formulario2AFamiliaBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        familia_id=None,
        vivienda_id=None,
        formulario_2a_id=None,
    )


def test_get_familias_buscar_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/familias/buscar/',
        {'familia_id': 'x'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AFamiliaBuscarView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El filtro familia_id debe ser un número entero'
