from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import (
    parse_nombre_completo,
    parse_numero_documento,
    parse_persona_id,
    parse_tipo_documento_id,
)
from app_sgbh.serializers import PersonaBusquedaSerializer
from app_sgbh.services.persona import PersonaService
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.persona_view import PersonaBuscarView, _parse_busqueda


def test_parse_busqueda_omits_every_filter_when_params_are_empty():
    parsed, error = _parse_busqueda({})

    assert error is None
    assert parsed == {
        'persona_id': None,
        'tipo_documento_id': None,
        'numero_documento': None,
        'nombre_completo': None,
    }


def test_parse_busqueda_accepts_filters_and_trims_text():
    parsed, error = _parse_busqueda(
        {
            'persona_id': '4',
            'tipo_documento_id': '2',
            'numero_documento': '  12345678  ',
            'nombre_completo': '  medina lopez mario  ',
        }
    )

    assert error is None
    assert parsed == {
        'persona_id': 4,
        'tipo_documento_id': 2,
        'numero_documento': '12345678',
        'nombre_completo': 'medina lopez mario',
    }


@pytest.mark.parametrize(
    ('parser', 'value', 'message'),
    [
        (parse_persona_id, 'abc', 'persona_id debe ser un número entero'),
        (parse_persona_id, '3000000000', 'persona_id debe ser un número entero'),
        (parse_tipo_documento_id, '2.5', 'tipo_documento_id debe ser un número entero'),
        (parse_tipo_documento_id, '40000', 'tipo_documento_id debe ser un número entero'),
        (parse_numero_documento, 'D' * 21, 'numero_documento no debe superar 20'),
        (parse_nombre_completo, 'N' * 253, 'nombre_completo no debe superar 252'),
    ],
)
def test_parsers_reject_invalid_filters(parser, value, message):
    _parsed, error = parser(value)

    assert error is not None
    assert message in error


def test_search_returns_every_row_when_no_filter_is_sent():
    with patch('app_sgbh.services.persona.Persona') as persona:
        queryset = persona.objects.select_related.return_value
        queryset.order_by.return_value = 'rows'

        result = PersonaService.search()

    assert result == 'rows'
    persona.objects.select_related.assert_called_once_with('tipo_documento')
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with(
        'apellido_paterno',
        'apellido_materno',
        'nombres',
    )


def test_search_combines_exact_and_name_filters():
    with patch('app_sgbh.services.persona.Persona') as persona:
        queryset = persona.objects.select_related.return_value
        queryset.alias.return_value = queryset
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = PersonaService.search(
            persona_id=4,
            tipo_documento_id=2,
            numero_documento='12345678',
            nombre_completo='medina lopez mario',
        )

    assert result == 'rows'
    queryset.alias.assert_called_once()
    assert queryset.filter.call_args_list == [
        ((), {'persona_id': 4}),
        ((), {'tipo_documento_id': 2}),
        ((), {'numero_documento': '12345678'}),
        (
            (),
            {
                'nombre_completo_busqueda__ilike_pattern': text_like_pattern(
                    'medina lopez mario'
                ),
            },
        ),
    ]
    assert text_like_pattern('medina lopez mario') == '%medina%lopez%mario%'


def test_persona_busqueda_serializer_includes_document_type():
    persona = SimpleNamespace(
        persona_id=4,
        tipo_documento_id=2,
        tipo_documento=SimpleNamespace(
            codigo='DNI',
            nombre='Documento nacional de identidad',
            esta_activo=True,
        ),
        numero_documento='12345678',
        apellido_paterno='Medina',
        apellido_materno='Lopez',
        nombres='Mario',
        fecha_nacimiento=date(1990, 5, 12),
        sexo='M',
        telefono='969000000',
        correo='mario@example.com',
        esta_activo=True,
        fecha_creacion='2026-10-09T12:00:00Z',
        c_usuari_login='mmedina',
        fecha_modificacion=None,
    )

    data = PersonaBusquedaSerializer(persona).data

    assert data['codigo_tipo_documento'] == 'DNI'
    assert data['nombre_tipo_documento'] == 'Documento nacional de identidad'
    assert data['esta_activo_tipo_documento'] is True


def test_persona_busqueda_serializer_returns_null_document_type():
    persona = SimpleNamespace(
        persona_id=4,
        tipo_documento_id=None,
        tipo_documento=None,
        numero_documento=None,
        apellido_paterno='Medina',
        apellido_materno='Lopez',
        nombres='Mario',
        fecha_nacimiento=date(1990, 5, 12),
        sexo='M',
        telefono='969000000',
        correo='mario@example.com',
        esta_activo=True,
        fecha_creacion='2026-10-09T12:00:00Z',
        c_usuari_login='mmedina',
        fecha_modificacion=None,
    )

    data = PersonaBusquedaSerializer(persona).data

    assert data['codigo_tipo_documento'] is None
    assert data['nombre_tipo_documento'] is None
    assert data['esta_activo_tipo_documento'] is None


def test_persona_busqueda_serializer_returns_null_fecha_nacimiento():
    persona = SimpleNamespace(
        persona_id=4,
        tipo_documento_id=None,
        tipo_documento=None,
        numero_documento=None,
        apellido_paterno='Medina',
        apellido_materno='Lopez',
        nombres='Mario',
        fecha_nacimiento=None,
        sexo='M',
        telefono='',
        correo='',
        esta_activo=True,
        fecha_creacion='2026-10-09T12:00:00Z',
        c_usuari_login='mmedina',
        fecha_modificacion=None,
    )

    data = PersonaBusquedaSerializer(persona).data

    assert data['fecha_nacimiento'] is None


def test_get_personas_buscar_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/personas/buscar/',
        {'persona_id': '4', 'nombre_completo': 'medina lopez mario'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'persona_id': 4, 'nombres': 'Mario'}]

    with (
        patch(
            'app_sgbh.views.persona_view.PersonaService.search',
            return_value='queryset',
        ) as search,
        patch('app_sgbh.views.persona_view.PersonaBusquedaSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = PersonaBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        persona_id=4,
        tipo_documento_id=None,
        numero_documento=None,
        nombre_completo='medina lopez mario',
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_personas_buscar_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/personas/buscar/', {'persona_id': 'abc'})
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = PersonaBuscarView.as_view()(request)

    assert response.status_code == 400
    assert 'persona_id debe ser un número entero' in response.data['error']
