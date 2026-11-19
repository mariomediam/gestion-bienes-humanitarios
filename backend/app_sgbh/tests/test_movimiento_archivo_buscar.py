from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

import pytest
from django.urls import resolve
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers.movimiento_archivo import (
    MovimientoArchivoBusquedaSerializer,
)
from app_sgbh.services.movimiento_archivo import MovimientoArchivoService
from app_sgbh.views.movimiento_archivo_view import MovimientoArchivoBuscarView


_ARCHIVO_ID = UUID('11111111-2222-4333-8444-555555555555')


def test_search_returns_every_row_when_no_filter_is_sent():
    with patch(
        'app_sgbh.services.movimiento_archivo.MovimientoArchivo'
    ) as model:
        queryset = model.objects.select_related.return_value
        queryset.order_by.return_value = 'rows'

        result = MovimientoArchivoService.search()

    assert result == 'rows'
    model.objects.select_related.assert_called_once_with('movimiento')
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('fecha_registro')


def test_search_combines_filters_with_and():
    with patch(
        'app_sgbh.services.movimiento_archivo.MovimientoArchivo'
    ) as model:
        queryset = model.objects.select_related.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = MovimientoArchivoService.search(
            archivo_id=_ARCHIVO_ID,
            movimiento_id=10,
            esta_activo=False,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'archivo_id': _ARCHIVO_ID}),
        ((), {'movimiento_id': 10}),
        ((), {'esta_activo': False}),
    ]
    queryset.order_by.assert_called_once_with('fecha_registro')


def test_serializer_returns_joined_columns_and_omits_the_internal_path():
    row = SimpleNamespace(
        archivo_id=_ARCHIVO_ID,
        movimiento_id=10,
        nombre_original='guia.PDF',
        nombre_archivo='abc.pdf',
        ruta_archivo='movimientos/10/abc.pdf',
        extension='pdf',
        tamano_bytes=8,
        esta_activo=True,
        fecha_registro=timezone.now(),
        c_usuari_login='mmedina',
        movimiento=SimpleNamespace(
            almacen_id=3,
            documento_referencia='GR-100',
        ),
    )

    data = MovimientoArchivoBusquedaSerializer(row).data

    assert 'ruta_archivo' not in data
    assert data['archivo_id'] == str(_ARCHIVO_ID)
    assert data['movimiento_id'] == 10
    assert data['nombre_original'] == 'guia.PDF'
    assert data['nombre_archivo'] == 'abc.pdf'
    assert data['extension'] == 'pdf'
    assert data['tamano_bytes'] == 8
    assert data['esta_activo'] is True
    assert data['c_usuari_login'] == 'mmedina'
    assert data['almacen_id'] == 3
    assert data['documento_referencia'] == 'GR-100'


def test_serializer_returns_null_optional_columns():
    row = SimpleNamespace(
        archivo_id=_ARCHIVO_ID,
        movimiento_id=10,
        nombre_original='guia.pdf',
        nombre_archivo='abc.pdf',
        ruta_archivo='movimientos/10/abc.pdf',
        extension=None,
        tamano_bytes=None,
        esta_activo=False,
        fecha_registro=timezone.now(),
        c_usuari_login='mmedina',
        movimiento=SimpleNamespace(
            almacen_id=3,
            documento_referencia=None,
        ),
    )

    data = MovimientoArchivoBusquedaSerializer(row).data

    assert data['extension'] is None
    assert data['tamano_bytes'] is None
    assert data['documento_referencia'] is None


def test_get_archivos_buscar_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/movimientos/archivos/buscar/',
        {
            'archivo_id': f'  {_ARCHIVO_ID} ',
            'movimiento_id': '10',
            'esta_activo': '0',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'archivo_id': str(_ARCHIVO_ID), 'movimiento_id': 10}]

    with (
        patch(
            'app_sgbh.views.movimiento_archivo_view.MovimientoArchivoService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.movimiento_archivo_view.MovimientoArchivoBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = MovimientoArchivoBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        archivo_id=_ARCHIVO_ID,
        movimiento_id=10,
        esta_activo=False,
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_archivos_buscar_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/movimientos/archivos/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.movimiento_archivo_view.MovimientoArchivoService.search',
            return_value='queryset',
        ) as search,
        patch(
            'app_sgbh.views.movimiento_archivo_view.MovimientoArchivoBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = MovimientoArchivoBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        archivo_id=None,
        movimiento_id=None,
        esta_activo=None,
    )


@pytest.mark.parametrize(
    ('params', 'message'),
    [
        ({'archivo_id': 'x'}, 'El filtro archivo_id debe ser un UUID'),
        (
            {'movimiento_id': 'x'},
            'El filtro movimiento_id debe ser un número entero',
        ),
        (
            {'esta_activo': 'si'},
            'El filtro esta_activo debe ser 1, 0, true o false',
        ),
    ],
)
def test_get_archivos_buscar_rejects_invalid_filters(params, message):
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/movimientos/archivos/buscar/', params)
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = MovimientoArchivoBuscarView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == message


def test_get_archivos_buscar_hides_internal_errors():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/movimientos/archivos/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.movimiento_archivo_view.MovimientoArchivoService.search',
        side_effect=RuntimeError(r'C:\secret\guia.pdf'),
    ):
        response = MovimientoArchivoBuscarView.as_view()(request)

    assert response.status_code == 500
    assert response.data['error'] == (
        'No se pudo obtener la búsqueda de archivos del movimiento de almacén'
    )


def test_archivos_buscar_url_resolves():
    match = resolve('/api/sgbh/movimientos/archivos/buscar/')

    assert match.url_name == 'movimientos-archivos-buscar'
