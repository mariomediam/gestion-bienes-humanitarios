from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.db.models import ProtectedError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.formulario_2a import (
    Formulario2AService,
    Formulario2AServiceError,
)
from app_sgbh.views.formulario_2a_view import Formulario2ADetailView


class _DoesNotExist(Exception):
    pass


def _patch_delete():
    return (
        patch('app_sgbh.services.formulario_2a.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a.Formulario2A'),
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega'),
        patch('app_sgbh.services.formulario_2a.Formulario2AVivienda'),
    )


def test_delete_rejects_missing_formulario():
    patches = _patch_delete()
    with patches[0], patches[1] as formulario, patches[2] as planilla, patches[3] as vivienda:
        formulario.DoesNotExist = _DoesNotExist
        formulario.objects.get.side_effect = _DoesNotExist

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.delete(15)

    assert exc.value.not_found is True
    assert exc.value.message == 'El formulario EDAN 2A indicado no existe'
    planilla.objects.filter.assert_not_called()
    vivienda.objects.filter.assert_not_called()


def test_delete_rejects_inactive_estado_registro():
    patches = _patch_delete()
    with patches[0], patches[1] as formulario, patches[2] as planilla, patches[3] as vivienda:
        row = SimpleNamespace(pk=15, estado_registro_id=2)
        formulario.DoesNotExist = _DoesNotExist
        formulario.objects.get.return_value = row

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.delete(15)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede modificar el formulario EDAN 2A porque su estado de registro es inactivo'
    )
    planilla.objects.filter.assert_not_called()
    vivienda.objects.filter.assert_not_called()


def test_delete_rejects_planilla_emitida_activa():
    patches = _patch_delete()
    with patches[0], patches[1] as formulario, patches[2] as planilla, patches[3] as vivienda:
        row = SimpleNamespace(pk=15, estado_registro_id=1)
        formulario.DoesNotExist = _DoesNotExist
        formulario.objects.get.return_value = row
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.delete(15)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede modificar el formulario EDAN 2A porque tiene una planilla BAH emitida y activa'
    )
    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=15,
        estado_planilla__codigo='EMITIDA',
    )
    vivienda.objects.filter.assert_not_called()


def test_delete_rejects_formulario_with_viviendas():
    patches = _patch_delete()
    with patches[0], patches[1] as formulario, patches[2] as planilla, patches[3] as vivienda:
        row = formulario.objects.get.return_value
        row.pk = 15
        row.estado_registro_id = 1
        formulario.DoesNotExist = _DoesNotExist
        planilla.objects.filter.return_value.exists.return_value = False
        vivienda.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.delete(15)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar el formulario EDAN 2A porque tiene viviendas asociadas'
    )
    vivienda.objects.filter.assert_called_once_with(formulario_2a_id=15)
    row.delete.assert_not_called()


def test_delete_removes_formulario_without_viviendas():
    patches = _patch_delete()
    with patches[0], patches[1] as formulario, patches[2] as planilla, patches[3] as vivienda:
        row = formulario.objects.get.return_value
        row.pk = 15
        row.estado_registro_id = 1
        formulario.DoesNotExist = _DoesNotExist
        planilla.objects.filter.return_value.exists.return_value = False
        vivienda.objects.filter.return_value.exists.return_value = False

        Formulario2AService.delete(15)

    vivienda.objects.filter.assert_called_once_with(formulario_2a_id=15)
    row.delete.assert_called_once_with()


def test_delete_rejects_when_database_protects_related_viviendas():
    patches = _patch_delete()
    with patches[0], patches[1] as formulario, patches[2] as planilla, patches[3] as vivienda:
        row = formulario.objects.get.return_value
        row.pk = 15
        row.estado_registro_id = 1
        formulario.DoesNotExist = _DoesNotExist
        planilla.objects.filter.return_value.exists.return_value = False
        vivienda.objects.filter.return_value.exists.return_value = False
        row.delete.side_effect = ProtectedError('protected', {object()})

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.delete(15)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar el formulario EDAN 2A porque tiene viviendas asociadas'
    )


def test_delete_formulario_2a_returns_conflict_when_viviendas_exist():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/formularios-2a/15/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_view.Formulario2AService.delete',
        side_effect=Formulario2AServiceError(
            'No se puede eliminar el formulario EDAN 2A porque tiene viviendas asociadas',
            conflict=True,
        ),
    ):
        response = Formulario2ADetailView.as_view()(request, formulario_2a_id=15)

    assert response.status_code == 409
    assert response.data['error'] == (
        'No se puede eliminar el formulario EDAN 2A porque tiene viviendas asociadas'
    )


def test_delete_formulario_2a_returns_no_content():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/formularios-2a/15/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_view.Formulario2AService.delete',
    ) as delete:
        response = Formulario2ADetailView.as_view()(request, formulario_2a_id=15)

    assert response.status_code == 204
    delete.assert_called_once_with(15)


def test_delete_formulario_2a_returns_not_found():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/formularios-2a/15/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_view.Formulario2AService.delete',
        side_effect=Formulario2AServiceError(
            'El formulario EDAN 2A indicado no existe',
            not_found=True,
        ),
    ):
        response = Formulario2ADetailView.as_view()(request, formulario_2a_id=15)

    assert response.status_code == 404
    assert response.data['error'] == 'El formulario EDAN 2A indicado no existe'


def test_delete_formulario_2a_rejects_invalid_id():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/formularios-2a/0/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_view.Formulario2AService.delete',
    ) as delete:
        response = Formulario2ADetailView.as_view()(request, formulario_2a_id=0)

    assert response.status_code == 400
    assert response.data['error'] == (
        'El campo formulario_2a_id debe ser un número entero'
    )
    delete.assert_not_called()


def test_delete_formulario_2a_returns_server_error():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/formularios-2a/15/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_view.Formulario2AService.delete',
        side_effect=RuntimeError('db'),
    ):
        response = Formulario2ADetailView.as_view()(request, formulario_2a_id=15)

    assert response.status_code == 500
    assert response.data['error'] == 'No se pudo eliminar el formulario EDAN 2A'
