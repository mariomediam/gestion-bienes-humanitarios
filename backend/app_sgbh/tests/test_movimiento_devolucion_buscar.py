from datetime import date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from django.db.models import Case, Q
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers.movimiento_devolucion import (
    MovimientoDevolucionBusquedaSerializer,
)
from app_sgbh.services.movimiento_devolucion import (
    MovimientoDevolucionService,
    _NumeroAnioPlanilla,
    _inicio_de_dia,
)
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.movimiento_devolucion_view import (
    MovimientoDevolucionBuscarView,
    _parse_busqueda,
)


def test_parse_busqueda_omits_every_filter_when_params_are_empty():
    parsed, error = _parse_busqueda({})

    assert error is None
    assert parsed == {
        'movimiento_id': None,
        'almacen_id': None,
        'estado_movimiento_id': None,
        'movimiento_origen_id': None,
        'documento_referencia': None,
        'documento_origen_referencia': None,
        'fecha_movimiento': None,
        'fecha_documento_desde': None,
        'fecha_documento_hasta': None,
    }


def test_parse_busqueda_accepts_several_filters_together():
    parsed, error = _parse_busqueda(
        {
            'movimiento_id': '10',
            'almacen_id': '2',
            'estado_movimiento_id': '1',
            'movimiento_origen_id': '8',
            'fecha_movimiento': '2026-03-02',
            'documento_referencia': ' GR-010 ',
            'fecha_documento_desde': '2026-01-01',
            'fecha_documento_hasta': '2026-03-31',
            'documento_origen_referencia': ' 4-2026 ',
        }
    )

    assert error is None
    assert parsed == {
        'movimiento_id': 10,
        'almacen_id': 2,
        'estado_movimiento_id': 1,
        'movimiento_origen_id': 8,
        'documento_referencia': 'GR-010',
        'documento_origen_referencia': '4-2026',
        'fecha_movimiento': date(2026, 3, 2),
        'fecha_documento_desde': date(2026, 1, 1),
        'fecha_documento_hasta': date(2026, 3, 31),
    }


@pytest.mark.parametrize(
    ('params', 'message'),
    [
        ({'movimiento_id': 'abc'}, 'movimiento_id debe ser un número entero'),
        ({'almacen_id': 'abc'}, 'almacen_id debe ser un número entero'),
        (
            {'estado_movimiento_id': 'x'},
            'estado_movimiento_id debe ser un número entero',
        ),
        (
            {'movimiento_origen_id': 'abc'},
            'movimiento_origen_id debe ser un número entero',
        ),
        (
            {'fecha_movimiento': '02/03/2026'},
            'fecha_movimiento debe tener el formato AAAA-MM-DD',
        ),
        (
            {'fecha_documento_desde': '01-03-2026'},
            'fecha_documento_desde debe tener el formato AAAA-MM-DD',
        ),
        (
            {'fecha_documento_hasta': '31/03/2026'},
            'fecha_documento_hasta debe tener el formato AAAA-MM-DD',
        ),
        (
            {'documento_referencia': 'a' * 101},
            'documento_referencia no debe superar 100 caracteres',
        ),
        (
            {'documento_origen_referencia': 'a' * 101},
            'documento_origen_referencia no debe superar 100 caracteres',
        ),
    ],
)
def test_parse_busqueda_rejects_invalid_filters(params, message):
    _parsed, error = _parse_busqueda(params)

    assert error is not None
    assert message in error


def _queryset():
    queryset = MagicMock()
    queryset.select_related.return_value = queryset
    queryset.annotate.return_value = queryset
    queryset.filter.return_value = queryset
    queryset.order_by.return_value = 'rows'
    return queryset


def test_search_returns_devoluciones_when_no_filter_is_sent():
    queryset = _queryset()

    with patch('app_sgbh.services.movimiento_devolucion.Movimiento') as movimiento:
        movimiento.objects.filter.return_value = queryset
        result = MovimientoDevolucionService.search()

    assert result == 'rows'
    movimiento.objects.filter.assert_called_once_with(
        tipo_movimiento__codigo='DEVOLUCION'
    )
    queryset.filter.assert_not_called()
    queryset.select_related.assert_called_once_with(
        'almacen',
        'tipo_movimiento',
        'estado_movimiento',
    )
    queryset.order_by.assert_called_once_with(
        '-fecha_movimiento',
        'detalles__movimiento_detalle_id',
    )


def test_search_annotates_origin_document_and_detail_columns():
    queryset = _queryset()

    with patch('app_sgbh.services.movimiento_devolucion.Movimiento') as movimiento:
        movimiento.objects.filter.return_value = queryset
        MovimientoDevolucionService.search()

    annotations = queryset.annotate.call_args.kwargs
    assert annotations['tipo_movimiento_origen_nombre'].name == (
        'movimiento_origen__tipo_movimiento__nombre'
    )
    documento = annotations['documento_origen_referencia']
    assert isinstance(documento, Case)
    assert documento.cases[0].condition == Q(
        movimiento_origen__tipo_movimiento__codigo='ENTREGA_BAH'
    )
    numero_anio = documento.cases[0].result
    assert isinstance(numero_anio, _NumeroAnioPlanilla)
    assert numero_anio.template == 'CONVERT(varchar(5), %(expressions)s)'
    assert numero_anio.arg_joiner == ") + '-' + CONVERT(varchar(5), "
    assert [expr.name for expr in numero_anio.source_expressions] == [
        'movimiento_origen__planillas_entrega__numero_planilla',
        'movimiento_origen__planillas_entrega__anio_planilla',
    ]
    assert documento.default.name == 'movimiento_origen__documento_referencia'
    assert annotations['movimiento_detalle_id'].name == (
        'detalles__movimiento_detalle_id'
    )
    assert annotations['bien_id'].name == 'detalles__bien_id'
    assert annotations['cantidad'].name == 'detalles__cantidad'
    assert annotations['cantidad_texto'].name == 'detalles__cantidad_texto'
    assert annotations['es_devolvible'].name == 'detalles__es_devolvible'
    assert annotations['movimiento_detalle_observacion'].name == 'detalles__observacion'
    assert annotations['categoria_bien_id'].name == (
        'detalles__bien__categoria_bien_id'
    )
    assert annotations['unidad_medida_id'].name == 'detalles__bien__unidad_medida_id'
    assert annotations['bien_codigo'].name == 'detalles__bien__codigo'
    assert annotations['bien_nombre'].name == 'detalles__bien__nombre'
    assert annotations['unidad_medida_codigo'].name == (
        'detalles__bien__unidad_medida__codigo'
    )
    assert annotations['unidad_medida_nombre'].name == (
        'detalles__bien__unidad_medida__nombre'
    )
    assert annotations['unidad_medida_abreviatura'].name == (
        'detalles__bien__unidad_medida__abreviatura'
    )


def test_search_combines_filters_with_and():
    queryset = _queryset()
    fecha = date(2026, 3, 2)

    with patch('app_sgbh.services.movimiento_devolucion.Movimiento') as movimiento:
        movimiento.objects.filter.return_value = queryset
        result = MovimientoDevolucionService.search(
            movimiento_id=10,
            almacen_id=2,
            estado_movimiento_id=1,
            movimiento_origen_id=8,
            fecha_movimiento=fecha,
            documento_referencia='GR-010',
            fecha_documento_desde=date(2026, 1, 1),
            fecha_documento_hasta=date(2026, 3, 31),
            documento_origen_referencia='4-2026',
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'movimiento_id': 10}),
        ((), {'almacen_id': 2}),
        ((), {'estado_movimiento_id': 1}),
        ((), {'movimiento_origen_id': 8}),
        (
            (),
            {
                'fecha_movimiento__gte': _inicio_de_dia(fecha),
                'fecha_movimiento__lt': _inicio_de_dia(fecha + timedelta(days=1)),
            },
        ),
        (
            (),
            {
                'documento_referencia__ilike_pattern': text_like_pattern('GR-010'),
            },
        ),
        ((), {'fecha_documento__gte': date(2026, 1, 1)}),
        ((), {'fecha_documento__lte': date(2026, 3, 31)}),
        (
            (),
            {
                'documento_origen_referencia__ilike_pattern': text_like_pattern(
                    '4-2026'
                ),
            },
        ),
    ]


def _devolucion():
    return SimpleNamespace(
        movimiento_id=10,
        almacen_id=2,
        tipo_movimiento_id=7,
        estado_movimiento_id=1,
        movimiento_origen_id=8,
        fecha_movimiento=timezone.make_aware(datetime(2026, 3, 2, 8, 30)),
        documento_referencia='DEV-010',
        fecha_documento=date(2026, 3, 1),
        destinatario='Almacén central',
        observacion='Devolución parcial',
        fecha_confirmacion=None,
        encargado_almacen_id=4,
        c_usuari_login='mmedina',
        fecha_creacion=timezone.make_aware(datetime(2026, 3, 2, 8, 0)),
        fecha_modificacion=None,
        almacen=SimpleNamespace(codigo='ALM-01', nombre='Almacén central'),
        tipo_movimiento=SimpleNamespace(
            codigo='DEVOLUCION',
            nombre='Devolución',
            naturaleza='E',
            requiere_movimiento_origen=True,
        ),
        estado_movimiento=SimpleNamespace(codigo='BORRADOR', nombre='Borrador'),
        tipo_movimiento_origen_nombre='Entrega BAH',
        documento_origen_referencia='4-2026',
        movimiento_detalle_id=21,
        bien_id=5,
        cantidad=Decimal('2.500000'),
        cantidad_texto='2 1/2',
        es_devolvible=False,
        movimiento_detalle_observacion='Devuelto',
        categoria_bien_id=1,
        unidad_medida_id=2,
        bien_codigo='FRAZ-01',
        bien_nombre='Frazada',
        unidad_medida_codigo='UND',
        unidad_medida_nombre='Unidad',
        unidad_medida_abreviatura='und',
    )


def test_serializer_returns_joined_columns():
    data = MovimientoDevolucionBusquedaSerializer(_devolucion()).data

    assert data['movimiento_id'] == 10
    assert data['almacen_id'] == 2
    assert data['tipo_movimiento_id'] == 7
    assert data['estado_movimiento_id'] == 1
    assert data['movimiento_origen_id'] == 8
    assert data['fecha_movimiento'] == '2026-03-02T08:30:00-05:00'
    assert data['documento_referencia'] == 'DEV-010'
    assert data['fecha_documento'] == '2026-03-01'
    assert data['destinatario'] == 'Almacén central'
    assert data['observacion'] == 'Devolución parcial'
    assert data['fecha_confirmacion'] is None
    assert data['encargado_almacen_id'] == 4
    assert data['c_usuari_login'] == 'mmedina'
    assert data['fecha_creacion'] == '2026-03-02T08:00:00-05:00'
    assert data['fecha_modificacion'] is None
    assert data['almacen_codigo'] == 'ALM-01'
    assert data['almacen_nombre'] == 'Almacén central'
    assert data['tipo_movimiento_codigo'] == 'DEVOLUCION'
    assert data['tipo_movimiento_nombre'] == 'Devolución'
    assert data['tipo_movimiento_naturaleza'] == 'E'
    assert data['tipo_movimiento_requiere_origen'] is True
    assert data['estado_movimiento_codigo'] == 'BORRADOR'
    assert data['estado_movimiento_nombre'] == 'Borrador'
    assert data['tipo_movimiento_origen_nombre'] == 'Entrega BAH'
    assert data['documento_origen_referencia'] == '4-2026'
    assert data['movimiento_detalle_id'] == 21
    assert data['bien_id'] == 5
    assert data['cantidad'] == '2.500000'
    assert data['cantidad_texto'] == '2 1/2'
    assert data['es_devolvible'] is False
    assert data['movimiento_detalle_observacion'] == 'Devuelto'
    assert data['categoria_bien_id'] == 1
    assert data['unidad_medida_id'] == 2
    assert data['bien_codigo'] == 'FRAZ-01'
    assert data['bien_nombre'] == 'Frazada'
    assert data['unidad_medida_codigo'] == 'UND'
    assert data['unidad_medida_nombre'] == 'Unidad'
    assert data['unidad_medida_abreviatura'] == 'und'


def test_serializer_returns_null_for_optional_joined_columns():
    row = _devolucion()
    row.movimiento_origen_id = None
    row.documento_referencia = None
    row.fecha_documento = None
    row.destinatario = None
    row.observacion = None
    row.tipo_movimiento_origen_nombre = None
    row.documento_origen_referencia = None
    row.movimiento_detalle_id = None
    row.bien_id = None
    row.cantidad = None
    row.cantidad_texto = None
    row.es_devolvible = None
    row.movimiento_detalle_observacion = None
    row.categoria_bien_id = None
    row.unidad_medida_id = None
    row.bien_codigo = None
    row.bien_nombre = None
    row.unidad_medida_codigo = None
    row.unidad_medida_nombre = None
    row.unidad_medida_abreviatura = None

    data = MovimientoDevolucionBusquedaSerializer(row).data

    assert data['movimiento_origen_id'] is None
    assert data['documento_referencia'] is None
    assert data['fecha_documento'] is None
    assert data['tipo_movimiento_origen_nombre'] is None
    assert data['documento_origen_referencia'] is None
    assert data['movimiento_detalle_id'] is None
    assert data['bien_id'] is None
    assert data['cantidad'] is None
    assert data['cantidad_texto'] is None
    assert data['es_devolvible'] is None
    assert data['movimiento_detalle_observacion'] is None
    assert data['categoria_bien_id'] is None
    assert data['bien_codigo'] is None
    assert data['unidad_medida_abreviatura'] is None


def test_get_movimientos_buscar_devoluciones_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/movimientos/buscar-devoluciones/',
        {
            'movimiento_id': '10',
            'almacen_id': '2',
            'estado_movimiento_id': '1',
            'movimiento_origen_id': '8',
            'fecha_movimiento': '2026-03-02',
            'documento_referencia': 'DEV-010',
            'fecha_documento_desde': '2026-01-01',
            'fecha_documento_hasta': '2026-03-31',
            'documento_origen_referencia': '4-2026',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'movimiento_id': 10, 'documento_origen_referencia': '4-2026'}]

    with (
        patch(
            'app_sgbh.views.movimiento_devolucion_view.MovimientoDevolucionService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.movimiento_devolucion_view.MovimientoDevolucionBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = MovimientoDevolucionBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        movimiento_id=10,
        almacen_id=2,
        estado_movimiento_id=1,
        movimiento_origen_id=8,
        documento_referencia='DEV-010',
        documento_origen_referencia='4-2026',
        fecha_movimiento=date(2026, 3, 2),
        fecha_documento_desde=date(2026, 1, 1),
        fecha_documento_hasta=date(2026, 3, 31),
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_movimientos_buscar_devoluciones_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/movimientos/buscar-devoluciones/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.movimiento_devolucion_view.MovimientoDevolucionService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.movimiento_devolucion_view.MovimientoDevolucionBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = MovimientoDevolucionBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        movimiento_id=None,
        almacen_id=None,
        estado_movimiento_id=None,
        movimiento_origen_id=None,
        documento_referencia=None,
        documento_origen_referencia=None,
        fecha_movimiento=None,
        fecha_documento_desde=None,
        fecha_documento_hasta=None,
    )


def test_get_movimientos_buscar_devoluciones_rejects_inverted_period():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/movimientos/buscar-devoluciones/',
        {
            'fecha_documento_desde': '2026-04-01',
            'fecha_documento_hasta': '2026-03-01',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = MovimientoDevolucionBuscarView.as_view()(request)

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro fecha_documento_desde no puede ser posterior '
        'a fecha_documento_hasta'
    )


def test_get_movimientos_buscar_devoluciones_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/movimientos/buscar-devoluciones/',
        {'movimiento_id': 'abc'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = MovimientoDevolucionBuscarView.as_view()(request)

    assert response.status_code == 400
    assert 'movimiento_id' in response.data['error']


def test_get_movimientos_buscar_devoluciones_returns_500_when_search_fails():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/movimientos/buscar-devoluciones/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.movimiento_devolucion_view.MovimientoDevolucionService.search',
        side_effect=RuntimeError('fallo'),
    ):
        response = MovimientoDevolucionBuscarView.as_view()(request)

    assert response.status_code == 500
    assert response.data['error'] == 'No se pudo obtener la búsqueda de devoluciones'
