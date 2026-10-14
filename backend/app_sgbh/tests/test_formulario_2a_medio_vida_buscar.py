from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import parse_medio_vida_id
from app_sgbh.serializers.formulario_2a_medio_vida import MedioVidaBusquedaSerializer
from app_sgbh.services.formulario_2a_medio_vida import Formulario2AMedioVidaService
from app_sgbh.views.formulario_2a_medio_vida_view import (
    Formulario2AMedioVidaBuscarView,
)


def _medio_vida(**overrides):
    tipo_medio_vida = SimpleNamespace(
        nombre='Ganado vacuno',
        codigo_formulario=4,
        categoria_medio_vida_id=2,
        categoria_medio_vida=SimpleNamespace(nombre='Pecuario'),
    )
    familia = SimpleNamespace(
        vivienda_id=4,
        vivienda=SimpleNamespace(
            formulario_2a_id=10,
            formulario_2a=SimpleNamespace(
                emergencia_id=6,
                emergencia=SimpleNamespace(codigo_sinpad='SIN-1'),
            ),
        ),
    )
    row = SimpleNamespace(
        medio_vida_id=21,
        familia_id=8,
        tipo_medio_vida_id=3,
        cantidad=12,
        observacion='Dos vacas lecheras',
        fecha_creacion=datetime(2026, 3, 1, 8, 0, tzinfo=timezone.utc),
        tipo_medio_vida=tipo_medio_vida,
        familia=familia,
    )
    for key, value in overrides.items():
        setattr(row, key, value)
    return row


def test_search_returns_every_row_when_no_filter_is_sent():
    with patch(
        'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
    ) as model:
        queryset = model.objects.select_related.return_value
        queryset.order_by.return_value = 'rows'

        result = Formulario2AMedioVidaService.search()

    assert result == 'rows'
    model.objects.select_related.assert_called_once_with(
        'tipo_medio_vida',
        'tipo_medio_vida__categoria_medio_vida',
        'familia',
        'familia__vivienda',
        'familia__vivienda__formulario_2a',
        'familia__vivienda__formulario_2a__emergencia',
    )
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('medio_vida_id')


def test_search_combines_filters_with_and():
    with patch(
        'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
    ) as model:
        queryset = model.objects.select_related.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = Formulario2AMedioVidaService.search(
            medio_vida_id=21,
            familia_id=8,
            tipo_medio_vida_id=3,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'medio_vida_id': 21}),
        ((), {'familia_id': 8}),
        ((), {'tipo_medio_vida_id': 3}),
    ]
    queryset.order_by.assert_called_once_with('medio_vida_id')


def test_serializer_returns_joined_columns():
    data = MedioVidaBusquedaSerializer(_medio_vida()).data

    assert data['medio_vida_id'] == 21
    assert data['familia_id'] == 8
    assert data['tipo_medio_vida_id'] == 3
    assert data['cantidad'] == 12
    assert data['observacion'] == 'Dos vacas lecheras'
    assert data['tipo_medio_vida_nombre'] == 'Ganado vacuno'
    assert data['tipo_medio_vida_codigo_formulario'] == 4
    assert data['categoria_medio_vida_id'] == 2
    assert data['categoria_medio_vida_nombre'] == 'Pecuario'
    assert data['vivienda_id'] == 4
    assert data['formulario_2a_id'] == 10
    assert data['emergencia_id'] == 6
    assert data['codigo_sinpad'] == 'SIN-1'


def test_serializer_returns_null_when_optional_columns_are_missing():
    row = _medio_vida()
    row.observacion = None
    row.familia.vivienda.formulario_2a.emergencia.codigo_sinpad = None

    data = MedioVidaBusquedaSerializer(row).data

    assert data['observacion'] is None
    assert data['codigo_sinpad'] is None


@pytest.mark.parametrize(
    ('value', 'message'),
    [
        ('abc', 'medio_vida_id debe ser un número entero'),
        ('2147483648', 'medio_vida_id debe ser un número entero'),
    ],
)
def test_parse_medio_vida_id_rejects_invalid_values(value, message):
    _parsed, error = parse_medio_vida_id(value)

    assert error is not None
    assert message in error


def test_get_medios_vida_buscar_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/medios-vida/buscar/',
        {'medio_vida_id': '21', 'familia_id': '8', 'tipo_medio_vida_id': '3'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'medio_vida_id': 21, 'familia_id': 8, 'tipo_medio_vida_id': 3}]

    with (
        patch(
            'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.formulario_2a_medio_vida_view.MedioVidaBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = Formulario2AMedioVidaBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        medio_vida_id=21,
        familia_id=8,
        tipo_medio_vida_id=3,
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_medios_vida_buscar_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/medios-vida/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.formulario_2a_medio_vida_view.MedioVidaBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = Formulario2AMedioVidaBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        medio_vida_id=None,
        familia_id=None,
        tipo_medio_vida_id=None,
    )


def test_get_medios_vida_buscar_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/medios-vida/buscar/',
        {'tipo_medio_vida_id': 'x'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AMedioVidaBuscarView.as_view()(request)

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro tipo_medio_vida_id debe ser un número entero'
    )
