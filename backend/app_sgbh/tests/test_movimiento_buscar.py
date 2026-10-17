from datetime import date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from django.db.models import Prefetch
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers.movimiento import MovimientoBusquedaSerializer
from app_sgbh.services.movimiento import MovimientoService, _inicio_de_dia
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.movimiento_view import MovimientoBuscarView, _parse_busqueda


def test_parse_busqueda_omits_every_filter_when_params_are_empty():
    parsed, error = _parse_busqueda({})

    assert error is None
    assert parsed == {
        'movimiento_id': None,
        'almacen_id': None,
        'tipo_movimiento_id': None,
        'estado_movimiento_id': None,
        'movimiento_origen_id': None,
        'documento_referencia': None,
        'destinatario': None,
        'observacion': None,
        'encargado_almacen_id': None,
        'fecha_desde': None,
        'fecha_hasta': None,
    }


def test_parse_busqueda_accepts_several_filters_together():
    parsed, error = _parse_busqueda(
        {
            'movimiento_id': '10',
            'almacen_id': '2',
            'tipo_movimiento_id': '3',
            'estado_movimiento_id': '1',
            'movimiento_origen_id': '8',
            'fecha_desde': '2026-01-01',
            'fecha_hasta': '2026-03-31',
            'documento_referencia': ' GR-001 ',
            'destinatario': ' Municipalidad ',
            'observacion': 'Entrega parcial',
            'encargado_almacen_id': '4',
        }
    )

    assert error is None
    assert parsed == {
        'movimiento_id': 10,
        'almacen_id': 2,
        'tipo_movimiento_id': 3,
        'estado_movimiento_id': 1,
        'movimiento_origen_id': 8,
        'documento_referencia': 'GR-001',
        'destinatario': 'Municipalidad',
        'observacion': 'Entrega parcial',
        'encargado_almacen_id': 4,
        'fecha_desde': date(2026, 1, 1),
        'fecha_hasta': date(2026, 3, 31),
    }


@pytest.mark.parametrize(
    ('params', 'message'),
    [
        ({'movimiento_id': 'abc'}, 'movimiento_id debe ser un número entero'),
        ({'almacen_id': 'abc'}, 'almacen_id debe ser un número entero'),
        ({'tipo_movimiento_id': 'abc'}, 'tipo_movimiento_id debe ser un número entero'),
        (
            {'estado_movimiento_id': 'x'},
            'estado_movimiento_id debe ser un número entero',
        ),
        (
            {'movimiento_origen_id': 'abc'},
            'movimiento_origen_id debe ser un número entero',
        ),
        (
            {'encargado_almacen_id': '99999'},
            'encargado_almacen_id debe ser un número entero',
        ),
        ({'fecha_desde': '01-03-2026'}, 'fecha_desde debe tener el formato AAAA-MM-DD'),
        ({'fecha_hasta': '31/03/2026'}, 'fecha_hasta debe tener el formato AAAA-MM-DD'),
        (
            {'documento_referencia': 'a' * 101},
            'documento_referencia no debe superar 100 caracteres',
        ),
        (
            {'destinatario': 'a' * 251},
            'destinatario no debe superar 250 caracteres',
        ),
        (
            {'observacion': 'a' * 1001},
            'observacion no debe superar 1000 caracteres',
        ),
    ],
)
def test_parse_busqueda_rejects_invalid_filters(params, message):
    _parsed, error = _parse_busqueda(params)

    assert error is not None
    assert message in error


def test_search_returns_every_row_when_no_filter_is_sent():
    queryset = MagicMock()
    queryset.prefetch_related.return_value = queryset
    queryset.order_by.return_value = 'rows'

    with patch('app_sgbh.services.movimiento.Movimiento') as movimiento:
        movimiento.objects.select_related.return_value = queryset
        result = MovimientoService.search()

    assert result == 'rows'
    movimiento.objects.select_related.assert_called_once_with(
        'almacen',
        'tipo_movimiento',
        'estado_movimiento',
        'encargado_almacen',
    )
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('-fecha_movimiento')


def test_search_prefetches_one_detail_list_per_movement():
    queryset = MagicMock()
    queryset.prefetch_related.return_value = queryset
    queryset.order_by.return_value = 'rows'
    detalle_qs = MagicMock()
    detalle_qs.order_by.return_value = 'detalles'

    with (
        patch('app_sgbh.services.movimiento.Movimiento') as movimiento,
        patch('app_sgbh.services.movimiento.MovimientoDetalle') as detalle,
    ):
        movimiento.objects.select_related.return_value = queryset
        detalle.objects.select_related.return_value = detalle_qs
        MovimientoService.search()

    detalle.objects.select_related.assert_called_once_with(
        'bien',
        'bien__unidad_medida',
    )
    detalle_qs.order_by.assert_called_once_with('movimiento_detalle_id')
    prefetch = queryset.prefetch_related.call_args.args[0]
    assert isinstance(prefetch, Prefetch)
    assert prefetch.prefetch_through == 'detalles'
    assert prefetch.queryset == 'detalles'


def test_search_combines_filters_with_and():
    queryset = MagicMock()
    queryset.prefetch_related.return_value = queryset
    queryset.filter.return_value = queryset
    queryset.order_by.return_value = 'rows'

    with patch('app_sgbh.services.movimiento.Movimiento') as movimiento:
        movimiento.objects.select_related.return_value = queryset
        result = MovimientoService.search(
            movimiento_id=10,
            almacen_id=2,
            tipo_movimiento_id=3,
            estado_movimiento_id=1,
            movimiento_origen_id=8,
            fecha_desde=date(2026, 1, 1),
            fecha_hasta=date(2026, 3, 31),
            documento_referencia='GR-001',
            destinatario='Municipalidad',
            observacion='Entrega parcial',
            encargado_almacen_id=4,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'movimiento_id': 10}),
        ((), {'almacen_id': 2}),
        ((), {'tipo_movimiento_id': 3}),
        ((), {'estado_movimiento_id': 1}),
        ((), {'movimiento_origen_id': 8}),
        ((), {'fecha_movimiento__gte': _inicio_de_dia(date(2026, 1, 1))}),
        (
            (),
            {
                'fecha_movimiento__lt': _inicio_de_dia(
                    date(2026, 3, 31) + timedelta(days=1)
                )
            },
        ),
        (
            (),
            {
                'documento_referencia__ilike_pattern': text_like_pattern('GR-001'),
            },
        ),
        ((), {'destinatario__ilike_pattern': text_like_pattern('Municipalidad')}),
        ((), {'observacion__ilike_pattern': text_like_pattern('Entrega parcial')}),
        ((), {'encargado_almacen_id': 4}),
    ]
    queryset.order_by.assert_called_once_with('-fecha_movimiento')


def test_serializer_returns_joined_columns():
    movimiento = SimpleNamespace(
        movimiento_id=10,
        almacen_id=2,
        tipo_movimiento_id=3,
        estado_movimiento_id=1,
        movimiento_origen_id=8,
        fecha_movimiento=timezone.make_aware(datetime(2026, 3, 1, 8, 30)),
        documento_referencia='GR-001',
        fecha_documento=date(2026, 3, 1),
        destinatario='Municipalidad',
        observacion='Entrega parcial',
        fecha_confirmacion=None,
        encargado_almacen_id=4,
        c_usuari_login='mmedina',
        fecha_creacion=timezone.make_aware(datetime(2026, 3, 1, 8, 0)),
        fecha_modificacion=None,
        almacen=SimpleNamespace(codigo='ALM-01', nombre='Almacén central'),
        tipo_movimiento=SimpleNamespace(
            codigo='SALIDA',
            nombre='Salida',
            naturaleza='S',
            requiere_movimiento_origen=False,
        ),
        estado_movimiento=SimpleNamespace(codigo='BORRADOR', nombre='Borrador'),
        encargado_almacen=SimpleNamespace(
            apellido_paterno='Perez',
            apellido_materno='Lopez',
            nombres='Ana',
        ),
        detalles=[
            SimpleNamespace(
                movimiento_detalle_id=21,
                bien_id=5,
                cantidad=Decimal('-2.500000'),
                cantidad_texto='2 1/2',
                es_devolvible=True,
                observacion='Prestado',
                bien=SimpleNamespace(
                    categoria_bien_id=1,
                    unidad_medida_id=2,
                    codigo='FRAZ-01',
                    nombre='Frazada',
                    unidad_medida=SimpleNamespace(
                        codigo='UND',
                        nombre='Unidad',
                        abreviatura='und',
                    ),
                ),
            ),
            SimpleNamespace(
                movimiento_detalle_id=22,
                bien_id=6,
                cantidad=Decimal('-1.000000'),
                cantidad_texto=None,
                es_devolvible=False,
                observacion=None,
                bien=SimpleNamespace(
                    categoria_bien_id=3,
                    unidad_medida_id=4,
                    codigo='AGUA-01',
                    nombre='Agua',
                    unidad_medida=SimpleNamespace(
                        codigo='LT',
                        nombre='Litro',
                        abreviatura=None,
                    ),
                ),
            ),
        ],
    )

    data = MovimientoBusquedaSerializer(movimiento).data

    assert data['movimiento_id'] == 10
    assert data['movimiento_origen_id'] == 8
    assert data['documento_referencia'] == 'GR-001'
    assert data['fecha_confirmacion'] is None
    assert data['almacen_codigo'] == 'ALM-01'
    assert data['almacen_nombre'] == 'Almacén central'
    assert data['tipo_movimiento_codigo'] == 'SALIDA'
    assert data['tipo_movimiento_nombre'] == 'Salida'
    assert data['tipo_movimiento_naturaleza'] == 'S'
    assert data['tipo_movimiento_origen'] is False
    assert data['estado_movimiento_codigo'] == 'BORRADOR'
    assert data['estado_movimiento_nombre'] == 'Borrador'
    assert data['encargado_almacen_nombre'] == 'Perez Lopez Ana'
    assert data['detalles'] == [
        {
            'movimiento_detalle_id': 21,
            'bien_id': 5,
            'cantidad': '-2.500000',
            'cantidad_texto': '2 1/2',
            'es_devolvible': True,
            'movimiento_detalle_observacion': 'Prestado',
            'categoria_bien_id': 1,
            'unidad_medida_id': 2,
            'bien_codigo': 'FRAZ-01',
            'bien_nombre': 'Frazada',
            'unidad_medida_codigo': 'UND',
            'unidad_medida_nombre': 'Unidad',
            'unidad_medida_abreviatura': 'und',
        },
        {
            'movimiento_detalle_id': 22,
            'bien_id': 6,
            'cantidad': '-1.000000',
            'cantidad_texto': None,
            'es_devolvible': False,
            'movimiento_detalle_observacion': None,
            'categoria_bien_id': 3,
            'unidad_medida_id': 4,
            'bien_codigo': 'AGUA-01',
            'bien_nombre': 'Agua',
            'unidad_medida_codigo': 'LT',
            'unidad_medida_nombre': 'Litro',
            'unidad_medida_abreviatura': None,
        },
    ]


def test_get_movimientos_buscar_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/movimientos/buscar/',
        {
            'movimiento_id': '10',
            'almacen_id': '2',
            'tipo_movimiento_id': '3',
            'estado_movimiento_id': '1',
            'fecha_desde': '2026-01-01',
            'fecha_hasta': '2026-03-31',
            'documento_referencia': 'GR-001',
            'encargado_almacen_id': '4',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'movimiento_id': 10}]

    with (
        patch(
            'app_sgbh.views.movimiento_view.MovimientoService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.movimiento_view.MovimientoBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = MovimientoBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        movimiento_id=10,
        almacen_id=2,
        tipo_movimiento_id=3,
        estado_movimiento_id=1,
        movimiento_origen_id=None,
        documento_referencia='GR-001',
        destinatario=None,
        observacion=None,
        encargado_almacen_id=4,
        fecha_desde=date(2026, 1, 1),
        fecha_hasta=date(2026, 3, 31),
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_movimientos_buscar_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/movimientos/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.movimiento_view.MovimientoService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.movimiento_view.MovimientoBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = MovimientoBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        movimiento_id=None,
        almacen_id=None,
        tipo_movimiento_id=None,
        estado_movimiento_id=None,
        movimiento_origen_id=None,
        documento_referencia=None,
        destinatario=None,
        observacion=None,
        encargado_almacen_id=None,
        fecha_desde=None,
        fecha_hasta=None,
    )


def test_get_movimientos_buscar_rejects_inverted_period():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/movimientos/buscar/',
        {'fecha_desde': '2026-04-01', 'fecha_hasta': '2026-03-01'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = MovimientoBuscarView.as_view()(request)

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro fecha_desde no puede ser posterior a fecha_hasta'
    )


def test_get_movimientos_buscar_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/movimientos/buscar/',
        {'tipo_movimiento_id': 'abc'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = MovimientoBuscarView.as_view()(request)

    assert response.status_code == 400
    assert 'tipo_movimiento_id' in response.data['error']
