from datetime import date, datetime, time, timezone
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.emergencia import EmergenciaService, EmergenciaServiceError
from app_sgbh.views.emergencia_view import EmergenciaDetailView


class _DoesNotExist(Exception):
    pass


class _Row:
    def __init__(self):
        self.pk = 9
        self.c_usuari_login = 'creador'
        self.fecha_creacion = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.saved = False

    def save(self):
        self.saved = True


def _body(**overrides):
    data = {
        'numero_evaluacion': 'EV-002',
        'codigo_sinpad': 'SIN-002',
        'tipo_peligro_id': 4,
        'fecha_emergencia': '2026-10-02',
        'hora_ocurrencia_estimada': '09:15',
        'esta_activo': False,
    }
    data.update(overrides)
    return data


def _patch_update():
    return (
        patch('app_sgbh.services.emergencia.transaction.atomic'),
        patch('app_sgbh.services.emergencia.TipoPeligro'),
        patch('app_sgbh.services.emergencia.Emergencia'),
        patch('app_sgbh.services.emergencia._formularios_con_distrito', return_value='qs'),
        patch(
            'app_sgbh.services.emergencia.timezone.now',
            return_value=datetime(2026, 10, 4, 12, 0, tzinfo=timezone.utc),
        ),
    )


def test_update_rejects_codigo_sinpad_used_by_another_emergency():
    patches = _patch_update()
    with patches[0], patches[1] as tipo_peligro, patches[2] as emergencia, patches[3], patches[4]:
        row = _Row()
        emergencia.DoesNotExist = _DoesNotExist
        emergencia.objects.get.return_value = row
        tipo_peligro.objects.filter.return_value.exists.return_value = True
        emergencia.objects.filter.return_value.exclude.return_value.exists.return_value = True

        with pytest.raises(EmergenciaServiceError) as exc:
            EmergenciaService.update(
                9,
                numero_evaluacion='EV-002',
                codigo_sinpad=' sin-002 ',
                tipo_peligro_id=4,
                fecha_emergencia=date(2026, 10, 2),
            )

    assert exc.value.conflict is True
    assert exc.value.message == 'Ya existe una emergencia con el código SINPAD indicado'
    emergencia.objects.filter.return_value.exclude.assert_called_once_with(pk=9)
    assert row.saved is False


def test_update_allows_the_same_codigo_sinpad_on_the_current_emergency():
    patches = _patch_update()
    with patches[0], patches[1] as tipo_peligro, patches[2] as emergencia, patches[3], patches[4]:
        row = _Row()
        emergencia.DoesNotExist = _DoesNotExist
        emergencia.objects.get.return_value = row
        tipo_peligro.objects.filter.return_value.exists.return_value = True
        emergencia.objects.filter.return_value.exclude.return_value.exists.return_value = False
        stored = (
            emergencia.objects.select_related.return_value
            .prefetch_related.return_value.get.return_value
        )

        result = EmergenciaService.update(
            9,
            numero_evaluacion='EV-002',
            codigo_sinpad='SIN-002',
            tipo_peligro_id=4,
            fecha_emergencia=date(2026, 10, 2),
            hora_ocurrencia_estimada=time(9, 15),
            esta_activo=False,
        )

    assert result is stored
    assert row.saved is True
    assert row.numero_evaluacion == 'EV-002'
    assert row.codigo_sinpad == 'SIN-002'
    assert row.tipo_peligro_id == 4
    assert row.fecha_emergencia == date(2026, 10, 2)
    assert row.hora_ocurrencia_estimada == time(9, 15)
    assert row.esta_activo is False
    assert row.fecha_modificacion == datetime(2026, 10, 4, 12, 0, tzinfo=timezone.utc)
    assert row.c_usuari_login == 'creador'
    assert row.fecha_creacion == datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_update_rejects_missing_emergency():
    patches = _patch_update()
    with patches[0], patches[1], patches[2] as emergencia, patches[3], patches[4]:
        emergencia.DoesNotExist = _DoesNotExist
        emergencia.objects.get.side_effect = _DoesNotExist

        with pytest.raises(EmergenciaServiceError) as exc:
            EmergenciaService.update(
                9,
                numero_evaluacion='EV-002',
                codigo_sinpad='SIN-002',
                tipo_peligro_id=4,
                fecha_emergencia=date(2026, 10, 2),
            )

    assert exc.value.not_found is True
    assert exc.value.message == 'La emergencia indicada no existe'


def test_put_emergencia_returns_conflict_when_codigo_sinpad_exists():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/emergencias/9/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.emergencia_view.EmergenciaService.update',
        side_effect=EmergenciaServiceError(
            'Ya existe una emergencia con el código SINPAD indicado',
            conflict=True,
        ),
    ):
        response = EmergenciaDetailView.as_view()(request, emergencia_id=9)

    assert response.status_code == 409
    assert response.data['error'] == 'Ya existe una emergencia con el código SINPAD indicado'


def test_put_emergencia_returns_updated_emergency():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/emergencias/9/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    updated = {'emergencia_id': 9, 'codigo_sinpad': 'SIN-002'}
    instance = object()

    with (
        patch(
            'app_sgbh.views.emergencia_view.EmergenciaService.update',
            return_value=instance,
        ) as update,
        patch('app_sgbh.views.emergencia_view.EmergenciaSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = updated
        response = EmergenciaDetailView.as_view()(request, emergencia_id=9)

    assert response.status_code == 200
    assert response.data == updated
    update.assert_called_once()
    assert update.call_args.args == (9,)
    assert update.call_args.kwargs['codigo_sinpad'] == 'SIN-002'
    assert update.call_args.kwargs['esta_activo'] is False
    serializer_cls.assert_called_once_with(instance)
