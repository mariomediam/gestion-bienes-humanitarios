from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from django.db.models import Prefetch
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers.movimiento_planilla_bah import (
    MovimientoPlanillaBahBusquedaSerializer,
)
from app_sgbh.services.movimiento_planilla_bah import MovimientoPlanillaBahService
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.movimiento_planilla_bah_view import (
    MovimientoPlanillaBahBuscarView,
    _parse_busqueda,
)


def test_parse_busqueda_omits_every_filter_when_params_are_empty():
    parsed, error = _parse_busqueda({})

    assert error is None
    assert parsed == {
        'planilla_entrega_id': None,
        'movimiento_id': None,
        'numero_planilla': None,
        'anio_planilla': None,
        'codigo_sinpad': None,
        'barrio_sector_urbanizacion': None,
        'documento_referencia': None,
        'integrante_receptor_nombre': None,
        'fecha_desde': None,
        'fecha_hasta': None,
    }


def test_parse_busqueda_accepts_several_filters_together():
    parsed, error = _parse_busqueda(
        {
            'planilla_entrega_id': '15',
            'movimiento_id': '10',
            'numero_planilla': '4',
            'anio_planilla': '2026',
            'codigo_sinpad': ' 261404 ',
            'barrio_sector_urbanizacion': ' Santa Rosa ',
            'fecha_desde': '2026-01-01',
            'fecha_hasta': '2026-03-31',
            'documento_referencia': ' GR-001 ',
            'integrante_receptor_nombre': ' Perez Lopez Ana ',
        }
    )

    assert error is None
    assert parsed == {
        'planilla_entrega_id': 15,
        'movimiento_id': 10,
        'numero_planilla': 4,
        'anio_planilla': 2026,
        'codigo_sinpad': '261404',
        'barrio_sector_urbanizacion': 'Santa Rosa',
        'documento_referencia': 'GR-001',
        'integrante_receptor_nombre': 'Perez Lopez Ana',
        'fecha_desde': date(2026, 1, 1),
        'fecha_hasta': date(2026, 3, 31),
    }


@pytest.mark.parametrize(
    ('params', 'message'),
    [
        (
            {'planilla_entrega_id': 'abc'},
            'planilla_entrega_id debe ser un número entero',
        ),
        ({'movimiento_id': 'abc'}, 'movimiento_id debe ser un número entero'),
        ({'numero_planilla': 'abc'}, 'numero_planilla debe ser un número entero'),
        ({'anio_planilla': 'abc'}, 'anio_planilla debe ser un número entero'),
        (
            {'codigo_sinpad': 'a' * 31},
            'codigo_sinpad no debe superar 30 caracteres',
        ),
        (
            {'barrio_sector_urbanizacion': 'a' * 251},
            'barrio_sector_urbanizacion no debe superar 250 caracteres',
        ),
        ({'fecha_desde': '01-03-2026'}, 'fecha_desde debe tener el formato AAAA-MM-DD'),
        ({'fecha_hasta': '31/03/2026'}, 'fecha_hasta debe tener el formato AAAA-MM-DD'),
        (
            {'documento_referencia': 'a' * 101},
            'documento_referencia no debe superar 100 caracteres',
        ),
        (
            {'integrante_receptor_nombre': 'a' * 253},
            'integrante_receptor_nombre no debe superar 252 caracteres',
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
    queryset.prefetch_related.return_value = queryset
    queryset.filter.return_value = queryset
    queryset.alias.return_value = queryset
    queryset.order_by.return_value = 'rows'
    return queryset


def test_search_returns_linked_rows_when_no_filter_is_sent():
    queryset = _queryset()
    distrito_qs = MagicMock()
    distrito_qs.values.return_value = distrito_qs
    detalle_qs = MagicMock()
    detalle_qs.order_by.return_value = 'detalles'

    with (
        patch(
            'app_sgbh.services.movimiento_planilla_bah.PlanillaEntrega'
        ) as planilla,
        patch('app_sgbh.services.movimiento_planilla_bah.Distrito') as distrito,
        patch(
            'app_sgbh.services.movimiento_planilla_bah.MovimientoDetalle'
        ) as detalle,
    ):
        planilla.objects.filter.return_value = queryset
        distrito.objects.filter.return_value = distrito_qs
        detalle.objects.select_related.return_value = detalle_qs
        result = MovimientoPlanillaBahService.search()

    assert result == 'rows'
    planilla.objects.filter.assert_called_once_with(movimiento_almacen__isnull=False)
    queryset.filter.assert_not_called()
    queryset.alias.assert_not_called()
    queryset.order_by.assert_called_once_with('-movimiento_almacen__fecha_movimiento')


def test_search_joins_movement_planilla_and_detail_lines():
    queryset = _queryset()
    distrito_qs = MagicMock()
    distrito_qs.values.return_value = distrito_qs
    detalle_qs = MagicMock()
    detalle_qs.order_by.return_value = 'detalles'

    with (
        patch(
            'app_sgbh.services.movimiento_planilla_bah.PlanillaEntrega'
        ) as planilla,
        patch('app_sgbh.services.movimiento_planilla_bah.Distrito') as distrito,
        patch(
            'app_sgbh.services.movimiento_planilla_bah.MovimientoDetalle'
        ) as detalle,
    ):
        planilla.objects.filter.return_value = queryset
        distrito.objects.filter.return_value = distrito_qs
        detalle.objects.select_related.return_value = detalle_qs
        MovimientoPlanillaBahService.search()

    queryset.select_related.assert_called_once_with(
        'movimiento_almacen',
        'movimiento_almacen__almacen',
        'movimiento_almacen__tipo_movimiento',
        'movimiento_almacen__estado_movimiento',
        'movimiento_almacen__encargado_almacen',
        'integrante_receptor',
        'integrante_receptor__persona',
        'integrante_receptor__familia',
        'integrante_receptor__familia__vivienda',
        'integrante_receptor__familia__vivienda__formulario_2a',
        'integrante_receptor__familia__vivienda__formulario_2a__emergencia',
    )
    distrito_filter = distrito.objects.filter.call_args.kwargs
    assert distrito_filter['departamento_id'].name == (
        'integrante_receptor__familia__vivienda__formulario_2a__departamento_id'
    )
    assert distrito_filter['provincia_id'].name == (
        'integrante_receptor__familia__vivienda__formulario_2a__provincia_id'
    )
    assert distrito_filter['distrito_id'].name == (
        'integrante_receptor__familia__vivienda__formulario_2a__distrito_id'
    )
    detalle.objects.select_related.assert_called_once_with(
        'bien',
        'bien__unidad_medida',
    )
    detalle_qs.order_by.assert_called_once_with('movimiento_detalle_id')
    prefetch = queryset.prefetch_related.call_args.args[0]
    assert isinstance(prefetch, Prefetch)
    assert prefetch.prefetch_through == 'movimiento_almacen__detalles'
    assert prefetch.queryset == 'detalles'


def test_search_combines_filters_with_and():
    queryset = _queryset()
    distrito_qs = MagicMock()
    distrito_qs.values.return_value = distrito_qs
    detalle_qs = MagicMock()
    detalle_qs.order_by.return_value = 'detalles'

    with (
        patch(
            'app_sgbh.services.movimiento_planilla_bah.PlanillaEntrega'
        ) as planilla,
        patch('app_sgbh.services.movimiento_planilla_bah.Distrito') as distrito,
        patch(
            'app_sgbh.services.movimiento_planilla_bah.MovimientoDetalle'
        ) as detalle,
    ):
        planilla.objects.filter.return_value = queryset
        distrito.objects.filter.return_value = distrito_qs
        detalle.objects.select_related.return_value = detalle_qs
        result = MovimientoPlanillaBahService.search(
            planilla_entrega_id=15,
            movimiento_id=10,
            numero_planilla=4,
            anio_planilla=2026,
            codigo_sinpad='261404',
            barrio_sector_urbanizacion='Santa Rosa',
            fecha_desde=date(2026, 1, 1),
            fecha_hasta=date(2026, 3, 31),
            documento_referencia='GR-001',
            integrante_receptor_nombre='Perez Lopez Ana',
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'planilla_entrega_id': 15}),
        ((), {'movimiento_almacen_id': 10}),
        ((), {'numero_planilla': 4}),
        ((), {'anio_planilla': 2026}),
        (
            (),
            {
                'integrante_receptor__familia__vivienda__formulario_2a__emergencia__codigo_sinpad': (
                    '261404'
                ),
            },
        ),
        (
            (),
            {
                'integrante_receptor__familia__vivienda__formulario_2a__barrio_sector_urbanizacion__ilike_pattern': (
                    text_like_pattern('Santa Rosa')
                ),
            },
        ),
        ((), {'fecha_entrega__gte': date(2026, 1, 1)}),
        ((), {'fecha_entrega__lte': date(2026, 3, 31)}),
        (
            (),
            {
                'movimiento_almacen__documento_referencia__ilike_pattern': (
                    text_like_pattern('GR-001')
                ),
            },
        ),
        (
            (),
            {
                'integrante_receptor_nombre__ilike_pattern': text_like_pattern(
                    'Perez Lopez Ana'
                ),
            },
        ),
    ]
    queryset.alias.assert_called_once()
    queryset.order_by.assert_called_once_with('-movimiento_almacen__fecha_movimiento')


def _planilla():
    return SimpleNamespace(
        planilla_entrega_id=15,
        numero_planilla=4,
        anio_planilla=2026,
        integrante_receptor_id=9,
        fecha_entrega=date(2026, 3, 2),
        estado_planilla_id=1,
        observacion='Entrega en vivienda',
        fecha_emision=timezone.make_aware(datetime(2026, 3, 2, 9, 0)),
        fecha_anulacion=None,
        motivo_anulacion=None,
        movimiento_almacen_id=10,
        distrito_nombre='Piura',
        integrante_receptor=SimpleNamespace(
            persona=SimpleNamespace(
                apellido_paterno='Perez',
                apellido_materno='Lopez',
                nombres='Ana',
            ),
            familia=SimpleNamespace(
                vivienda=SimpleNamespace(
                    numero_lote='L-12',
                    formulario_2a=SimpleNamespace(
                        barrio_sector_urbanizacion='Santa Rosa',
                        emergencia=SimpleNamespace(codigo_sinpad='261404'),
                    ),
                ),
            ),
        ),
        movimiento_almacen=SimpleNamespace(
            movimiento_id=10,
            almacen_id=2,
            tipo_movimiento_id=3,
            estado_movimiento_id=1,
            movimiento_origen_id=None,
            fecha_movimiento=timezone.make_aware(datetime(2026, 3, 2, 8, 30)),
            documento_referencia='GR-001',
            fecha_documento=date(2026, 3, 1),
            destinatario='Familia Perez',
            observacion='Salida por planilla',
            fecha_confirmacion=None,
            encargado_almacen_id=4,
            c_usuari_login='mmedina',
            fecha_creacion=timezone.make_aware(datetime(2026, 3, 2, 8, 0)),
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
                apellido_paterno='Rojas',
                apellido_materno='Diaz',
                nombres='Luis',
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
            ],
        ),
    )


def test_serializer_returns_joined_columns():
    data = MovimientoPlanillaBahBusquedaSerializer(_planilla()).data

    assert data['movimiento_id'] == 10
    assert data['almacen_id'] == 2
    assert data['tipo_movimiento_id'] == 3
    assert data['estado_movimiento_id'] == 1
    assert data['movimiento_origen_id'] is None
    assert data['documento_referencia'] == 'GR-001'
    assert data['fecha_documento'] == '2026-03-01'
    assert data['destinatario'] == 'Familia Perez'
    assert data['observacion'] == 'Salida por planilla'
    assert data['fecha_confirmacion'] is None
    assert data['encargado_almacen_id'] == 4
    assert data['c_usuari_login'] == 'mmedina'
    assert data['fecha_modificacion'] is None
    assert data['almacen_codigo'] == 'ALM-01'
    assert data['almacen_nombre'] == 'Almacén central'
    assert data['tipo_movimiento_codigo'] == 'SALIDA'
    assert data['tipo_movimiento_nombre'] == 'Salida'
    assert data['tipo_movimiento_naturaleza'] == 'S'
    assert data['tipo_movimiento_origen'] is False
    assert data['estado_movimiento_codigo'] == 'BORRADOR'
    assert data['estado_movimiento_nombre'] == 'Borrador'
    assert data['encargado_almacen_nombre'] == 'Rojas Diaz Luis'
    assert data['planilla_entrega_id'] == 15
    assert data['numero_planilla'] == 4
    assert data['anio_planilla'] == 2026
    assert data['integrante_receptor_id'] == 9
    assert data['planilla_fecha_entrega'] == '2026-03-02'
    assert data['estado_planilla_id'] == 1
    assert data['planilla_entrega_observacion'] == 'Entrega en vivienda'
    assert data['planilla_entrega_fecha_anulacion'] is None
    assert data['planilla_entrega_motivo_anulacion'] is None
    assert data['movimiento_almacen_id'] == 10
    assert data['codigo_sinpad'] == '261404'
    assert data['distrito_nombre'] == 'Piura'
    assert data['barrio_sector_urbanizacion'] == 'Santa Rosa'
    assert data['numero_lote'] == 'L-12'
    assert data['integrante_receptor_nombre'] == 'Perez Lopez Ana'
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
    ]


def test_serializer_returns_null_for_optional_joined_columns():
    planilla = _planilla()
    planilla.observacion = None
    planilla.fecha_emision = None
    planilla.distrito_nombre = None
    planilla.integrante_receptor.familia.vivienda.numero_lote = None
    planilla.integrante_receptor.familia.vivienda.formulario_2a.barrio_sector_urbanizacion = (
        None
    )
    planilla.integrante_receptor.familia.vivienda.formulario_2a.emergencia.codigo_sinpad = (
        None
    )
    planilla.movimiento_almacen.detalles = []

    data = MovimientoPlanillaBahBusquedaSerializer(planilla).data

    assert data['planilla_entrega_observacion'] is None
    assert data['planilla_entrega_fecha_emision'] is None
    assert data['codigo_sinpad'] is None
    assert data['distrito_nombre'] is None
    assert data['barrio_sector_urbanizacion'] is None
    assert data['numero_lote'] is None
    assert data['detalles'] == []


def test_get_movimientos_buscar_planilla_bah_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/movimientos/buscar-planilla-bah/',
        {
            'planilla_entrega_id': '15',
            'movimiento_id': '10',
            'numero_planilla': '4',
            'anio_planilla': '2026',
            'codigo_sinpad': '261404',
            'barrio_sector_urbanizacion': 'Santa Rosa',
            'fecha_desde': '2026-01-01',
            'fecha_hasta': '2026-03-31',
            'documento_referencia': 'GR-001',
            'integrante_receptor_nombre': 'Perez Lopez Ana',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'planilla_entrega_id': 15, 'movimiento_id': 10}]

    with (
        patch(
            'app_sgbh.views.movimiento_planilla_bah_view.MovimientoPlanillaBahService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.movimiento_planilla_bah_view.MovimientoPlanillaBahBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = MovimientoPlanillaBahBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        planilla_entrega_id=15,
        movimiento_id=10,
        numero_planilla=4,
        anio_planilla=2026,
        codigo_sinpad='261404',
        barrio_sector_urbanizacion='Santa Rosa',
        documento_referencia='GR-001',
        integrante_receptor_nombre='Perez Lopez Ana',
        fecha_desde=date(2026, 1, 1),
        fecha_hasta=date(2026, 3, 31),
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_movimientos_buscar_planilla_bah_returns_every_linked_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/movimientos/buscar-planilla-bah/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.movimiento_planilla_bah_view.MovimientoPlanillaBahService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.movimiento_planilla_bah_view.MovimientoPlanillaBahBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = MovimientoPlanillaBahBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        planilla_entrega_id=None,
        movimiento_id=None,
        numero_planilla=None,
        anio_planilla=None,
        codigo_sinpad=None,
        barrio_sector_urbanizacion=None,
        documento_referencia=None,
        integrante_receptor_nombre=None,
        fecha_desde=None,
        fecha_hasta=None,
    )


def test_get_movimientos_buscar_planilla_bah_rejects_inverted_period():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/movimientos/buscar-planilla-bah/',
        {'fecha_desde': '2026-04-01', 'fecha_hasta': '2026-03-01'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = MovimientoPlanillaBahBuscarView.as_view()(request)

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro fecha_desde no puede ser posterior a fecha_hasta'
    )


def test_get_movimientos_buscar_planilla_bah_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/movimientos/buscar-planilla-bah/',
        {'numero_planilla': 'abc'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = MovimientoPlanillaBahBuscarView.as_view()(request)

    assert response.status_code == 400
    assert 'numero_planilla' in response.data['error']
