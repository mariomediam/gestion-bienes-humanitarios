from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.db.models import ProtectedError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.formulario_2a_integrante import (
    Formulario2AIntegranteService,
    Formulario2AIntegranteServiceError,
)
from app_sgbh.views.formulario_2a_integrante_view import Formulario2AIntegranteDetailView


class _DoesNotExist(Exception):
    pass


def _padres_existentes(familia, vivienda, formulario, estado_registro_id=1):
    familia.objects.select_for_update.return_value.get.return_value = SimpleNamespace(
        pk=8,
        vivienda_id=4,
    )
    vivienda.objects.select_for_update.return_value.get.return_value = SimpleNamespace(
        pk=4,
        formulario_2a_id=10,
    )
    formulario.objects.select_for_update.return_value.get.return_value = (
        SimpleNamespace(pk=10, estado_registro_id=estado_registro_id)
    )


def test_delete_rejects_missing_integrante():
    with (
        patch('app_sgbh.services.formulario_2a_integrante.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
    ):
        integrante.DoesNotExist = _DoesNotExist
        integrante.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.delete(31)

    assert exc.value.not_found is True
    assert exc.value.message == 'El integrante indicado no existe'
    familia.objects.select_for_update.assert_not_called()


def test_delete_rejects_inactive_formulario():
    row = SimpleNamespace(pk=31, familia_id=8)
    with (
        patch('app_sgbh.services.formulario_2a_integrante.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_integrante.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla_formulario,
        patch('app_sgbh.services.formulario_2a_integrante.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
    ):
        integrante.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario, estado_registro_id=2)

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.delete(31)

    assert exc.value.conflict is True
    assert 'estado de registro es inactivo' in exc.value.message
    planilla_formulario.objects.filter.assert_not_called()
    planilla.objects.filter.assert_not_called()


def test_delete_rejects_planilla_emitida():
    row = SimpleNamespace(pk=31, familia_id=8)
    with (
        patch('app_sgbh.services.formulario_2a_integrante.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_integrante.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla_formulario,
        patch('app_sgbh.services.formulario_2a_integrante.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
    ):
        integrante.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario)
        planilla_formulario.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.delete(31)

    assert exc.value.conflict is True
    assert 'planilla BAH emitida y activa' in exc.value.message
    planilla_formulario.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=10,
        estado_planilla__codigo='EMITIDA',
    )
    planilla.objects.filter.assert_not_called()


def test_delete_rejects_integrante_with_planilla():
    row = SimpleNamespace(pk=31, familia_id=8, delete=lambda: None)
    with (
        patch('app_sgbh.services.formulario_2a_integrante.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_integrante.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla_formulario,
        patch('app_sgbh.services.formulario_2a_integrante.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
    ):
        integrante.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario)
        planilla_formulario.objects.filter.return_value.exists.return_value = False
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.delete(31)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar el integrante porque tiene planillas de entrega asociadas'
    )
    planilla.objects.filter.assert_called_once_with(integrante_receptor_id=31)


def test_delete_removes_integrante_without_planilla():
    row = SimpleNamespace(pk=31, familia_id=8)
    row.delete = lambda: setattr(row, 'deleted', True)
    with (
        patch('app_sgbh.services.formulario_2a_integrante.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_integrante.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla_formulario,
        patch('app_sgbh.services.formulario_2a_integrante.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
    ):
        integrante.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario)
        planilla_formulario.objects.filter.return_value.exists.return_value = False
        planilla.objects.filter.return_value.exists.return_value = False

        Formulario2AIntegranteService.delete(31)

    assert row.deleted is True
    planilla.objects.filter.assert_called_once_with(integrante_receptor_id=31)


def test_delete_rejects_when_database_protects_related_rows():
    row = SimpleNamespace(pk=31, familia_id=8)
    row.delete = lambda: (_ for _ in ()).throw(ProtectedError('protected', {object()}))
    with (
        patch('app_sgbh.services.formulario_2a_integrante.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_integrante.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla_formulario,
        patch('app_sgbh.services.formulario_2a_integrante.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
    ):
        integrante.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario)
        planilla_formulario.objects.filter.return_value.exists.return_value = False
        planilla.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.delete(31)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar el integrante porque tiene registros asociados'
    )


def test_delete_integrantes_returns_conflict_when_planilla_exists():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/integrantes/31/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.delete',
        side_effect=Formulario2AIntegranteServiceError(
            'No se puede eliminar el integrante porque tiene planillas de entrega asociadas',
            conflict=True,
        ),
    ):
        response = Formulario2AIntegranteDetailView.as_view()(request, integrante_id=31)

    assert response.status_code == 409
    assert response.data['error'] == (
        'No se puede eliminar el integrante porque tiene planillas de entrega asociadas'
    )


def test_delete_integrantes_returns_no_content():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/integrantes/31/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.delete',
    ) as delete:
        response = Formulario2AIntegranteDetailView.as_view()(request, integrante_id=31)

    assert response.status_code == 204
    delete.assert_called_once_with(31)


def test_delete_integrantes_returns_not_found():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/integrantes/31/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.delete',
        side_effect=Formulario2AIntegranteServiceError(
            'El integrante indicado no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AIntegranteDetailView.as_view()(request, integrante_id=31)

    assert response.status_code == 404
    assert response.data['error'] == 'El integrante indicado no existe'


def test_delete_integrantes_rejects_invalid_id():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/integrantes/0/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.delete',
    ) as delete:
        response = Formulario2AIntegranteDetailView.as_view()(request, integrante_id=0)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo integrante_id debe ser un número entero'
    delete.assert_not_called()
