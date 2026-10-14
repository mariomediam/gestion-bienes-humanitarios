from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.db.models import ProtectedError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.formulario_2a_medio_vida import (
    Formulario2AMedioVidaService,
    Formulario2AMedioVidaServiceError,
)
from app_sgbh.views.formulario_2a_medio_vida_view import (
    Formulario2AMedioVidaDetailView,
)


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


def test_delete_rejects_missing_medio_vida():
    with (
        patch('app_sgbh.services.formulario_2a_medio_vida.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
        ) as medio_vida,
    ):
        medio_vida.DoesNotExist = _DoesNotExist
        medio_vida.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.delete(21)

    assert exc.value.not_found is True
    assert exc.value.message == 'El medio de vida indicado no existe'
    familia.objects.select_for_update.assert_not_called()


def test_delete_rejects_inactive_formulario():
    row = SimpleNamespace(pk=21, familia_id=8)
    with (
        patch('app_sgbh.services.formulario_2a_medio_vida.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AVivienda'
        ) as vivienda,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2A'
        ) as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
        ) as medio_vida,
    ):
        medio_vida.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario, estado_registro_id=2)

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.delete(21)

    assert exc.value.conflict is True
    assert 'estado de registro es inactivo' in exc.value.message
    planilla.objects.filter.assert_not_called()


def test_delete_rejects_planilla_emitida():
    row = SimpleNamespace(pk=21, familia_id=8)
    with (
        patch('app_sgbh.services.formulario_2a_medio_vida.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AVivienda'
        ) as vivienda,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2A'
        ) as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
        ) as medio_vida,
    ):
        medio_vida.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.delete(21)

    assert exc.value.conflict is True
    assert 'planilla BAH emitida y activa' in exc.value.message
    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=10,
        estado_planilla__codigo='EMITIDA',
    )


def test_delete_removes_medio_vida():
    row = SimpleNamespace(pk=21, familia_id=8)
    row.delete = lambda: setattr(row, 'deleted', True)
    with (
        patch('app_sgbh.services.formulario_2a_medio_vida.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AVivienda'
        ) as vivienda,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2A'
        ) as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
        ) as medio_vida,
    ):
        medio_vida.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False

        Formulario2AMedioVidaService.delete(21)

    assert row.deleted is True
    medio_vida.objects.select_for_update.return_value.get.assert_called_once_with(
        pk=21
    )


def test_delete_rejects_when_database_protects_related_rows():
    row = SimpleNamespace(pk=21, familia_id=8)
    row.delete = lambda: (_ for _ in ()).throw(ProtectedError('protected', {object()}))
    with (
        patch('app_sgbh.services.formulario_2a_medio_vida.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AVivienda'
        ) as vivienda,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2A'
        ) as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
        ) as medio_vida,
    ):
        medio_vida.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.delete(21)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar el medio de vida porque tiene registros asociados'
    )


def test_delete_medios_vida_returns_conflict_when_formulario_is_locked():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/medios-vida/21/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.delete',
        side_effect=Formulario2AMedioVidaServiceError(
            'No se puede modificar el formulario EDAN 2A porque tiene una planilla BAH emitida y activa',
            conflict=True,
        ),
    ):
        response = Formulario2AMedioVidaDetailView.as_view()(
            request,
            medio_vida_id=21,
        )

    assert response.status_code == 409
    assert response.data['error'] == (
        'No se puede modificar el formulario EDAN 2A porque tiene una planilla BAH emitida y activa'
    )


def test_delete_medios_vida_returns_no_content():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/medios-vida/21/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.delete',
    ) as delete:
        response = Formulario2AMedioVidaDetailView.as_view()(
            request,
            medio_vida_id=21,
        )

    assert response.status_code == 204
    delete.assert_called_once_with(21)


def test_delete_medios_vida_returns_not_found():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/medios-vida/21/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.delete',
        side_effect=Formulario2AMedioVidaServiceError(
            'El medio de vida indicado no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AMedioVidaDetailView.as_view()(
            request,
            medio_vida_id=21,
        )

    assert response.status_code == 404
    assert response.data['error'] == 'El medio de vida indicado no existe'


def test_delete_medios_vida_rejects_invalid_id():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/medios-vida/0/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.delete',
    ) as delete:
        response = Formulario2AMedioVidaDetailView.as_view()(
            request,
            medio_vida_id=0,
        )

    assert response.status_code == 400
    assert response.data['error'] == 'El campo medio_vida_id debe ser un número entero'
    delete.assert_not_called()
