from unittest.mock import MagicMock, patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.formulario_2a_archivo import (
    Formulario2AArchivoService,
    Formulario2AArchivoServiceError,
)
from app_sgbh.views.formulario_2a_archivo_view import Formulario2AArchivoDetailView


class _DoesNotExist(Exception):
    pass


def _delete_request():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/formularios-2a/10/archivos/9/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    return request


def test_delete_marks_the_row_inactive_and_keeps_the_file():
    row = MagicMock(esta_activo=True)

    with (
        patch('app_sgbh.services.formulario_2a_archivo.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo'
        ) as archivo,
        patch('app_sgbh.services.formulario_2a_archivo._delete_file') as remove_file,
    ):
        archivo.objects.select_for_update.return_value.get.return_value = row

        Formulario2AArchivoService.delete(10, 9)

    archivo.objects.select_for_update.return_value.get.assert_called_once_with(
        pk=9,
        formulario_2a_id=10,
    )
    assert row.esta_activo is False
    row.save.assert_called_once_with(update_fields=['esta_activo'])
    remove_file.assert_not_called()


def test_delete_rejects_a_missing_file():
    with (
        patch('app_sgbh.services.formulario_2a_archivo.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo'
        ) as archivo,
    ):
        archivo.DoesNotExist = _DoesNotExist
        archivo.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.delete(10, 9)

    assert exc.value.not_found is True
    assert exc.value.message == 'El archivo indicado no existe'


def test_delete_rejects_a_file_that_is_already_inactive():
    row = MagicMock(esta_activo=False)

    with (
        patch('app_sgbh.services.formulario_2a_archivo.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_archivo.Formulario2AArchivo'
        ) as archivo,
        patch('app_sgbh.services.formulario_2a_archivo._delete_file') as remove_file,
    ):
        archivo.objects.select_for_update.return_value.get.return_value = row

        with pytest.raises(Formulario2AArchivoServiceError) as exc:
            Formulario2AArchivoService.delete(10, 9)

    assert exc.value.conflict is True
    assert exc.value.message == 'El archivo indicado ya está inactivo'
    row.save.assert_not_called()
    remove_file.assert_not_called()


def test_delete_archivos_returns_no_content():
    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.delete',
    ) as delete:
        response = Formulario2AArchivoDetailView.as_view()(
            _delete_request(),
            formulario_2a_id=10,
            archivo_id=9,
        )

    assert response.status_code == 204
    delete.assert_called_once_with(10, 9)


def test_delete_archivos_returns_not_found():
    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.delete',
        side_effect=Formulario2AArchivoServiceError(
            'El archivo indicado no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AArchivoDetailView.as_view()(
            _delete_request(),
            formulario_2a_id=10,
            archivo_id=9,
        )

    assert response.status_code == 404
    assert response.data['error'] == 'El archivo indicado no existe'


def test_delete_archivos_returns_conflict_when_the_file_is_inactive():
    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.delete',
        side_effect=Formulario2AArchivoServiceError(
            'El archivo indicado ya está inactivo',
            conflict=True,
        ),
    ):
        response = Formulario2AArchivoDetailView.as_view()(
            _delete_request(),
            formulario_2a_id=10,
            archivo_id=9,
        )

    assert response.status_code == 409
    assert response.data['error'] == 'El archivo indicado ya está inactivo'


@pytest.mark.parametrize(
    ('formulario_2a_id', 'archivo_id', 'message'),
    [
        (0, 9, 'formulario_2a_id debe ser un número entero'),
        (10, 0, 'archivo_id debe ser un número entero'),
        (2147483648, 9, 'formulario_2a_id debe ser un número entero'),
        (10, 9223372036854775808, 'archivo_id debe ser un número entero'),
    ],
)
def test_delete_archivos_rejects_an_invalid_id(formulario_2a_id, archivo_id, message):
    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.delete',
    ) as delete:
        response = Formulario2AArchivoDetailView.as_view()(
            _delete_request(),
            formulario_2a_id=formulario_2a_id,
            archivo_id=archivo_id,
        )

    assert response.status_code == 400
    assert message in response.data['error']
    delete.assert_not_called()


def test_delete_archivos_hides_internal_errors():
    with patch(
        'app_sgbh.views.formulario_2a_archivo_view.Formulario2AArchivoService.delete',
        side_effect=RuntimeError(r'C:\secret\ficha.pdf'),
    ):
        response = Formulario2AArchivoDetailView.as_view()(
            _delete_request(),
            formulario_2a_id=10,
            archivo_id=9,
        )

    assert response.status_code == 500
    assert response.data['error'] == (
        'No se pudo eliminar el archivo del formulario EDAN 2A'
    )
