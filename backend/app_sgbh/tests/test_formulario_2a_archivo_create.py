from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.models import Formulario2AArchivo
from app_sgbh.serializers.formulario_2a_archivo import Formulario2AArchivoSerializer
from app_sgbh.services.formulario_2a_archivo import (
    Formulario2AArchivoService,
    Formulario2AArchivoServiceError,
)
from app_sgbh.views.formulario_2a_archivo_view import Formulario2AArchivoCreateView

_FIXED_UUID = UUID('12345678-1234-5678-1234-567812345678')
_ARCHIVO_ID = UUID('11111111-2222-4333-8444-555555555555')
_FIXED_NAME = f'{_FIXED_UUID.hex}.pdf'


class _DoesNotExist(Exception):
    pass


def _upload(name='ficha.pdf', content=b'%PDF-1.4'):
    return SimpleUploadedFile(name, content, content_type='application/pdf')


def _storage(tmp_path, **extra):
    values = {
        'STORAGE_ROOT': tmp_path,
        'STORAGE_ALLOWED_EXTENSIONS': ['pdf', 'jpg', 'jpeg', 'png'],
        'STORAGE_MAX_UPLOAD_BYTES': 1024,
    }
    values.update(extra)
    return override_settings(**values)


def _formulario_existente(formulario, estado_registro_id=1):
    formulario.objects.select_for_update.return_value.get.return_value = (
        SimpleNamespace(pk=10, estado_registro_id=estado_registro_id)
    )


@contextmanager
def _modelos():
    with (
        patch('app_sgbh.services.formulario_2a_archivo.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a_archivo.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch('app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo') as archivo,
        patch(
            'app_sgbh.services.formulario_2a_archivo.uuid.uuid4',
            return_value=_FIXED_UUID,
        ),
    ):
        formulario.DoesNotExist = _DoesNotExist
        planilla.objects.filter.return_value.exists.return_value = False
        archivo.return_value.pk = 9
        yield formulario, planilla, archivo


def _post(data, formulario_2a_id=10):
    factory = APIRequestFactory()
    request = factory.post(
        f'/api/sgbh/formularios-2a/{formulario_2a_id}/archivos/',
        data,
        format='multipart',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    return request


def test_create_writes_the_file_and_saves_the_row(tmp_path):
    uploaded = _upload()
    uploaded.name = r'C:\temp\ficha.PDF'

    with _storage(tmp_path), _modelos() as (formulario, _planilla, archivo):
        _formulario_existente(formulario)
        stored = archivo.objects.get.return_value

        result = Formulario2AArchivoService.create(
            formulario_2a_id=10,
            archivo=uploaded,
            c_usuari_login=' mmedina ',
        )

    assert result is stored
    archivo.assert_called_once_with(
        formulario_2a_id=10,
        nombre_original='ficha.PDF',
        nombre_archivo=_FIXED_NAME,
        ruta_archivo=f'formularios-2a/10/{_FIXED_NAME}',
        extension='pdf',
        tamano_bytes=len(b'%PDF-1.4'),
        c_usuari_login='mmedina',
    )
    archivo.return_value.save.assert_called_once_with()
    written = tmp_path / 'formularios-2a' / '10' / _FIXED_NAME
    assert written.read_bytes() == b'%PDF-1.4'


def test_create_removes_the_file_when_the_insert_fails(tmp_path):
    with _storage(tmp_path), _modelos() as (formulario, _planilla, archivo):
        _formulario_existente(formulario)
        archivo.return_value.save.side_effect = RuntimeError('db')

        with pytest.raises(RuntimeError, match='db'):
            Formulario2AArchivoService.create(
                formulario_2a_id=10,
                archivo=_upload(),
                c_usuari_login='mmedina',
            )

    written = tmp_path / 'formularios-2a' / '10' / _FIXED_NAME
    assert not written.exists()


@pytest.mark.parametrize('login', ['', '   ', 'a' * 21])
def test_create_rejects_an_unidentified_user(tmp_path, login):
    with _storage(tmp_path):
        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.create(
                formulario_2a_id=10,
                archivo=_upload(),
                c_usuari_login=login,
            )

    assert exc.value.message == 'No se pudo identificar al usuario'
    assert list(tmp_path.rglob('*')) == []


def test_create_rejects_unknown_formulario(tmp_path):
    with _storage(tmp_path), _modelos() as (formulario, _planilla, archivo):
        formulario.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.create(
                formulario_2a_id=10,
                archivo=_upload(),
                c_usuari_login='mmedina',
            )

    assert exc.value.not_found is True
    assert exc.value.message == 'El formulario EDAN 2A indicado no existe'
    archivo.assert_not_called()
    assert list(tmp_path.rglob('*')) == []


def test_create_rejects_inactive_formulario(tmp_path):
    with _storage(tmp_path), _modelos() as (formulario, _planilla, archivo):
        _formulario_existente(formulario, estado_registro_id=2)

        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.create(
                formulario_2a_id=10,
                archivo=_upload(),
                c_usuari_login='mmedina',
            )

    assert exc.value.conflict is True
    assert 'inactivo' in exc.value.message
    archivo.assert_not_called()


def test_create_rejects_formulario_with_issued_planilla(tmp_path):
    with _storage(tmp_path), _modelos() as (formulario, planilla, archivo):
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.create(
                formulario_2a_id=10,
                archivo=_upload(),
                c_usuari_login='mmedina',
            )

    assert exc.value.conflict is True
    assert 'planilla BAH' in exc.value.message
    archivo.assert_not_called()


@pytest.mark.parametrize(
    ('name', 'content', 'message'),
    [
        ('ficha.pdf', b'', 'El archivo está vacío'),
        ('ficha.exe', b'ABCD', 'El tipo de archivo no está permitido'),
        ('ficha', b'ABCD', 'El archivo debe tener una extensión'),
        ('.pdf', b'ABCD', 'El archivo no tiene un nombre válido'),
    ],
)
def test_create_rejects_invalid_uploads(tmp_path, name, content, message):
    uploaded = _upload(name=name, content=content)

    with _storage(tmp_path):
        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.create(
                formulario_2a_id=10,
                archivo=uploaded,
                c_usuari_login='mmedina',
            )

    assert message in exc.value.message
    assert list(tmp_path.rglob('*')) == []


def test_create_rejects_a_name_longer_than_the_column(tmp_path):
    uploaded = _upload(content=b'ABCD')
    uploaded._name = 'a' * 252 + '.pdf'

    with _storage(tmp_path):
        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.create(
                formulario_2a_id=10,
                archivo=uploaded,
                c_usuari_login='mmedina',
            )

    assert 'no puede superar 255 caracteres' in exc.value.message
    assert list(tmp_path.rglob('*')) == []


def test_create_rejects_a_file_over_the_configured_limit(tmp_path):
    uploaded = _upload(content=b'a' * 1025)

    with _storage(tmp_path):
        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.create(
                formulario_2a_id=10,
                archivo=uploaded,
                c_usuari_login='mmedina',
            )

    assert exc.value.message == 'El archivo supera el tamaño máximo permitido'


def test_create_rejects_a_value_that_is_not_a_file(tmp_path):
    with _storage(tmp_path):
        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.create(
                formulario_2a_id=10,
                archivo='ficha.pdf',
                c_usuari_login='mmedina',
            )

    assert exc.value.message == 'El archivo es obligatorio'


def test_archivo_id_is_a_random_uuid_sent_with_hyphens():
    field = Formulario2AArchivo._meta.get_field('archivo_id')
    connection = SimpleNamespace(
        features=SimpleNamespace(has_native_uuid_field=False),
    )

    value = field.get_default()
    prepared = field.get_db_prep_value(_ARCHIVO_ID, connection)

    assert field.primary_key is True
    assert field.db_type(connection) == 'uniqueidentifier'
    assert isinstance(value, UUID)
    assert value.version == 4
    assert prepared == str(_ARCHIVO_ID)


def test_serializer_omits_the_internal_path():
    row = SimpleNamespace(
        archivo_id=_ARCHIVO_ID,
        formulario_2a_id=10,
        nombre_original='ficha.PDF',
        nombre_archivo=_FIXED_NAME,
        ruta_archivo=f'formularios-2a/10/{_FIXED_NAME}',
        extension='pdf',
        tamano_bytes=8,
        esta_activo=True,
        fecha_registro=timezone.now(),
        c_usuari_login='mmedina',
    )

    data = Formulario2AArchivoSerializer(row).data

    assert 'ruta_archivo' not in data
    assert data['nombre_original'] == 'ficha.PDF'
    assert data['c_usuari_login'] == 'mmedina'


def test_post_archivos_returns_the_created_row():
    stored = SimpleNamespace(
        archivo_id=_ARCHIVO_ID,
        formulario_2a_id=10,
        nombre_original='ficha.pdf',
        nombre_archivo=_FIXED_NAME,
        ruta_archivo=f'formularios-2a/10/{_FIXED_NAME}',
        extension='pdf',
        tamano_bytes=8,
        esta_activo=True,
        fecha_registro=timezone.now(),
        c_usuari_login='mmedina',
    )
    request = _post({'archivo': _upload()})

    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.create',
        return_value=stored,
    ) as create:
        response = Formulario2AArchivoCreateView.as_view()(
            request,
            formulario_2a_id=10,
        )

    assert response.status_code == 201
    assert response.data['archivo_id'] == str(_ARCHIVO_ID)
    assert response.data['formulario_2a_id'] == 10
    assert response.data['extension'] == 'pdf'
    assert response.data['c_usuari_login'] == 'mmedina'
    assert create.call_args.kwargs['c_usuari_login'] == 'mmedina'
    assert 'ruta_archivo' not in response.data
    assert create.call_args.kwargs['formulario_2a_id'] == 10
    assert create.call_args.kwargs['archivo'].name == 'ficha.pdf'


def test_post_archivos_requires_a_file():
    request = _post({})

    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.create',
    ) as create:
        response = Formulario2AArchivoCreateView.as_view()(
            request,
            formulario_2a_id=10,
        )

    assert response.status_code == 400
    assert response.data['error'] == 'El archivo es obligatorio'
    create.assert_not_called()


def test_post_archivos_rejects_two_files():
    boundary = '----ArchivoBoundary'
    body = (
        f'--{boundary}\r\n'
        'Content-Disposition: form-data; name="archivo"; filename="uno.pdf"\r\n'
        'Content-Type: application/pdf\r\n\r\n'
    ).encode() + b'%PDF-1\r\n' + (
        f'--{boundary}\r\n'
        'Content-Disposition: form-data; name="archivo"; filename="dos.pdf"\r\n'
        'Content-Type: application/pdf\r\n\r\n'
    ).encode() + f'\r\n--{boundary}--\r\n'.encode()
    factory = APIRequestFactory()
    request = factory.post(
        '/api/sgbh/formularios-2a/10/archivos/',
        data=body,
        content_type=f'multipart/form-data; boundary={boundary}',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.create',
    ) as create:
        response = Formulario2AArchivoCreateView.as_view()(
            request,
            formulario_2a_id=10,
        )

    assert response.status_code == 400
    assert response.data['error'] == 'Solo se puede subir un archivo por solicitud'
    create.assert_not_called()


def test_post_archivos_rejects_c_usuari_login_from_the_client():
    request = _post({'archivo': _upload(), 'c_usuari_login': '4'})

    response = Formulario2AArchivoCreateView.as_view()(request, formulario_2a_id=10)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo c_usuari_login lo asigna el sistema'


@pytest.mark.parametrize('formulario_2a_id', [0, 2147483648])
def test_post_archivos_rejects_an_invalid_id(formulario_2a_id):
    request = _post({'archivo': _upload()})

    response = Formulario2AArchivoCreateView.as_view()(
        request,
        formulario_2a_id=formulario_2a_id,
    )

    assert response.status_code == 400
    assert response.data['error'] == (
        'El campo formulario_2a_id debe ser un número entero'
    )


def test_post_archivos_returns_not_found_when_the_formulario_is_missing():
    request = _post({'archivo': _upload()})

    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.create',
        side_effect=Formulario2AArchivoServiceError(
            'El formulario EDAN 2A indicado no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AArchivoCreateView.as_view()(
            request,
            formulario_2a_id=10,
        )

    assert response.status_code == 404
    assert response.data['error'] == 'El formulario EDAN 2A indicado no existe'


def test_post_archivos_returns_conflict_when_the_formulario_is_locked():
    request = _post({'archivo': _upload()})
    message = (
        'No se puede modificar el formulario EDAN 2A porque tiene '
        'una planilla BAH emitida y activa'
    )

    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.create',
        side_effect=Formulario2AArchivoServiceError(message, conflict=True),
    ):
        response = Formulario2AArchivoCreateView.as_view()(
            request,
            formulario_2a_id=10,
        )

    assert response.status_code == 409
    assert response.data['error'] == message


def test_post_archivos_hides_internal_errors():
    request = _post({'archivo': _upload()})

    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.create',
        side_effect=RuntimeError(r'C:\secret\ficha.pdf'),
    ):
        response = Formulario2AArchivoCreateView.as_view()(
            request,
            formulario_2a_id=10,
        )

    assert response.status_code == 500
    assert response.data['error'] == (
        'No se pudo registrar el archivo del formulario EDAN 2A'
    )
