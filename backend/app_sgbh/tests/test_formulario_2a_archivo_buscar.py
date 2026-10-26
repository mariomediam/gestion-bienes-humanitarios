from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

import pytest
from django.urls import resolve
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import parse_archivo_id
from app_sgbh.serializers.formulario_2a_archivo import (
    Formulario2AArchivoBusquedaSerializer,
)
from app_sgbh.services.formulario_2a_archivo import Formulario2AArchivoService
from app_sgbh.views.formulario_2a_archivo_view import Formulario2AArchivoBuscarView


_ARCHIVO_ID = UUID('11111111-2222-4333-8444-555555555555')


def test_search_returns_every_row_when_no_filter_is_sent():
    with patch(
        'app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo'
    ) as model:
        queryset = model.objects.select_related.return_value
        queryset.order_by.return_value = 'rows'

        result = Formulario2AArchivoService.search()

    assert result == 'rows'
    model.objects.select_related.assert_called_once_with(
        'formulario_2a',
        'formulario_2a__emergencia',
    )
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('fecha_registro')


def test_search_combines_filters_with_and():
    with patch(
        'app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo'
    ) as model:
        queryset = model.objects.select_related.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = Formulario2AArchivoService.search(
            archivo_id=_ARCHIVO_ID,
            formulario_2a_id=10,
            esta_activo=False,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'archivo_id': _ARCHIVO_ID}),
        ((), {'formulario_2a_id': 10}),
        ((), {'esta_activo': False}),
    ]
    queryset.order_by.assert_called_once_with('fecha_registro')


def test_serializer_returns_joined_columns_and_omits_the_internal_path():
    row = SimpleNamespace(
        archivo_id=_ARCHIVO_ID,
        formulario_2a_id=10,
        nombre_original='ficha.PDF',
        nombre_archivo='abc.pdf',
        ruta_archivo='formularios-2a/10/abc.pdf',
        extension='pdf',
        tamano_bytes=8,
        esta_activo=True,
        fecha_registro=timezone.now(),
        c_usuari_login='mmedina',
        formulario_2a=SimpleNamespace(
            emergencia_id=9,
            emergencia=SimpleNamespace(codigo_sinpad='261404'),
        ),
    )

    data = Formulario2AArchivoBusquedaSerializer(row).data

    assert 'ruta_archivo' not in data
    assert data['archivo_id'] == str(_ARCHIVO_ID)
    assert data['formulario_2a_id'] == 10
    assert data['nombre_original'] == 'ficha.PDF'
    assert data['nombre_archivo'] == 'abc.pdf'
    assert data['extension'] == 'pdf'
    assert data['tamano_bytes'] == 8
    assert data['esta_activo'] is True
    assert data['c_usuari_login'] == 'mmedina'
    assert data['emergencia_id'] == 9
    assert data['codigo_sinpad'] == '261404'


def test_serializer_returns_null_optional_columns():
    row = SimpleNamespace(
        archivo_id=_ARCHIVO_ID,
        formulario_2a_id=10,
        nombre_original='ficha.pdf',
        nombre_archivo='abc.pdf',
        ruta_archivo='formularios-2a/10/abc.pdf',
        extension=None,
        tamano_bytes=None,
        esta_activo=False,
        fecha_registro=timezone.now(),
        c_usuari_login='mmedina',
        formulario_2a=SimpleNamespace(
            emergencia_id=9,
            emergencia=SimpleNamespace(codigo_sinpad=None),
        ),
    )

    data = Formulario2AArchivoBusquedaSerializer(row).data

    assert data['extension'] is None
    assert data['tamano_bytes'] is None
    assert data['codigo_sinpad'] is None


@pytest.mark.parametrize(
    ('value', 'message'),
    [
        ('abc', 'archivo_id debe ser un UUID'),
        ('9', 'archivo_id debe ser un UUID'),
    ],
)
def test_parse_archivo_id_rejects_invalid_values(value, message):
    _parsed, error = parse_archivo_id(value)

    assert error is not None
    assert message in error


def test_parse_archivo_id_accepts_a_uuid_and_an_empty_value():
    parsed, error = parse_archivo_id(f'  {_ARCHIVO_ID}  ')
    omitted, omitted_error = parse_archivo_id('')

    assert error is None
    assert parsed == _ARCHIVO_ID
    assert omitted is None
    assert omitted_error is None


def test_get_archivos_buscar_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/formularios-2a/archivos/buscar/',
        {
            'archivo_id': f'  {_ARCHIVO_ID} ',
            'formulario_2a_id': '10',
            'esta_activo': '0',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'archivo_id': str(_ARCHIVO_ID), 'formulario_2a_id': 10}]

    with (
        patch(
            'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = Formulario2AArchivoBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        archivo_id=_ARCHIVO_ID,
        formulario_2a_id=10,
        esta_activo=False,
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_archivos_buscar_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/archivos/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = Formulario2AArchivoBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        archivo_id=None,
        formulario_2a_id=None,
        esta_activo=None,
    )


@pytest.mark.parametrize(
    ('params', 'message'),
    [
        ({'archivo_id': 'x'}, 'El filtro archivo_id debe ser un UUID'),
        (
            {'formulario_2a_id': 'x'},
            'El filtro formulario_2a_id debe ser un número entero',
        ),
        (
            {'esta_activo': 'si'},
            'El filtro esta_activo debe ser 1, 0, true o false',
        ),
    ],
)
def test_get_archivos_buscar_rejects_invalid_filters(params, message):
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/archivos/buscar/', params)
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AArchivoBuscarView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == message


def test_get_archivos_buscar_hides_internal_errors():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/archivos/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.search',
        side_effect=RuntimeError(r'C:\secret\ficha.pdf'),
    ):
        response = Formulario2AArchivoBuscarView.as_view()(request)

    assert response.status_code == 500
    assert response.data['error'] == (
        'No se pudo obtener la búsqueda de archivos del formulario EDAN 2A'
    )


def test_archivos_buscar_url_resolves():
    match = resolve('/api/sgbh/formularios-2a/archivos/buscar/')

    assert match.url_name == 'formularios-2a-archivos-buscar'
