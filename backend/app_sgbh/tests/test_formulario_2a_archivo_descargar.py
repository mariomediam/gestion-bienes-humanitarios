from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

import pytest
from django.test import override_settings
from django.urls import Resolver404, resolve
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.formulario_2a_archivo import (
    Formulario2AArchivoDownload,
    Formulario2AArchivoService,
    Formulario2AArchivoServiceError,
)
from app_sgbh.views.formulario_2a_archivo_view import Formulario2AArchivoDescargarView


_ARCHIVO_ID = UUID('11111111-2222-4333-8444-555555555555')
_RUTA = 'formularios-2a/10/abc123.pdf'


class _DoesNotExist(Exception):
    pass


def _row(**extra):
    data = {
        'esta_activo': True,
        'ruta_archivo': _RUTA,
        'nombre_original': 'Ficha.pdf',
        'nombre_archivo': 'abc123.pdf',
        'extension': 'pdf',
    }
    data.update(extra)
    return SimpleNamespace(**data)


def _stored_file(tmp_path, content=b'%PDF-1.4 ficha'):
    destination = tmp_path.joinpath(*_RUTA.split('/'))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return destination


def _get_request():
    factory = APIRequestFactory()
    request = factory.get(
        f'/api/sgbh/formularios-2a/10/archivos/{_ARCHIVO_ID}/descargar/'
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    return request


def _response_body(response):
    try:
        return b''.join(response.streaming_content)
    finally:
        response.close()


def test_download_returns_the_file_inside_storage(tmp_path):
    stored = _stored_file(tmp_path)
    row = _row()

    with (
        override_settings(STORAGE_ROOT=tmp_path),
        patch('app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo') as archivo,
    ):
        archivo.objects.get.return_value = row
        result = Formulario2AArchivoService.download(10, _ARCHIVO_ID)

    archivo.objects.get.assert_called_once_with(
        pk=_ARCHIVO_ID,
        formulario_2a_id=10,
    )
    assert result.path == stored.resolve()
    assert result.filename == 'Ficha.pdf'
    assert result.content_type == 'application/pdf'


def test_download_keeps_an_inactive_file_available(tmp_path):
    _stored_file(tmp_path)

    with (
        override_settings(STORAGE_ROOT=tmp_path),
        patch('app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo') as archivo,
    ):
        archivo.objects.get.return_value = _row(esta_activo=False)
        result = Formulario2AArchivoService.download(10, _ARCHIVO_ID)

    assert result.filename == 'Ficha.pdf'


def test_download_uses_the_extension_for_the_content_type(tmp_path):
    ruta = 'formularios-2a/10/foto.jpg'
    destination = tmp_path.joinpath(*ruta.split('/'))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(b'\xff\xd8\xff')

    with (
        override_settings(STORAGE_ROOT=tmp_path),
        patch('app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo') as archivo,
    ):
        archivo.objects.get.return_value = _row(
            ruta_archivo=ruta,
            nombre_original='foto.jpg',
            nombre_archivo='foto.jpg',
            extension='jpg',
        )
        result = Formulario2AArchivoService.download(10, _ARCHIVO_ID)

    assert result.content_type == 'image/jpeg'


def test_download_falls_back_when_the_original_name_is_unsafe(tmp_path):
    _stored_file(tmp_path)

    with (
        override_settings(STORAGE_ROOT=tmp_path),
        patch('app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo') as archivo,
    ):
        archivo.objects.get.return_value = _row(nombre_original='ficha\r\n.pdf')
        result = Formulario2AArchivoService.download(10, _ARCHIVO_ID)

    assert result.filename == 'abc123.pdf'


def test_download_rejects_a_missing_row():
    with patch(
        'app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo'
    ) as archivo:
        archivo.DoesNotExist = _DoesNotExist
        archivo.objects.get.side_effect = _DoesNotExist

        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.download(10, _ARCHIVO_ID)

    assert exc.value.not_found is True
    assert exc.value.message == 'El archivo indicado no existe'


def test_download_rejects_a_missing_file_on_disk(tmp_path):
    with (
        override_settings(STORAGE_ROOT=tmp_path),
        patch('app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo') as archivo,
    ):
        archivo.objects.get.return_value = _row()

        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.download(10, _ARCHIVO_ID)

    assert exc.value.not_found is True
    assert _RUTA not in exc.value.message


def test_download_rejects_a_path_outside_storage(tmp_path):
    root = tmp_path / 'storage'
    root.mkdir()
    outside = tmp_path / 'secreto.pdf'
    outside.write_bytes(b'secreto')

    with (
        override_settings(STORAGE_ROOT=root),
        patch('app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo') as archivo,
    ):
        archivo.objects.get.return_value = _row(ruta_archivo='../secreto.pdf')

        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.download(10, _ARCHIVO_ID)

    assert exc.value.not_found is True
    assert 'secreto' not in exc.value.message
    assert outside.read_bytes() == b'secreto'


def test_download_rejects_an_absolute_path(tmp_path):
    outside = tmp_path / 'absoluto.pdf'
    outside.write_bytes(b'secreto')

    with (
        override_settings(STORAGE_ROOT=tmp_path / 'storage'),
        patch('app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo') as archivo,
    ):
        (tmp_path / 'storage').mkdir()
        archivo.objects.get.return_value = _row(ruta_archivo=str(outside))

        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.download(10, _ARCHIVO_ID)

    assert exc.value.not_found is True
    assert str(outside) not in exc.value.message


def test_download_url_accepts_a_uuid():
    match = resolve(
        f'/api/sgbh/formularios-2a/10/archivos/{_ARCHIVO_ID}/descargar/'
    )

    assert match.kwargs['archivo_id'] == _ARCHIVO_ID
    assert match.url_name == 'formularios-2a-archivos-descargar'


def test_download_url_rejects_an_integer_id():
    with pytest.raises(Resolver404):
        resolve('/api/sgbh/formularios-2a/10/archivos/9/descargar/')


def test_download_archivos_returns_the_file(tmp_path):
    stored = tmp_path / 'ficha.pdf'
    stored.write_bytes(b'%PDF-1.4 ficha')
    descarga = Formulario2AArchivoDownload(
        path=stored,
        filename='Ficha.pdf',
        content_type='application/pdf',
    )

    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.download',
        return_value=descarga,
    ) as download:
        response = Formulario2AArchivoDescargarView.as_view()(
            _get_request(),
            formulario_2a_id=10,
            archivo_id=_ARCHIVO_ID,
        )
        body = _response_body(response)

    assert response.status_code == 200
    assert body == b'%PDF-1.4 ficha'
    assert response['Content-Type'] == 'application/pdf'
    disposition = response['Content-Disposition']
    assert disposition.startswith('attachment;')
    assert 'Ficha.pdf' in disposition
    assert response['X-Content-Type-Options'] == 'nosniff'
    assert response['Cache-Control'] == 'private, no-store'
    assert _RUTA not in disposition
    download.assert_called_once_with(10, _ARCHIVO_ID)


def test_download_archivos_returns_not_found():
    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.download',
        side_effect=Formulario2AArchivoServiceError(
            'El archivo indicado no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AArchivoDescargarView.as_view()(
            _get_request(),
            formulario_2a_id=10,
            archivo_id=_ARCHIVO_ID,
        )

    assert response.status_code == 404
    assert response.data['error'] == 'El archivo indicado no existe'


@pytest.mark.parametrize(
    ('formulario_2a_id', 'archivo_id', 'message'),
    [
        (0, _ARCHIVO_ID, 'formulario_2a_id debe ser un número entero'),
        (10, 'no-es-uuid', 'archivo_id debe ser un UUID'),
        (2147483648, _ARCHIVO_ID, 'formulario_2a_id debe ser un número entero'),
    ],
)
def test_download_archivos_rejects_an_invalid_id(
    formulario_2a_id,
    archivo_id,
    message,
):
    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.download',
    ) as download:
        response = Formulario2AArchivoDescargarView.as_view()(
            _get_request(),
            formulario_2a_id=formulario_2a_id,
            archivo_id=archivo_id,
        )

    assert response.status_code == 400
    assert message in response.data['error']
    download.assert_not_called()


def test_download_archivos_hides_internal_errors():
    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.download',
        side_effect=RuntimeError(r'C:\secret\ficha.pdf'),
    ):
        response = Formulario2AArchivoDescargarView.as_view()(
            _get_request(),
            formulario_2a_id=10,
            archivo_id=_ARCHIVO_ID,
        )

    assert response.status_code == 500
    assert response.data['error'] == (
        'No se pudo descargar el archivo del formulario EDAN 2A'
    )
    assert 'secret' not in response.data['error']
