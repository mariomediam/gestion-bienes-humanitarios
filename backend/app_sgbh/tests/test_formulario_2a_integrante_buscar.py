from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import parse_integrante_id
from app_sgbh.serializers.formulario_2a_integrante import IntegranteBusquedaSerializer
from app_sgbh.services.formulario_2a_integrante import Formulario2AIntegranteService
from app_sgbh.views.formulario_2a_integrante_view import Formulario2AIntegranteBuscarView


def _integrante(**overrides):
    persona = SimpleNamespace(
        tipo_documento_id=1,
        numero_documento='12345678',
        apellido_paterno='Medina',
        apellido_materno='Rios',
        nombres='Mario',
        fecha_nacimiento=date(1990, 5, 2),
        sexo='M',
        telefono='999111222',
        correo='mario@example.com',
        esta_activo=True,
        tipo_documento=SimpleNamespace(codigo='DNI'),
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
        integrante_id=31,
        familia_id=8,
        persona_id=15,
        rol_familiar_id=2,
        numero_orden=1,
        edad=35,
        condicion_persona_id=1,
        tipo_danio_personal_id=1,
        grado_lesion_id=3,
        gestante_semanas=None,
        tipo_discapacidad_id=4,
        enfermedad_cronica_id=5,
        fecha_creacion=datetime(2026, 3, 1, 8, 0, tzinfo=timezone.utc),
        persona=persona,
        rol_familiar=SimpleNamespace(nombre='Jefe'),
        condicion_persona=SimpleNamespace(nombre='Damnificado'),
        tipo_danio_personal=SimpleNamespace(nombre='Herido'),
        grado_lesion=SimpleNamespace(nombre='Leve'),
        tipo_discapacidad=SimpleNamespace(nombre='Motriz'),
        enfermedad_cronica=SimpleNamespace(nombre='Diabetes'),
        familia=familia,
    )
    for key, value in overrides.items():
        setattr(row, key, value)
    return row


def test_search_returns_every_row_when_no_filter_is_sent():
    with patch(
        'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
    ) as model:
        queryset = model.objects.select_related.return_value
        queryset.order_by.return_value = 'rows'

        result = Formulario2AIntegranteService.search()

    assert result == 'rows'
    model.objects.select_related.assert_called_once_with(
        'persona',
        'persona__tipo_documento',
        'rol_familiar',
        'condicion_persona',
        'tipo_danio_personal',
        'grado_lesion',
        'tipo_discapacidad',
        'enfermedad_cronica',
        'familia',
        'familia__vivienda',
        'familia__vivienda__formulario_2a',
        'familia__vivienda__formulario_2a__emergencia',
    )
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('integrante_id')


def test_search_combines_filters_with_and():
    with patch(
        'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
    ) as model:
        queryset = model.objects.select_related.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = Formulario2AIntegranteService.search(
            integrante_id=31,
            familia_id=8,
            persona_id=15,
            formulario_2a_id=10,
            codigo_sinpad='261404',
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'integrante_id': 31}),
        ((), {'familia_id': 8}),
        ((), {'persona_id': 15}),
        ((), {'familia__vivienda__formulario_2a_id': 10}),
        (
            (),
            {
                'familia__vivienda__formulario_2a__emergencia__codigo_sinpad': (
                    '261404'
                )
            },
        ),
    ]
    queryset.order_by.assert_called_once_with('integrante_id')


def test_serializer_returns_joined_columns():
    data = IntegranteBusquedaSerializer(_integrante()).data

    assert data['integrante_id'] == 31
    assert data['familia_id'] == 8
    assert data['persona_id'] == 15
    assert data['rol_familiar_id'] == 2
    assert data['numero_orden'] == 1
    assert data['edad'] == 35
    assert data['condicion_persona_id'] == 1
    assert data['tipo_danio_personal_id'] == 1
    assert data['grado_lesion_id'] == 3
    assert data['gestante_semanas'] is None
    assert data['tipo_discapacidad_id'] == 4
    assert data['enfermedad_cronica_id'] == 5
    assert data['tipo_documento_id'] == 1
    assert data['numero_documento'] == '12345678'
    assert data['apellido_paterno'] == 'Medina'
    assert data['apellido_materno'] == 'Rios'
    assert data['nombres'] == 'Mario'
    assert data['fecha_nacimiento'] == '1990-05-02'
    assert data['sexo'] == 'M'
    assert data['telefono'] == '999111222'
    assert data['correo'] == 'mario@example.com'
    assert data['persona_esta_activo'] is True
    assert data['tipo_documento_codigo'] == 'DNI'
    assert data['rol_familiar_nombre'] == 'Jefe'
    assert data['condicion_persona_nombre'] == 'Damnificado'
    assert data['tipo_danio_personal_nombre'] == 'Herido'
    assert data['grado_lesion_nombre'] == 'Leve'
    assert data['tipo_discapacidad_nombre'] == 'Motriz'
    assert data['enfermedad_cronica_nombre'] == 'Diabetes'
    assert data['vivienda_id'] == 4
    assert data['formulario_2a_id'] == 10
    assert data['emergencia_id'] == 6
    assert data['codigo_sinpad'] == 'SIN-1'


def test_serializer_returns_null_names_when_optional_joins_are_missing():
    row = _integrante()
    row.tipo_danio_personal_id = None
    row.grado_lesion_id = None
    row.tipo_discapacidad_id = None
    row.enfermedad_cronica_id = None
    row.tipo_danio_personal = None
    row.grado_lesion = None
    row.tipo_discapacidad = None
    row.enfermedad_cronica = None
    row.persona.tipo_documento_id = None
    row.persona.numero_documento = None
    row.persona.tipo_documento = None
    row.familia.vivienda.formulario_2a.emergencia.codigo_sinpad = None

    data = IntegranteBusquedaSerializer(row).data

    assert data['tipo_documento_id'] is None
    assert data['numero_documento'] is None
    assert data['tipo_documento_codigo'] is None
    assert data['tipo_danio_personal_nombre'] is None
    assert data['grado_lesion_nombre'] is None
    assert data['tipo_discapacidad_nombre'] is None
    assert data['enfermedad_cronica_nombre'] is None
    assert data['codigo_sinpad'] is None


@pytest.mark.parametrize(
    ('value', 'message'),
    [
        ('abc', 'integrante_id debe ser un número entero'),
        ('2147483648', 'integrante_id debe ser un número entero'),
    ],
)
def test_parse_integrante_id_rejects_invalid_values(value, message):
    _parsed, error = parse_integrante_id(value)

    assert error is not None
    assert message in error


def test_get_integrantes_buscar_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/integrantes/buscar/',
        {
            'integrante_id': '31',
            'familia_id': '8',
            'persona_id': '15',
            'formulario_2a_id': '10',
            'codigo_sinpad': ' 261404 ',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'integrante_id': 31, 'familia_id': 8, 'persona_id': 15}]

    with (
        patch(
            'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.formulario_2a_integrante_view.IntegranteBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = Formulario2AIntegranteBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        integrante_id=31,
        familia_id=8,
        persona_id=15,
        formulario_2a_id=10,
        codigo_sinpad='261404',
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_integrantes_buscar_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/integrantes/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.formulario_2a_integrante_view.IntegranteBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = Formulario2AIntegranteBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        integrante_id=None,
        familia_id=None,
        persona_id=None,
        formulario_2a_id=None,
        codigo_sinpad=None,
    )


def test_get_integrantes_buscar_rejects_codigo_sinpad_too_long():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/integrantes/buscar/',
        {'codigo_sinpad': 'a' * 31},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AIntegranteBuscarView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == (
        'El filtro codigo_sinpad no debe superar 30 caracteres'
    )


def test_get_integrantes_buscar_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/integrantes/buscar/',
        {'persona_id': 'x'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AIntegranteBuscarView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El filtro persona_id debe ser un número entero'
