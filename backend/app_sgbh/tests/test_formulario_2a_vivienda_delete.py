from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.db.models import ProtectedError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.formulario_2a_vivienda import (
    Formulario2AViviendaService,
    Formulario2AViviendaServiceError,
)
from app_sgbh.views.formulario_2a_vivienda_view import Formulario2AViviendaDetailView


class _DoesNotExist(Exception):
    pass


def _formulario_existente(formulario, estado_registro_id=1):
    formulario.objects.select_for_update.return_value.get.return_value = (
        SimpleNamespace(pk=10, estado_registro_id=estado_registro_id)
    )


def _patch_delete():
    return (
        patch('app_sgbh.services.formulario_2a_vivienda.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a_vivienda.Formulario2A'),
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega'),
        patch('app_sgbh.services.formulario_2a_vivienda.Formulario2AIntegrante'),
        patch('app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'),
    )


def test_delete_rejects_missing_vivienda():
    patches = _patch_delete()
    with patches[0], patches[1] as formulario, patches[2], patches[3], patches[4] as vivienda:
        vivienda.DoesNotExist = _DoesNotExist
        vivienda.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.delete(21)

    assert exc.value.not_found is True
    assert exc.value.message == 'La vivienda indicada no existe'
    formulario.objects.select_for_update.assert_not_called()


def test_delete_rejects_inactive_formulario():
    row = SimpleNamespace(pk=21, formulario_2a_id=10)
    patches = _patch_delete()
    with (
        patches[0],
        patches[1] as formulario,
        patches[2] as planilla,
        patches[3] as integrante,
        patches[4] as vivienda,
    ):
        vivienda.objects.select_for_update.return_value.get.return_value = row
        _formulario_existente(formulario, estado_registro_id=2)

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.delete(21)

    assert exc.value.conflict is True
    assert 'estado de registro es inactivo' in exc.value.message
    planilla.objects.filter.assert_not_called()
    integrante.objects.filter.assert_not_called()


def test_delete_rejects_planilla_emitida():
    row = SimpleNamespace(pk=21, formulario_2a_id=10)
    patches = _patch_delete()
    with (
        patches[0],
        patches[1] as formulario,
        patches[2] as planilla,
        patches[3] as integrante,
        patches[4] as vivienda,
    ):
        vivienda.objects.select_for_update.return_value.get.return_value = row
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.delete(21)

    assert exc.value.conflict is True
    assert 'planilla BAH emitida y activa' in exc.value.message
    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=10,
        estado_planilla__codigo='EMITIDA',
    )
    integrante.objects.filter.assert_not_called()


def test_delete_rejects_vivienda_with_integrante():
    row = SimpleNamespace(pk=21, formulario_2a_id=10, delete=lambda: None)
    patches = _patch_delete()
    with (
        patches[0],
        patches[1] as formulario,
        patches[2] as planilla,
        patches[3] as integrante,
        patches[4] as vivienda,
    ):
        vivienda.objects.select_for_update.return_value.get.return_value = row
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        integrante.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.delete(21)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar la vivienda. Primero debe eliminar los integrantes de la vivienda'
    )
    integrante.objects.filter.assert_called_once_with(familia__vivienda_id=21)


def test_delete_removes_vivienda_without_integrantes():
    row = SimpleNamespace(pk=21, formulario_2a_id=10)
    row.delete = lambda: setattr(row, 'deleted', True)
    patches = _patch_delete()
    with (
        patches[0],
        patches[1] as formulario,
        patches[2] as planilla,
        patches[3] as integrante,
        patches[4] as vivienda,
    ):
        vivienda.objects.select_for_update.return_value.get.return_value = row
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        integrante.objects.filter.return_value.exists.return_value = False

        Formulario2AViviendaService.delete(21)

    assert row.deleted is True
    integrante.objects.filter.assert_called_once_with(familia__vivienda_id=21)


def test_delete_rejects_when_database_protects_related_rows():
    row = SimpleNamespace(pk=21, formulario_2a_id=10)
    row.delete = lambda: (_ for _ in ()).throw(ProtectedError('protected', {object()}))
    patches = _patch_delete()
    with (
        patches[0],
        patches[1] as formulario,
        patches[2] as planilla,
        patches[3] as integrante,
        patches[4] as vivienda,
    ):
        vivienda.objects.select_for_update.return_value.get.return_value = row
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        integrante.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.delete(21)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar la vivienda porque tiene registros asociados'
    )


def test_delete_viviendas_returns_conflict_when_integrante_exists():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/viviendas/21/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.delete',
        side_effect=Formulario2AViviendaServiceError(
            'No se puede eliminar la vivienda. Primero debe eliminar los integrantes de la vivienda',
            conflict=True,
        ),
    ):
        response = Formulario2AViviendaDetailView.as_view()(request, vivienda_id=21)

    assert response.status_code == 409
    assert response.data['error'] == (
        'No se puede eliminar la vivienda. Primero debe eliminar los integrantes de la vivienda'
    )


def test_delete_viviendas_returns_no_content():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/viviendas/21/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.delete',
    ) as delete:
        response = Formulario2AViviendaDetailView.as_view()(request, vivienda_id=21)

    assert response.status_code == 204
    delete.assert_called_once_with(21)


def test_delete_viviendas_returns_not_found():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/viviendas/21/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.delete',
        side_effect=Formulario2AViviendaServiceError(
            'La vivienda indicada no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AViviendaDetailView.as_view()(request, vivienda_id=21)

    assert response.status_code == 404
    assert response.data['error'] == 'La vivienda indicada no existe'


def test_delete_viviendas_rejects_invalid_id():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/viviendas/0/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.delete',
    ) as delete:
        response = Formulario2AViviendaDetailView.as_view()(request, vivienda_id=0)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo vivienda_id debe ser un número entero'
    delete.assert_not_called()
