from datetime import date, datetime, time, timezone
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.db.models import Subquery
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import parse_vivienda_id
from app_sgbh.serializers.formulario_2a_vivienda import (
    ViviendaBuscarSerializer,
    ViviendaBusquedaSerializer,
)
from app_sgbh.services.formulario_2a_vivienda import Formulario2AViviendaService
from app_sgbh.views.formulario_2a_vivienda_view import Formulario2AViviendaBuscarView


def test_search_returns_every_row_when_no_filter_is_sent():
    with patch(
        'app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'
    ) as model:
        queryset = model.objects.select_related.return_value
        queryset.annotate.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = Formulario2AViviendaService.search()

    assert result == 'rows'
    model.objects.select_related.assert_called_once_with(
        'formulario_2a',
        'formulario_2a__emergencia',
        'formulario_2a__emergencia__tipo_peligro',
        'tipo_uso_instalacion',
        'condicion_vivienda',
        'material_techo',
        'material_pared',
        'material_piso',
    )
    annotation = queryset.annotate.call_args.kwargs['distrito_nombre']
    assert isinstance(annotation, Subquery)
    assert _outer_ref_names(annotation) == {
        'departamento_id': 'formulario_2a__departamento_id',
        'provincia_id': 'formulario_2a__provincia_id',
        'distrito_id': 'formulario_2a__distrito_id',
    }
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('vivienda_id')


def _outer_ref_names(annotation):
    names = {}
    for child in annotation.query.where.children:
        names[child.lhs.target.column] = child.rhs.name
    return names


def test_search_combines_filters_with_and():
    with patch(
        'app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'
    ) as model:
        queryset = model.objects.select_related.return_value
        queryset.annotate.return_value = queryset
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = Formulario2AViviendaService.search(
            vivienda_id=7,
            formulario_2a_id=10,
            codigo_sinpad='261404',
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'vivienda_id': 7}),
        ((), {'formulario_2a_id': 10}),
        ((), {'formulario_2a__emergencia__codigo_sinpad': '261404'}),
    ]
    queryset.order_by.assert_called_once_with('vivienda_id')


def test_serializer_returns_catalog_names():
    vivienda = SimpleNamespace(
        vivienda_id=7,
        formulario_2a_id=10,
        numero_orden=1,
        numero_lote='L-1',
        tenencia_propia=True,
        tipo_uso_instalacion_id=2,
        condicion_vivienda_id=3,
        material_techo_id=4,
        material_pared_id=5,
        material_piso_id=6,
        fecha_creacion=datetime(2026, 3, 1, 8, 0, tzinfo=timezone.utc),
        tipo_uso_instalacion=SimpleNamespace(nombre='Vivienda'),
        condicion_vivienda=SimpleNamespace(nombre='Habitable'),
        material_techo=SimpleNamespace(nombre='Calamina'),
        material_pared=SimpleNamespace(nombre='Adobe'),
        material_piso=SimpleNamespace(nombre='Tierra'),
    )

    data = ViviendaBusquedaSerializer(vivienda).data

    assert data['vivienda_id'] == 7
    assert data['formulario_2a_id'] == 10
    assert data['numero_orden'] == 1
    assert data['numero_lote'] == 'L-1'
    assert data['tenencia_propia'] is True
    assert data['tipo_uso_instalacion_id'] == 2
    assert data['condicion_vivienda_id'] == 3
    assert data['material_techo_id'] == 4
    assert data['material_pared_id'] == 5
    assert data['material_piso_id'] == 6
    assert data['tipo_uso_instalacion_nombre'] == 'Vivienda'
    assert data['condicion_vivienda_nombre'] == 'Habitable'
    assert data['material_techo_nombre'] == 'Calamina'
    assert data['material_pared_nombre'] == 'Adobe'
    assert data['material_piso_nombre'] == 'Tierra'


def test_serializer_returns_null_names_when_catalogs_are_missing():
    vivienda = SimpleNamespace(
        vivienda_id=8,
        formulario_2a_id=10,
        numero_orden=2,
        numero_lote=None,
        tenencia_propia=None,
        tipo_uso_instalacion_id=2,
        condicion_vivienda_id=None,
        material_techo_id=None,
        material_pared_id=None,
        material_piso_id=None,
        fecha_creacion=datetime(2026, 3, 1, 8, 0, tzinfo=timezone.utc),
        tipo_uso_instalacion=SimpleNamespace(nombre='Vivienda'),
        condicion_vivienda=None,
        material_techo=None,
        material_pared=None,
        material_piso=None,
    )

    data = ViviendaBusquedaSerializer(vivienda).data

    assert data['numero_lote'] is None
    assert data['tenencia_propia'] is None
    assert data['condicion_vivienda_nombre'] is None
    assert data['material_techo_nombre'] is None
    assert data['material_pared_nombre'] is None
    assert data['material_piso_nombre'] is None


def test_buscar_serializer_returns_joined_columns():
    row = SimpleNamespace(
        vivienda_id=7,
        formulario_2a_id=10,
        numero_orden=1,
        numero_lote='L-1',
        tenencia_propia=True,
        tipo_uso_instalacion_id=2,
        condicion_vivienda_id=3,
        material_techo_id=4,
        material_pared_id=5,
        material_piso_id=6,
        fecha_creacion=datetime(2026, 3, 1, 8, 0, tzinfo=timezone.utc),
        tipo_uso_instalacion=SimpleNamespace(nombre='Vivienda'),
        condicion_vivienda=SimpleNamespace(nombre='Habitable'),
        material_techo=SimpleNamespace(nombre='Calamina'),
        material_pared=SimpleNamespace(nombre='Adobe'),
        material_piso=SimpleNamespace(nombre='Tierra'),
        formulario_2a=SimpleNamespace(
            emergencia_id=9,
            fecha_empadronamiento=date(2026, 3, 1),
            hora_empadronamiento=time(8, 30),
            localidad='Centro',
            barrio_sector_urbanizacion='Sector 1',
            centro_poblado='Piura',
            caserio=None,
            anexo=None,
            calle_manzana='Calle 1',
            edificio_piso_dpto=None,
            otros_ubicacion=None,
            numero_hoja=1,
            total_hojas=2,
            institucion='Municipalidad',
            evaluador_id=4,
            estado_registro_id=1,
            emergencia=SimpleNamespace(
                codigo_sinpad='261404',
                tipo_peligro_id=3,
                tipo_peligro=SimpleNamespace(nombre='Inundación'),
            ),
        ),
        distrito_nombre='Piura',
    )

    data = ViviendaBuscarSerializer(row).data

    assert data['emergencia_id'] == 9
    assert data['fecha_empadronamiento'] == '2026-03-01'
    assert data['hora_empadronamiento'] == '08:30:00'
    assert data['localidad'] == 'Centro'
    assert data['barrio_sector_urbanizacion'] == 'Sector 1'
    assert data['centro_poblado'] == 'Piura'
    assert data['caserio'] is None
    assert data['calle_manzana'] == 'Calle 1'
    assert data['numero_hoja'] == 1
    assert data['total_hojas'] == 2
    assert data['institucion'] == 'Municipalidad'
    assert data['evaluador_id'] == 4
    assert data['estado_registro_id'] == 1
    assert data['codigo_sinpad'] == '261404'
    assert data['tipo_peligro_id'] == 3
    assert data['nombre_tipo_peligro'] == 'Inundación'
    assert data['distrito_nombre'] == 'Piura'
    assert data['tipo_uso_instalacion_nombre'] == 'Vivienda'


@pytest.mark.parametrize(
    ('value', 'message'),
    [
        ('abc', 'vivienda_id debe ser un número entero'),
        ('2147483648', 'vivienda_id debe ser un número entero'),
    ],
)
def test_parse_vivienda_id_rejects_invalid_values(value, message):
    _parsed, error = parse_vivienda_id(value)

    assert error is not None
    assert message in error


def test_get_viviendas_buscar_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/viviendas/buscar/',
        {
            'vivienda_id': '7',
            'formulario_2a_id': '10',
            'codigo_sinpad': ' 261404 ',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'vivienda_id': 7, 'formulario_2a_id': 10}]

    with (
        patch(
            'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.formulario_2a_vivienda_view.ViviendaBuscarSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = Formulario2AViviendaBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        vivienda_id=7,
        formulario_2a_id=10,
        codigo_sinpad='261404',
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_viviendas_buscar_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/viviendas/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.formulario_2a_vivienda_view.ViviendaBuscarSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = Formulario2AViviendaBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        vivienda_id=None,
        formulario_2a_id=None,
        codigo_sinpad=None,
    )


def test_get_viviendas_buscar_rejects_codigo_sinpad_too_long():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/viviendas/buscar/',
        {'codigo_sinpad': 'a' * 31},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AViviendaBuscarView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == (
        'El filtro codigo_sinpad no debe superar 30 caracteres'
    )


def test_get_viviendas_buscar_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/viviendas/buscar/',
        {'vivienda_id': 'x'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AViviendaBuscarView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El filtro vivienda_id debe ser un número entero'
