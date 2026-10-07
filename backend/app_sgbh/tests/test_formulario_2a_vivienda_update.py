from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers import first_error_message
from app_sgbh.serializers.formulario_2a_vivienda import ViviendaUpdateSerializer
from app_sgbh.services.formulario_2a_vivienda import (
    Formulario2AViviendaService,
    Formulario2AViviendaServiceError,
)
from app_sgbh.views.formulario_2a_vivienda_view import Formulario2AViviendaDetailView


class _DoesNotExist(Exception):
    pass


class _Vivienda:
    def __init__(self):
        self.pk = 21
        self.formulario_2a_id = 10
        self.numero_orden = 3
        self.fecha_creacion = 'fecha-original'
        self.numero_lote = 'L-1'
        self.tenencia_propia = None
        self.tipo_uso_instalacion_id = 2
        self.condicion_vivienda_id = None
        self.material_techo_id = None
        self.material_pared_id = None
        self.material_piso_id = None
        self.saved = False

    def save(self):
        self.saved = True


def _parse_modificar(data):
    serializer = ViviendaUpdateSerializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data, None
    return None, first_error_message(serializer.errors)


def _body(**overrides):
    data = {
        'numero_lote': 'L-9',
        'tipo_uso_instalacion_id': 4,
    }
    data.update(overrides)
    return data


def _update_kwargs(**overrides):
    data = {
        'numero_lote': 'L-9',
        'tipo_uso_instalacion_id': 4,
        'tenencia_propia': None,
        'condicion_vivienda_id': None,
        'material_techo_id': None,
        'material_pared_id': None,
        'material_piso_id': None,
    }
    data.update(overrides)
    return data


def _formulario_existente(formulario, estado_registro_id=1):
    formulario.objects.select_for_update.return_value.get.return_value = (
        SimpleNamespace(pk=10, estado_registro_id=estado_registro_id)
    )


def test_parse_modificar_accepts_editable_fields_without_formulario():
    parsed, error = _parse_modificar(_body(numero_lote='  L-9  ', tenencia_propia='0'))

    assert error is None
    assert 'formulario_2a_id' not in parsed
    assert 'numero_orden' not in parsed
    assert parsed['numero_lote'] == 'L-9'
    assert parsed['tenencia_propia'] is False
    assert parsed['tipo_uso_instalacion_id'] == 4


def test_parse_modificar_ignores_formulario_2a_id_when_the_view_already_rejected_it():
    parsed, error = _parse_modificar(_body(formulario_2a_id=99, numero_orden=1))

    assert error is None
    assert 'formulario_2a_id' not in parsed
    assert 'numero_orden' not in parsed


def test_update_rejects_missing_vivienda():
    with (
        patch('app_sgbh.services.formulario_2a_vivienda.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a_vivienda.Formulario2A') as formulario,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'
        ) as vivienda,
    ):
        vivienda.DoesNotExist = _DoesNotExist
        vivienda.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.update(21, **_update_kwargs())

    assert exc.value.not_found is True
    assert exc.value.message == 'La vivienda indicada no existe'
    formulario.objects.select_for_update.assert_not_called()


def test_update_rejects_inactive_formulario():
    row = _Vivienda()
    with (
        patch('app_sgbh.services.formulario_2a_vivienda.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a_vivienda.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'
        ) as vivienda,
    ):
        vivienda.objects.select_for_update.return_value.get.return_value = row
        _formulario_existente(formulario, estado_registro_id=2)

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.update(21, **_update_kwargs())

    assert exc.value.conflict is True
    assert 'estado de registro es inactivo' in exc.value.message
    planilla.objects.filter.assert_not_called()
    assert row.saved is False
    assert row.numero_lote == 'L-1'


def test_update_rejects_planilla_emitida():
    row = _Vivienda()
    with (
        patch('app_sgbh.services.formulario_2a_vivienda.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a_vivienda.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'
        ) as vivienda,
    ):
        vivienda.objects.select_for_update.return_value.get.return_value = row
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.update(21, **_update_kwargs())

    assert exc.value.conflict is True
    assert 'planilla BAH emitida y activa' in exc.value.message
    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=10,
        estado_planilla__codigo='EMITIDA',
    )
    assert row.saved is False


def test_update_keeps_formulario_orden_and_fecha_creacion():
    row = _Vivienda()
    with (
        patch('app_sgbh.services.formulario_2a_vivienda.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a_vivienda.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.TipoUsoInstalacion'
        ) as tipo_uso,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.CondicionVivienda'
        ) as condicion,
        patch('app_sgbh.services.formulario_2a_vivienda.MaterialTecho') as techo,
        patch('app_sgbh.services.formulario_2a_vivienda.MaterialPared') as pared,
        patch('app_sgbh.services.formulario_2a_vivienda.MaterialPiso') as piso,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'
        ) as vivienda,
    ):
        vivienda.objects.select_for_update.return_value.get.return_value = row
        stored = object()
        vivienda.objects.select_related.return_value.get.return_value = stored
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        tipo_uso.objects.filter.return_value.exists.return_value = True
        condicion.objects.filter.return_value.exists.return_value = True
        techo.objects.filter.return_value.exists.return_value = True
        pared.objects.filter.return_value.exists.return_value = True
        piso.objects.filter.return_value.exists.return_value = True

        result = Formulario2AViviendaService.update(
            21,
            **_update_kwargs(
                numero_lote='  L-20  ',
                tenencia_propia=True,
                condicion_vivienda_id=3,
                material_techo_id=4,
                material_pared_id=5,
                material_piso_id=6,
            ),
        )

    assert result is stored
    assert row.saved is True
    assert row.formulario_2a_id == 10
    assert row.numero_orden == 3
    assert row.fecha_creacion == 'fecha-original'
    assert row.numero_lote == 'L-20'
    assert row.tenencia_propia is True
    assert row.tipo_uso_instalacion_id == 4
    assert row.condicion_vivienda_id == 3
    assert row.material_techo_id == 4
    assert row.material_pared_id == 5
    assert row.material_piso_id == 6
    vivienda.objects.select_for_update.return_value.get.assert_called_once_with(pk=21)
    vivienda.objects.select_related.return_value.get.assert_called_once_with(pk=21)


def test_put_viviendas_rejects_formulario_2a_id():
    factory = APIRequestFactory()
    request = factory.put(
        '/api/sgbh/viviendas/21/',
        _body(formulario_2a_id=99),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.update',
    ) as update:
        response = Formulario2AViviendaDetailView.as_view()(request, vivienda_id=21)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo formulario_2a_id no puede modificarse'
    update.assert_not_called()


def test_put_viviendas_rejects_numero_orden():
    factory = APIRequestFactory()
    request = factory.put(
        '/api/sgbh/viviendas/21/',
        _body(numero_orden=1),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.update',
    ) as update:
        response = Formulario2AViviendaDetailView.as_view()(request, vivienda_id=21)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo numero_orden no puede modificarse'
    update.assert_not_called()


def test_put_viviendas_returns_not_found():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/viviendas/21/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.update',
        side_effect=Formulario2AViviendaServiceError(
            'La vivienda indicada no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AViviendaDetailView.as_view()(request, vivienda_id=21)

    assert response.status_code == 404
    assert response.data['error'] == 'La vivienda indicada no existe'


def test_put_viviendas_returns_updated_vivienda():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/viviendas/21/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    updated = {'vivienda_id': 21, 'numero_lote': 'L-9'}
    instance = object()

    with (
        patch(
            'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.update',
            return_value=instance,
        ) as update,
        patch(
            'app_sgbh.views.formulario_2a_vivienda_view.ViviendaBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = updated
        response = Formulario2AViviendaDetailView.as_view()(request, vivienda_id=21)

    assert response.status_code == 200
    assert response.data == updated
    update.assert_called_once()
    serializer_cls.assert_called_once_with(instance)
    assert update.call_args.args == (21,)
    assert update.call_args.kwargs['numero_lote'] == 'L-9'
    assert update.call_args.kwargs['tipo_uso_instalacion_id'] == 4
    assert 'formulario_2a_id' not in update.call_args.kwargs
    assert 'numero_orden' not in update.call_args.kwargs
