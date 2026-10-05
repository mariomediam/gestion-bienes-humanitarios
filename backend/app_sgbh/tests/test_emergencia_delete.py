from unittest.mock import patch

import pytest
from django.db.models import ProtectedError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.emergencia import EmergenciaService, EmergenciaServiceError
from app_sgbh.views.emergencia_view import EmergenciaDetailView


class _DoesNotExist(Exception):
    pass


def _patch_delete():
    return (
        patch('app_sgbh.services.emergencia.transaction.atomic'),
        patch('app_sgbh.services.emergencia.Emergencia'),
        patch('app_sgbh.services.emergencia.Formulario2A'),
    )


def test_delete_rejects_emergency_referenced_by_formulario_2a():
    patches = _patch_delete()
    with patches[0], patches[1] as emergencia, patches[2] as formulario:
        row = emergencia.objects.get.return_value
        emergencia.DoesNotExist = _DoesNotExist
        formulario.objects.filter.return_value.exists.return_value = True

        with pytest.raises(EmergenciaServiceError) as exc:
            EmergenciaService.delete(9)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar la emergencia porque tiene formularios 2A asociados'
    )
    formulario.objects.filter.assert_called_once_with(emergencia_id=9)
    row.delete.assert_not_called()


def test_delete_removes_emergency_without_formulario_2a():
    patches = _patch_delete()
    with patches[0], patches[1] as emergencia, patches[2] as formulario:
        row = emergencia.objects.get.return_value
        emergencia.DoesNotExist = _DoesNotExist
        formulario.objects.filter.return_value.exists.return_value = False

        EmergenciaService.delete(9)

    row.delete.assert_called_once_with()


def test_delete_rejects_missing_emergency():
    patches = _patch_delete()
    with patches[0], patches[1] as emergencia, patches[2] as formulario:
        emergencia.DoesNotExist = _DoesNotExist
        emergencia.objects.get.side_effect = _DoesNotExist

        with pytest.raises(EmergenciaServiceError) as exc:
            EmergenciaService.delete(9)

    assert exc.value.not_found is True
    assert exc.value.message == 'La emergencia indicada no existe'
    formulario.objects.filter.assert_not_called()


def test_delete_rejects_when_database_protects_related_formulario_2a():
    patches = _patch_delete()
    with patches[0], patches[1] as emergencia, patches[2] as formulario:
        row = emergencia.objects.get.return_value
        emergencia.DoesNotExist = _DoesNotExist
        formulario.objects.filter.return_value.exists.return_value = False
        row.delete.side_effect = ProtectedError('protected', {object()})

        with pytest.raises(EmergenciaServiceError) as exc:
            EmergenciaService.delete(9)

    assert exc.value.conflict is True


def test_delete_emergencia_returns_conflict_when_formulario_2a_exists():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/emergencias/9/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.emergencia_view.EmergenciaService.delete',
        side_effect=EmergenciaServiceError(
            'No se puede eliminar la emergencia porque tiene formularios 2A asociados',
            conflict=True,
        ),
    ):
        response = EmergenciaDetailView.as_view()(request, emergencia_id=9)

    assert response.status_code == 409
    assert response.data['error'] == (
        'No se puede eliminar la emergencia porque tiene formularios 2A asociados'
    )


def test_delete_emergencia_returns_no_content():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/emergencias/9/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch('app_sgbh.views.emergencia_view.EmergenciaService.delete') as delete:
        response = EmergenciaDetailView.as_view()(request, emergencia_id=9)

    assert response.status_code == 204
    delete.assert_called_once_with(9)


def test_delete_emergencia_rejects_invalid_id():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/emergencias/0/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch('app_sgbh.views.emergencia_view.EmergenciaService.delete') as delete:
        response = EmergenciaDetailView.as_view()(request, emergencia_id=0)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo emergencia_id debe ser un número entero'
    delete.assert_not_called()
