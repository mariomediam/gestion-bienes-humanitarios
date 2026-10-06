from datetime import date, datetime, time, timezone
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers import Formulario2AUpdateSerializer, first_error_message
from app_sgbh.services.formulario_2a import (
    Formulario2AService,
    Formulario2AServiceError,
)
from app_sgbh.views.formulario_2a_view import Formulario2ADetailView


class _DoesNotExist(Exception):
    pass


class _Row:
    def __init__(self):
        self.pk = 15
        self.emergencia_id = 4
        self.estado_registro_id = 1
        self.c_usuari_login = 'creador'
        self.fecha_creacion = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.saved = False

    def save(self):
        self.saved = True


def _parse_modificar(data):
    serializer = Formulario2AUpdateSerializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data, None
    return None, first_error_message(serializer.errors)


def _body(**overrides):
    data = {
        'departamento_id': '20',
        'provincia_id': '01',
        'distrito_id': '01',
        'fecha_empadronamiento': '2026-10-05',
        'evaluador_id': 7,
        'estado_registro_id': 2,
    }
    data.update(overrides)
    return data


def _update_kwargs(**overrides):
    data = {
        'departamento_id': '20',
        'provincia_id': '01',
        'distrito_id': '01',
        'fecha_empadronamiento': date(2026, 10, 5),
        'evaluador_id': 7,
        'estado_registro_id': 2,
        'hora_empadronamiento': None,
        'localidad': None,
        'barrio_sector_urbanizacion': None,
        'centro_poblado': None,
        'caserio': None,
        'anexo': None,
        'calle_manzana': None,
        'edificio_piso_dpto': None,
        'otros_ubicacion': None,
        'numero_hoja': 1,
        'total_hojas': None,
        'institucion': None,
    }
    data.update(overrides)
    return data


def test_parse_modificar_accepts_the_same_fields_as_create_without_emergencia():
    parsed, error = _parse_modificar(_body(localidad='  Centro  ', numero_hoja=2))

    assert error is None
    assert 'emergencia_id' not in parsed
    assert parsed['localidad'] == 'Centro'
    assert parsed['numero_hoja'] == 2
    assert parsed['estado_registro_id'] == 2


def test_parse_modificar_ignores_emergencia_id_when_the_view_already_rejected_it():
    parsed, error = _parse_modificar(_body(emergencia_id=99))

    assert error is None
    assert 'emergencia_id' not in parsed


def test_update_rejects_missing_formulario():
    with (
        patch('app_sgbh.services.formulario_2a.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a.Formulario2A') as formulario,
    ):
        formulario.DoesNotExist = _DoesNotExist
        formulario.objects.get.side_effect = _DoesNotExist

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.update(15, **_update_kwargs())

    assert exc.value.not_found is True
    assert exc.value.message == 'El formulario EDAN 2A indicado no existe'


def test_update_keeps_emergencia_and_creator_and_sets_fecha_modificacion():
    moment = datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc)
    with (
        patch('app_sgbh.services.formulario_2a.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.Distrito') as distrito,
        patch('app_sgbh.services.formulario_2a.Personal') as personal,
        patch('app_sgbh.services.formulario_2a.EstadoRegistro') as estado,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch('app_sgbh.services.formulario_2a._formularios_con_distrito') as detalle,
        patch('app_sgbh.services.formulario_2a.timezone.now', return_value=moment),
    ):
        row = _Row()
        formulario.DoesNotExist = _DoesNotExist
        formulario.objects.get.return_value = row
        distrito.objects.filter.return_value.exists.return_value = True
        personal.objects.filter.return_value.first.return_value = SimpleNamespace(
            es_evaluador_edan=True,
        )
        estado.objects.filter.return_value.exists.return_value = True
        planilla.objects.filter.return_value.exists.return_value = False
        stored = detalle.return_value.get.return_value

        result = Formulario2AService.update(
            15,
            **_update_kwargs(localidad='Centro', numero_hoja=2, total_hojas=3),
        )

    assert result is stored
    assert row.saved is True
    assert row.emergencia_id == 4
    assert row.c_usuari_login == 'creador'
    assert row.fecha_creacion == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert row.fecha_modificacion == moment
    assert row.localidad == 'Centro'
    assert row.numero_hoja == 2
    assert row.total_hojas == 3
    assert row.evaluador_id == 7
    assert row.estado_registro_id == 2
    detalle.return_value.get.assert_called_once_with(pk=15)


def test_update_rejects_personal_that_is_not_evaluador():
    with (
        patch('app_sgbh.services.formulario_2a.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.Distrito') as distrito,
        patch('app_sgbh.services.formulario_2a.Personal') as personal,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
    ):
        row = _Row()
        formulario.DoesNotExist = _DoesNotExist
        formulario.objects.get.return_value = row
        distrito.objects.filter.return_value.exists.return_value = True
        personal.objects.filter.return_value.first.return_value = SimpleNamespace(
            es_evaluador_edan=False,
        )
        planilla.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.update(15, **_update_kwargs())

    assert exc.value.message == (
        'El personal indicado no puede registrarse como evaluador EDAN'
    )
    assert row.saved is False
    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=15,
        estado_planilla__codigo='EMITIDA',
    )


def test_update_rejects_inactive_estado_registro():
    with (
        patch('app_sgbh.services.formulario_2a.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
    ):
        row = _Row()
        row.estado_registro_id = 2
        formulario.DoesNotExist = _DoesNotExist
        formulario.objects.get.return_value = row

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.update(15, **_update_kwargs())

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede modificar el formulario EDAN 2A porque su estado de registro es inactivo'
    )
    assert row.saved is False
    planilla.objects.filter.assert_not_called()


def test_update_rejects_planilla_emitida_activa():
    with (
        patch('app_sgbh.services.formulario_2a.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
    ):
        row = _Row()
        formulario.DoesNotExist = _DoesNotExist
        formulario.objects.get.return_value = row
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.update(15, **_update_kwargs())

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede modificar el formulario EDAN 2A porque tiene una planilla BAH emitida y activa'
    )
    assert row.saved is False


@pytest.mark.parametrize(
    ('body', 'status_code', 'message'),
    [
        (
            {'emergencia_id': 9, **{
                'departamento_id': '20',
                'provincia_id': '01',
                'distrito_id': '01',
                'fecha_empadronamiento': '2026-10-05',
                'evaluador_id': 7,
                'estado_registro_id': 2,
            }},
            400,
            'El campo emergencia_id no puede modificarse',
        ),
    ],
)
def test_put_rejects_emergencia_id(body, status_code, message):
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/formularios-2a/15/', body, format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2ADetailView.as_view()(request, formulario_2a_id=15)

    assert response.status_code == status_code
    assert response.data['error'] == message


def test_put_returns_conflict_when_formulario_is_inactive():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/formularios-2a/15/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_view.Formulario2AService.update',
        side_effect=Formulario2AServiceError(
            'No se puede modificar el formulario EDAN 2A porque su estado de registro es inactivo',
            conflict=True,
        ),
    ):
        response = Formulario2ADetailView.as_view()(request, formulario_2a_id=15)

    assert response.status_code == 409
    assert response.data['error'] == (
        'No se puede modificar el formulario EDAN 2A porque su estado de registro es inactivo'
    )


def test_put_returns_not_found_when_formulario_does_not_exist():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/formularios-2a/15/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_view.Formulario2AService.update',
        side_effect=Formulario2AServiceError(
            'El formulario EDAN 2A indicado no existe',
            not_found=True,
        ),
    ):
        response = Formulario2ADetailView.as_view()(request, formulario_2a_id=15)

    assert response.status_code == 404
    assert response.data['error'] == 'El formulario EDAN 2A indicado no existe'


def test_put_returns_updated_formulario():
    factory = APIRequestFactory()
    request = factory.put(
        '/api/sgbh/formularios-2a/15/',
        _body(hora_empadronamiento='08:15'),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    updated = {'formulario_2a_id': 15, 'emergencia_id': 4}
    instance = object()

    with (
        patch(
            'app_sgbh.views.formulario_2a_view.Formulario2AService.update',
            return_value=instance,
        ) as update,
        patch(
            'app_sgbh.views.formulario_2a_view.Formulario2ADetalleSerializer',
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = updated
        response = Formulario2ADetailView.as_view()(request, formulario_2a_id=15)

    assert response.status_code == 200
    assert response.data == updated
    update.assert_called_once()
    assert update.call_args.args == (15,)
    assert update.call_args.kwargs['hora_empadronamiento'] == time(8, 15)
    assert 'emergencia_id' not in update.call_args.kwargs
    assert 'c_usuari_login' not in update.call_args.kwargs
    serializer_cls.assert_called_once_with(instance)
