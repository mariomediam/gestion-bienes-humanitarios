from datetime import date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers.kardex import AlmacenKardexBusquedaSerializer
from app_sgbh.services.kardex import AlmacenKardexService, _inicio_de_dia
from app_sgbh.views.kardex_view import AlmacenKardexBuscarView, _parse_busqueda


def test_parse_busqueda_omits_every_filter_when_params_are_empty():
    parsed, error = _parse_busqueda({})

    assert error is None
    assert parsed == {
        'almacen_id': None,
        'estado_movimiento': None,
        'bien_id': None,
        'fecha_desde': None,
        'fecha_hasta': None,
    }


def test_parse_busqueda_accepts_several_filters_together():
    parsed, error = _parse_busqueda(
        {
            'fecha_desde': '2026-01-01',
            'fecha_hasta': '2026-03-31',
            'almacen_id': '2',
            'estado_movimiento': ' CONFIRMADO ',
            'bien_id': '4',
        }
    )

    assert error is None
    assert parsed == {
        'almacen_id': 2,
        'estado_movimiento': 'CONFIRMADO',
        'bien_id': 4,
        'fecha_desde': date(2026, 1, 1),
        'fecha_hasta': date(2026, 3, 31),
    }


@pytest.mark.parametrize(
    ('params', 'message'),
    [
        ({'almacen_id': 'abc'}, 'almacen_id debe ser un número entero'),
        ({'bien_id': 'x'}, 'bien_id debe ser un número entero'),
        ({'fecha_desde': '01-03-2026'}, 'fecha_desde debe tener el formato AAAA-MM-DD'),
        ({'fecha_hasta': '31/03/2026'}, 'fecha_hasta debe tener el formato AAAA-MM-DD'),
        (
            {'estado_movimiento': 'A' * 31},
            'estado_movimiento no debe superar 30 caracteres',
        ),
    ],
)
def test_parse_busqueda_rejects_invalid_filters(params, message):
    _parsed, error = _parse_busqueda(params)

    assert error is not None
    assert message in error


def test_search_returns_every_row_when_no_filter_is_sent():
    queryset = MagicMock()
    queryset.order_by.return_value = 'rows'

    with patch('app_sgbh.services.kardex.AlmacenKardex') as model:
        model.objects.all.return_value = queryset
        result = AlmacenKardexService.search()

    assert result == 'rows'
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with(
        'fecha_movimiento',
        'movimiento_detalle_id',
    )


def test_search_combines_filters_with_and():
    queryset = MagicMock()
    queryset.filter.return_value = queryset
    queryset.order_by.return_value = 'rows'

    with patch('app_sgbh.services.kardex.AlmacenKardex') as model:
        model.objects.all.return_value = queryset
        result = AlmacenKardexService.search(
            fecha_desde=date(2026, 1, 1),
            fecha_hasta=date(2026, 3, 31),
            almacen_id=2,
            estado_movimiento='CONFIRMADO',
            bien_id=4,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'fecha_movimiento__gte': _inicio_de_dia(date(2026, 1, 1))}),
        (
            (),
            {
                'fecha_movimiento__lt': _inicio_de_dia(
                    date(2026, 3, 31) + timedelta(days=1)
                )
            },
        ),
        ((), {'almacen_id': 2}),
        ((), {'estado_movimiento': 'CONFIRMADO'}),
        ((), {'bien_id': 4}),
    ]
    queryset.order_by.assert_called_once_with(
        'fecha_movimiento',
        'movimiento_detalle_id',
    )


def _kardex_row():
    return SimpleNamespace(
        movimiento_id=10,
        almacen_id=2,
        fecha_movimiento=timezone.make_aware(datetime(2026, 3, 1, 8, 30)),
        tipo_movimiento_id=3,
        tipo_movimiento_codigo='SALIDA',
        tipo_movimiento='Salida',
        naturaleza='S',
        estado_movimiento='CONFIRMADO',
        movimiento_origen_id=8,
        documento_referencia='GR-001',
        movimiento_detalle_id=21,
        bien_id=4,
        cantidad=Decimal('-2.500000'),
        cantidad_texto='2 1/2',
        es_devolvible=True,
        detalle_observacion='Prestado',
        movimiento_observacion='Entrega parcial',
    )


def test_serializer_returns_view_columns():
    data = AlmacenKardexBusquedaSerializer(_kardex_row()).data

    assert data == {
        'movimiento_id': 10,
        'almacen_id': 2,
        'fecha_movimiento': '2026-03-01T08:30:00-05:00',
        'tipo_movimiento_id': 3,
        'tipo_movimiento_codigo': 'SALIDA',
        'tipo_movimiento': 'Salida',
        'naturaleza': 'S',
        'estado_movimiento': 'CONFIRMADO',
        'movimiento_origen_id': 8,
        'documento_referencia': 'GR-001',
        'movimiento_detalle_id': 21,
        'bien_id': 4,
        'cantidad': '-2.500000',
        'cantidad_texto': '2 1/2',
        'es_devolvible': True,
        'detalle_observacion': 'Prestado',
        'movimiento_observacion': 'Entrega parcial',
    }


def test_serializer_returns_null_optional_columns():
    row = _kardex_row()
    row.movimiento_origen_id = None
    row.documento_referencia = None
    row.cantidad_texto = None
    row.detalle_observacion = None
    row.movimiento_observacion = None

    data = AlmacenKardexBusquedaSerializer(row).data

    assert data['movimiento_origen_id'] is None
    assert data['documento_referencia'] is None
    assert data['cantidad_texto'] is None
    assert data['detalle_observacion'] is None
    assert data['movimiento_observacion'] is None


def test_get_returns_rows_when_filters_are_sent():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/kardex/buscar/',
        {
            'fecha_desde': '2026-01-01',
            'fecha_hasta': '2026-03-31',
            'almacen_id': '2',
            'estado_movimiento': 'CONFIRMADO',
            'bien_id': '4',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'movimiento_detalle_id': 21}]

    with (
        patch(
            'app_sgbh.views.kardex_view.AlmacenKardexService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.kardex_view.AlmacenKardexBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = AlmacenKardexBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        almacen_id=2,
        estado_movimiento='CONFIRMADO',
        bien_id=4,
        fecha_desde=date(2026, 1, 1),
        fecha_hasta=date(2026, 3, 31),
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/kardex/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.kardex_view.AlmacenKardexService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.kardex_view.AlmacenKardexBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = AlmacenKardexBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == []
    search.assert_called_once_with(
        almacen_id=None,
        estado_movimiento=None,
        bien_id=None,
        fecha_desde=None,
        fecha_hasta=None,
    )


def test_get_rejects_fecha_desde_after_fecha_hasta():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/kardex/buscar/',
        {'fecha_desde': '2026-04-01', 'fecha_hasta': '2026-03-01'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = AlmacenKardexBuscarView.as_view()(request)

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro fecha_desde no puede ser posterior a fecha_hasta'
    )


def test_get_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/kardex/buscar/', {'bien_id': 'x'})
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = AlmacenKardexBuscarView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El filtro bien_id debe ser un número entero'


def test_get_returns_500_when_the_query_fails():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/kardex/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.kardex_view.AlmacenKardexService.search',
        side_effect=Exception('db'),
    ):
        response = AlmacenKardexBuscarView.as_view()(request)

    assert response.status_code == 500
    assert response.data['error'] == 'No se pudo obtener la búsqueda del kardex de almacén'
