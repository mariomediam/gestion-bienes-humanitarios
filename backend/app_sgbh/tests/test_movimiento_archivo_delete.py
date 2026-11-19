from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from django.urls import Resolver404, resolve
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.movimiento_archivo import (
    MovimientoArchivoService,
    MovimientoArchivoServiceError,
)
from app_sgbh.views.movimiento_archivo_view import MovimientoArchivoDetailView


_ARCHIVO_ID = UUID('11111111-2222-4333-8444-555555555555')


class _DoesNotExist(Exception):
    pass


def _delete_request():
    factory = APIRequestFactory()
    request = factory.delete(f'/api/sgbh/movimientos/10/archivos/{_ARCHIVO_ID}/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    return request


def test_delete_marks_the_row_inactive_and_keeps_the_file():
    row = MagicMock(esta_activo=True)

    with (
        patch('app_sgbh.services.movimiento_archivo.transaction.atomic'),
        patch(
            'app_sgbh.services.movimiento_archivo.MovimientoArchivo'
        ) as archivo,
        patch('app_sgbh.services.movimiento_archivo._delete_file') as remove_file,
    ):
        archivo.objects.select_for_update.return_value.get.return_value = row

        MovimientoArchivoService.delete(10, _ARCHIVO_ID)

    archivo.objects.select_for_update.return_value.get.assert_called_once_with(
        pk=_ARCHIVO_ID,
        movimiento_id=10,
    )
    assert row.esta_activo is False
    row.save.assert_called_once_with(update_fields=['esta_activo'])
    remove_file.assert_not_called()


def test_delete_rejects_a_missing_file():
    with (
        patch('app_sgbh.services.movimiento_archivo.transaction.atomic'),
        patch(
            'app_sgbh.services.movimiento_archivo.MovimientoArchivo'
        ) as archivo,
    ):
        archivo.DoesNotExist = _DoesNotExist
        archivo.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(MovimientoArchivoServiceError) as exc:
            MovimientoArchivoService.delete(10, _ARCHIVO_ID)

    assert exc.value.not_found is True
    assert exc.value.message == 'El archivo indicado no existe'


def test_delete_rejects_a_file_that_is_already_inactive():
    row = MagicMock(esta_activo=False)

    with (
        patch('app_sgbh.services.movimiento_archivo.transaction.atomic'),
        patch(
            'app_sgbh.services.movimiento_archivo.MovimientoArchivo'
        ) as archivo,
        patch('app_sgbh.services.movimiento_archivo._delete_file') as remove_file,
    ):
        archivo.objects.select_for_update.return_value.get.return_value = row

        with pytest.raises(MovimientoArchivoServiceError) as exc:
            MovimientoArchivoService.delete(10, _ARCHIVO_ID)

    assert exc.value.conflict is True
    assert exc.value.message == 'El archivo indicado ya está inactivo'
    row.save.assert_not_called()
    remove_file.assert_not_called()


def test_delete_url_accepts_a_uuid_in_either_case():
    lower = resolve(
        f'/api/sgbh/movimientos/10/archivos/{_ARCHIVO_ID}/'
    )
    upper = resolve(
        '/api/sgbh/movimientos/10/archivos/A9E4342E-1F84-4A65-8A4D-86C8C13BA8EC/'
    )

    assert lower.kwargs['archivo_id'] == _ARCHIVO_ID
    assert upper.kwargs['archivo_id'] == UUID(
        'A9E4342E-1F84-4A65-8A4D-86C8C13BA8EC'
    )


def test_delete_url_rejects_an_integer_id():
    with pytest.raises(Resolver404):
        resolve('/api/sgbh/movimientos/10/archivos/9/')


def test_delete_archivos_returns_no_content():
    with patch(
        'app_sgbh.views.movimiento_archivo_view.MovimientoArchivoService.delete',
    ) as delete:
        response = MovimientoArchivoDetailView.as_view()(
            _delete_request(),
            movimiento_id=10,
            archivo_id=_ARCHIVO_ID,
        )

    assert response.status_code == 204
    delete.assert_called_once_with(10, _ARCHIVO_ID)


def test_delete_archivos_returns_not_found():
    with patch(
        'app_sgbh.views.movimiento_archivo_view.MovimientoArchivoService.delete',
        side_effect=MovimientoArchivoServiceError(
            'El archivo indicado no existe',
            not_found=True,
        ),
    ):
        response = MovimientoArchivoDetailView.as_view()(
            _delete_request(),
            movimiento_id=10,
            archivo_id=_ARCHIVO_ID,
        )

    assert response.status_code == 404
    assert response.data['error'] == 'El archivo indicado no existe'


def test_delete_archivos_returns_conflict_when_the_file_is_inactive():
    with patch(
        'app_sgbh.views.movimiento_archivo_view.MovimientoArchivoService.delete',
        side_effect=MovimientoArchivoServiceError(
            'El archivo indicado ya está inactivo',
            conflict=True,
        ),
    ):
        response = MovimientoArchivoDetailView.as_view()(
            _delete_request(),
            movimiento_id=10,
            archivo_id=_ARCHIVO_ID,
        )

    assert response.status_code == 409
    assert response.data['error'] == 'El archivo indicado ya está inactivo'


@pytest.mark.parametrize(
    ('movimiento_id', 'archivo_id', 'message'),
    [
        (0, _ARCHIVO_ID, 'movimiento_id debe ser un número entero'),
        (10, 0, 'archivo_id debe ser un UUID'),
        (10, 'no-es-uuid', 'archivo_id debe ser un UUID'),
        (2147483648, _ARCHIVO_ID, 'movimiento_id debe ser un número entero'),
    ],
)
def test_delete_archivos_rejects_an_invalid_id(movimiento_id, archivo_id, message):
    with patch(
        'app_sgbh.views.movimiento_archivo_view.MovimientoArchivoService.delete',
    ) as delete:
        response = MovimientoArchivoDetailView.as_view()(
            _delete_request(),
            movimiento_id=movimiento_id,
            archivo_id=archivo_id,
        )

    assert response.status_code == 400
    assert message in response.data['error']
    delete.assert_not_called()


def test_delete_archivos_hides_internal_errors():
    with patch(
        'app_sgbh.views.movimiento_archivo_view.MovimientoArchivoService.delete',
        side_effect=RuntimeError(r'C:\secret\guia.pdf'),
    ):
        response = MovimientoArchivoDetailView.as_view()(
            _delete_request(),
            movimiento_id=10,
            archivo_id=_ARCHIVO_ID,
        )

    assert response.status_code == 500
    assert response.data['error'] == (
        'No se pudo eliminar el archivo del movimiento de almacén'
    )
