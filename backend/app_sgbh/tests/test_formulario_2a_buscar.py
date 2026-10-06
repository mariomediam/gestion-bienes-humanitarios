from datetime import date, datetime, time
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers.formulario_2a import Formulario2ABusquedaSerializer
from app_sgbh.services.formulario_2a import Formulario2AService
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.formulario_2a_view import Formulario2ABuscarView, _parse_busqueda


def test_parse_busqueda_omits_every_filter_when_params_are_empty():
    parsed, error = _parse_busqueda({})

    assert error is None
    assert parsed == {
        'formulario_2a_id': None,
        'codigo_sinpad': None,
        'tipo_peligro_id': None,
        'departamento_id': None,
        'provincia_id': None,
        'distrito_id': None,
        'barrio_sector_urbanizacion': None,
        'localidad': None,
        'estado_registro_id': None,
        'fecha_desde': None,
        'fecha_hasta': None,
    }


def test_parse_busqueda_accepts_several_filters_together():
    parsed, error = _parse_busqueda(
        {
            'formulario_2a_id': '10',
            'codigo_sinpad': ' 45821 ',
            'tipo_peligro_id': '3',
            'departamento_id': '20',
            'provincia_id': '01',
            'distrito_id': '01',
            'fecha_desde': '2026-01-01',
            'fecha_hasta': '2026-03-31',
            'barrio_sector_urbanizacion': ' Santa Rosa ',
            'localidad': 'Centro',
            'estado_registro_id': '1',
        }
    )

    assert error is None
    assert parsed == {
        'formulario_2a_id': 10,
        'codigo_sinpad': '45821',
        'tipo_peligro_id': 3,
        'departamento_id': '20',
        'provincia_id': '01',
        'distrito_id': '01',
        'barrio_sector_urbanizacion': 'Santa Rosa',
        'localidad': 'Centro',
        'estado_registro_id': 1,
        'fecha_desde': date(2026, 1, 1),
        'fecha_hasta': date(2026, 3, 31),
    }


@pytest.mark.parametrize(
    ('params', 'message'),
    [
        ({'formulario_2a_id': 'abc'}, 'formulario_2a_id debe ser un número entero'),
        ({'tipo_peligro_id': 'abc'}, 'tipo_peligro_id debe ser un número entero'),
        ({'estado_registro_id': 'x'}, 'estado_registro_id debe ser un número entero'),
        ({'departamento_id': '200'}, 'departamento_id no debe superar 2 caracteres'),
        ({'provincia_id': '001'}, 'provincia_id no debe superar 2 caracteres'),
        ({'distrito_id': '001'}, 'distrito_id no debe superar 2 caracteres'),
        ({'fecha_desde': '01-03-2026'}, 'fecha_desde debe tener el formato AAAA-MM-DD'),
        ({'fecha_hasta': '31/03/2026'}, 'fecha_hasta debe tener el formato AAAA-MM-DD'),
        (
            {'localidad': 'a' * 201},
            'localidad no debe superar 200 caracteres',
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

    with patch(
        'app_sgbh.services.formulario_2a._formularios_busqueda',
        return_value=queryset,
    ):
        result = Formulario2AService.search()

    assert result == 'rows'
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with(
        '-fecha_empadronamiento',
        '-hora_empadronamiento',
    )


def test_search_combines_filters_with_and():
    queryset = MagicMock()
    queryset.filter.return_value = queryset
    queryset.order_by.return_value = 'rows'

    with patch(
        'app_sgbh.services.formulario_2a._formularios_busqueda',
        return_value=queryset,
    ):
        result = Formulario2AService.search(
            formulario_2a_id=10,
            codigo_sinpad='45821',
            tipo_peligro_id=3,
            departamento_id='20',
            provincia_id='01',
            distrito_id='01',
            fecha_desde=date(2026, 1, 1),
            fecha_hasta=date(2026, 3, 31),
            barrio_sector_urbanizacion='Santa Rosa',
            localidad='Centro',
            estado_registro_id=1,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'formulario_2a_id': 10}),
        ((), {'emergencia__codigo_sinpad': '45821'}),
        ((), {'emergencia__tipo_peligro_id': 3}),
        ((), {'departamento_id': '20'}),
        ((), {'provincia_id': '01'}),
        ((), {'distrito_id': '01'}),
        ((), {'fecha_empadronamiento__gte': date(2026, 1, 1)}),
        ((), {'fecha_empadronamiento__lte': date(2026, 3, 31)}),
        (
            (),
            {
                'barrio_sector_urbanizacion__ilike_pattern': text_like_pattern(
                    'Santa Rosa'
                )
            },
        ),
        ((), {'localidad__ilike_pattern': text_like_pattern('Centro')}),
        ((), {'estado_registro_id': 1}),
    ]


def test_serializer_nests_viviendas_on_each_formulario():
    formulario = SimpleNamespace(
        formulario_2a_id=10,
        emergencia_id=3,
        departamento_id='20',
        provincia_id='01',
        distrito_id='01',
        fecha_empadronamiento=date(2026, 3, 1),
        hora_empadronamiento=time(8, 30),
        localidad='Centro',
        barrio_sector_urbanizacion='Santa Rosa',
        centro_poblado=None,
        caserio=None,
        anexo=None,
        calle_manzana=None,
        edificio_piso_dpto=None,
        otros_ubicacion=None,
        numero_hoja=1,
        total_hojas=2,
        institucion=None,
        evaluador_id=4,
        estado_registro_id=1,
        c_usuari_login='mmedina',
        fecha_creacion=datetime(2026, 3, 1, 8, 0),
        fecha_modificacion=None,
        distrito_nombre='Piura',
        emergencia=SimpleNamespace(
            codigo_sinpad='45821',
            tipo_peligro_id=2,
            tipo_peligro=SimpleNamespace(nombre='Inundación'),
        ),
        evaluador=SimpleNamespace(
            apellido_paterno='Perez',
            apellido_materno='Lopez',
            nombres='Ana',
        ),
        viviendas=[
            SimpleNamespace(vivienda_id=7, numero_lote='L-1'),
            SimpleNamespace(vivienda_id=8, numero_lote=None),
        ],
    )

    data = Formulario2ABusquedaSerializer(formulario).data

    assert data['formulario_2a_id'] == 10
    assert data['codigo_sinpad'] == '45821'
    assert data['tipo_peligro_id'] == 2
    assert data['nombre_tipo_peligro'] == 'Inundación'
    assert data['distrito_nombre'] == 'Piura'
    assert data['evaluador_nombre'] == 'Perez Lopez Ana'
    assert data['viviendas'] == [
        {'vivienda_id': 7, 'numero_lote': 'L-1'},
        {'vivienda_id': 8, 'numero_lote': None},
    ]


def test_get_formularios_2a_buscar_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/formularios-2a/buscar/',
        {
            'formulario_2a_id': '10',
            'codigo_sinpad': '45821',
            'tipo_peligro_id': '3',
            'departamento_id': '20',
            'fecha_desde': '2026-01-01',
            'fecha_hasta': '2026-03-31',
            'estado_registro_id': '1',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'formulario_2a_id': 10, 'viviendas': []}]

    with (
        patch(
            'app_sgbh.views.formulario_2a_view.Formulario2AService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.formulario_2a_view.Formulario2ABusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = Formulario2ABuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        formulario_2a_id=10,
        codigo_sinpad='45821',
        tipo_peligro_id=3,
        departamento_id='20',
        provincia_id=None,
        distrito_id=None,
        barrio_sector_urbanizacion=None,
        localidad=None,
        estado_registro_id=1,
        fecha_desde=date(2026, 1, 1),
        fecha_hasta=date(2026, 3, 31),
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_formularios_2a_buscar_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.formulario_2a_view.Formulario2AService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.formulario_2a_view.Formulario2ABusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = Formulario2ABuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        formulario_2a_id=None,
        codigo_sinpad=None,
        tipo_peligro_id=None,
        departamento_id=None,
        provincia_id=None,
        distrito_id=None,
        barrio_sector_urbanizacion=None,
        localidad=None,
        estado_registro_id=None,
        fecha_desde=None,
        fecha_hasta=None,
    )


def test_get_formularios_2a_buscar_rejects_inverted_period():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/formularios-2a/buscar/',
        {'fecha_desde': '2026-04-01', 'fecha_hasta': '2026-03-01'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2ABuscarView.as_view()(request)

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro fecha_desde no puede ser posterior a fecha_hasta'
    )


def test_get_formularios_2a_buscar_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/formularios-2a/buscar/',
        {'departamento_id': '200'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2ABuscarView.as_view()(request)

    assert response.status_code == 400
    assert 'departamento_id' in response.data['error']
