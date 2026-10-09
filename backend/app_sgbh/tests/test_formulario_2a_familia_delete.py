from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.db.models import ProtectedError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.formulario_2a_familia import (
    Formulario2AFamiliaService,
    Formulario2AFamiliaServiceError,
)
from app_sgbh.views.formulario_2a_familia_view import Formulario2AFamiliaDetailView


class _DoesNotExist(Exception):
    pass


def _vivienda_existente(vivienda, formulario_2a_id=10):
    vivienda.objects.select_for_update.return_value.get.return_value = (
        SimpleNamespace(pk=8, formulario_2a_id=formulario_2a_id)
    )


def _formulario_existente(formulario, estado_registro_id=1):
    formulario.objects.select_for_update.return_value.get.return_value = (
        SimpleNamespace(pk=10, estado_registro_id=estado_registro_id)
    )


def _patch_delete():
    return (
        patch('app_sgbh.services.formulario_2a_familia.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a_familia.Formulario2AFamilia'),
        patch('app_sgbh.services.formulario_2a_familia.Formulario2AVivienda'),
        patch('app_sgbh.services.formulario_2a_familia.Formulario2A'),
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega'),
        patch('app_sgbh.services.formulario_2a_familia.Formulario2AIntegrante'),
    )


def test_delete_rejects_missing_familia():
    patches = _patch_delete()
    with (
        patches[0],
        patches[1] as familia,
        patches[2] as vivienda,
        patches[3],
        patches[4],
        patches[5],
    ):
        familia.DoesNotExist = _DoesNotExist
        familia.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AFamiliaServiceError) as exc:
            Formulario2AFamiliaService.delete(33)

    assert exc.value.not_found is True
    assert exc.value.message == 'La familia indicada no existe'
    vivienda.objects.select_for_update.assert_not_called()


def test_delete_rejects_inactive_formulario():
    row = SimpleNamespace(pk=33, vivienda_id=8)
    patches = _patch_delete()
    with (
        patches[0],
        patches[1] as familia,
        patches[2] as vivienda,
        patches[3] as formulario,
        patches[4] as planilla,
        patches[5] as integrante,
    ):
        familia.objects.select_for_update.return_value.get.return_value = row
        _vivienda_existente(vivienda)
        _formulario_existente(formulario, estado_registro_id=2)

        with pytest.raises(Formulario2AFamiliaServiceError) as exc:
            Formulario2AFamiliaService.delete(33)

    assert exc.value.conflict is True
    assert 'estado de registro es inactivo' in exc.value.message
    planilla.objects.filter.assert_not_called()
    integrante.objects.filter.assert_not_called()


def test_delete_rejects_planilla_emitida():
    row = SimpleNamespace(pk=33, vivienda_id=8)
    patches = _patch_delete()
    with (
        patches[0],
        patches[1] as familia,
        patches[2] as vivienda,
        patches[3] as formulario,
        patches[4] as planilla,
        patches[5] as integrante,
    ):
        familia.objects.select_for_update.return_value.get.return_value = row
        _vivienda_existente(vivienda)
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AFamiliaServiceError) as exc:
            Formulario2AFamiliaService.delete(33)

    assert exc.value.conflict is True
    assert 'planilla BAH emitida y activa' in exc.value.message
    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=10,
        estado_planilla__codigo='EMITIDA',
    )
    integrante.objects.filter.assert_not_called()


def test_delete_rejects_familia_with_integrante():
    row = SimpleNamespace(pk=33, vivienda_id=8, delete=lambda: None)
    patches = _patch_delete()
    with (
        patches[0],
        patches[1] as familia,
        patches[2] as vivienda,
        patches[3] as formulario,
        patches[4] as planilla,
        patches[5] as integrante,
    ):
        familia.objects.select_for_update.return_value.get.return_value = row
        _vivienda_existente(vivienda)
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        integrante.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AFamiliaServiceError) as exc:
            Formulario2AFamiliaService.delete(33)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar la familia. Primero debe eliminar los integrantes de la familia'
    )
    integrante.objects.filter.assert_called_once_with(familia_id=33)


def test_delete_removes_familia_without_integrantes():
    row = SimpleNamespace(pk=33, vivienda_id=8)
    row.delete = lambda: setattr(row, 'deleted', True)
    patches = _patch_delete()
    with (
        patches[0],
        patches[1] as familia,
        patches[2] as vivienda,
        patches[3] as formulario,
        patches[4] as planilla,
        patches[5] as integrante,
    ):
        familia.objects.select_for_update.return_value.get.return_value = row
        _vivienda_existente(vivienda)
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        integrante.objects.filter.return_value.exists.return_value = False

        Formulario2AFamiliaService.delete(33)

    assert row.deleted is True
    integrante.objects.filter.assert_called_once_with(familia_id=33)


def test_delete_rejects_when_database_protects_related_rows():
    row = SimpleNamespace(pk=33, vivienda_id=8)
    row.delete = lambda: (_ for _ in ()).throw(ProtectedError('protected', {object()}))
    patches = _patch_delete()
    with (
        patches[0],
        patches[1] as familia,
        patches[2] as vivienda,
        patches[3] as formulario,
        patches[4] as planilla,
        patches[5] as integrante,
    ):
        familia.objects.select_for_update.return_value.get.return_value = row
        _vivienda_existente(vivienda)
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        integrante.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AFamiliaServiceError) as exc:
            Formulario2AFamiliaService.delete(33)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar la familia porque tiene registros asociados'
    )


def test_delete_familias_returns_conflict_when_integrante_exists():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/familias/33/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_familia_view.Formulario2AFamiliaService.delete',
        side_effect=Formulario2AFamiliaServiceError(
            'No se puede eliminar la familia. Primero debe eliminar los integrantes de la familia',
            conflict=True,
        ),
    ):
        response = Formulario2AFamiliaDetailView.as_view()(request, familia_id=33)

    assert response.status_code == 409
    assert response.data['error'] == (
        'No se puede eliminar la familia. Primero debe eliminar los integrantes de la familia'
    )


def test_delete_familias_returns_no_content():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/familias/33/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_familia_view.Formulario2AFamiliaService.delete',
    ) as delete:
        response = Formulario2AFamiliaDetailView.as_view()(request, familia_id=33)

    assert response.status_code == 204
    delete.assert_called_once_with(33)


def test_delete_familias_returns_not_found():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/familias/33/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_familia_view.Formulario2AFamiliaService.delete',
        side_effect=Formulario2AFamiliaServiceError(
            'La familia indicada no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AFamiliaDetailView.as_view()(request, familia_id=33)

    assert response.status_code == 404
    assert response.data['error'] == 'La familia indicada no existe'


def test_delete_familias_rejects_invalid_id():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/familias/0/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_familia_view.Formulario2AFamiliaService.delete',
    ) as delete:
        response = Formulario2AFamiliaDetailView.as_view()(request, familia_id=0)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo familia_id debe ser un número entero'
    delete.assert_not_called()
