from contextlib import ExitStack, contextmanager
from datetime import date, datetime, timezone as dt_timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from django.db import IntegrityError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.movimiento import MovimientoServiceError
from app_sgbh.services.planilla_entrega import (
    PlanillaEntregaService,
    PlanillaEntregaServiceError,
)
from app_sgbh.views.planilla_entrega_view import PlanillaEntregaDetailView

FIXED_NOW = datetime(2026, 10, 20, 15, 0, tzinfo=dt_timezone.utc)
ORIGINAL_CREATED = datetime(2026, 1, 2, tzinfo=dt_timezone.utc)
FECHA_ANULACION = datetime(2026, 3, 1, 8, 0, tzinfo=dt_timezone.utc)


class _DoesNotExist(Exception):
    pass


class _Row:
    def __init__(self, *, movimiento_almacen_id=15):
        self.pk = 21
        self.planilla_entrega_id = 21
        self.movimiento_almacen_id = movimiento_almacen_id
        self.fecha_anulacion = FECHA_ANULACION
        self.motivo_anulacion = 'Error de registro'
        self.fecha_creacion = ORIGINAL_CREATED
        self.update_fields = None

    def save(self, update_fields=None):
        self.update_fields = update_fields


@contextmanager
def _patched(
    *,
    formulario_2a_id=9,
    tiene_planilla=False,
    estado=None,
    maximo=7,
    row=None,
):
    with ExitStack() as stack:
        mocks = {
            'atomic': stack.enter_context(
                patch('app_sgbh.services.planilla_entrega.transaction.atomic')
            ),
            'now': stack.enter_context(
                patch(
                    'app_sgbh.services.planilla_entrega.timezone.now',
                    return_value=FIXED_NOW,
                )
            ),
            'integrante': stack.enter_context(
                patch('app_sgbh.services.planilla_entrega.Formulario2AIntegrante')
            ),
            'planilla': stack.enter_context(
                patch('app_sgbh.services.planilla_entrega.PlanillaEntrega')
            ),
            'estado': stack.enter_context(
                patch('app_sgbh.services.planilla_entrega.EstadoPlanilla')
            ),
            'movimiento': stack.enter_context(
                patch('app_sgbh.services.planilla_entrega.MovimientoService')
            ),
        }
        mocks['integrante'].objects.filter.return_value.values_list.return_value.first.return_value = (
            formulario_2a_id
        )
        consulta = Mock()
        consulta.exclude.return_value = consulta
        consulta.exists.return_value = tiene_planilla
        consulta.aggregate.return_value = {'maximo': maximo}
        mocks['planilla'].objects.filter.return_value = consulta
        mocks['consulta'] = consulta
        mocks['planilla'].DoesNotExist = _DoesNotExist
        if row is None:
            row = _Row()
        mocks['row'] = row
        mocks['planilla'].objects.get.return_value = row
        if estado is None:
            estado = SimpleNamespace(esta_activo=True)
        mocks['estado'].objects.filter.return_value.first.return_value = estado
        movimiento = _stored_movimiento()
        mocks['movimiento'].update.return_value = movimiento
        mocks['movimiento_row'] = movimiento
        yield mocks


def _payload(**overrides):
    data = {
        'almacen_id': 1,
        'tipo_movimiento_id': 2,
        'estado_movimiento_id': 1,
        'movimiento_origen_id': None,
        'fecha_movimiento': datetime(2026, 10, 19, 9, 30),
        'documento_referencia': 'FAC-1',
        'fecha_documento': date(2026, 10, 15),
        'destinatario': 'Municipalidad',
        'observacion': 'Ingreso',
        'fecha_confirmacion': None,
        'encargado_almacen_id': 4,
        'c_usuari_login': 'mmedina',
        'detalles': [
            {
                'bien_id': 8,
                'cantidad': Decimal('3.000000'),
                'cantidad_texto': '3',
                'es_devolvible': False,
                'observacion': 'Caja',
            }
        ],
        'anio_planilla': 2026,
        'numero_planilla': 4,
        'integrante_receptor_id': 100,
        'fecha_entrega': date(2026, 10, 19),
        'estado_planilla_id': 1,
        'planilla_entrega_observacion': ' Entrega ',
        'fecha_emision': datetime(2026, 10, 19, 10, 0),
    }
    data.update(overrides)
    return data


def _stored_movimiento():
    return SimpleNamespace(
        movimiento_id=15,
        almacen_id=1,
        tipo_movimiento_id=2,
        estado_movimiento_id=1,
        movimiento_origen_id=None,
        fecha_movimiento=datetime(2026, 10, 19, 9, 30, tzinfo=dt_timezone.utc),
        documento_referencia='FAC-1',
        fecha_documento=date(2026, 10, 15),
        destinatario='Municipalidad',
        observacion='Ingreso',
        fecha_confirmacion=None,
        encargado_almacen_id=4,
        c_usuari_login='mmedina',
        fecha_creacion=FIXED_NOW,
        fecha_modificacion=FIXED_NOW,
        detalles=[
            SimpleNamespace(
                movimiento_detalle_id=100,
                movimiento_id=15,
                bien_id=8,
                cantidad=Decimal('3.000000'),
                cantidad_texto='3',
                es_devolvible=False,
                observacion='Caja',
                fecha_creacion=FIXED_NOW,
            )
        ],
    )


def test_update_reemplaza_planilla_y_movimiento_vinculado():
    with _patched() as mocks:
        updated = PlanillaEntregaService.update(21, **_payload())

    mocks['planilla'].objects.get.assert_called_once_with(pk=21)
    mocks['consulta'].exclude.assert_called_once_with(pk=21)
    mocks['consulta'].aggregate.assert_not_called()
    kwargs = mocks['movimiento'].update.call_args.kwargs
    assert mocks['movimiento'].update.call_args.args == (15,)
    assert kwargs['desde_planilla'] is True
    assert kwargs['almacen_id'] == 1
    assert kwargs['c_usuari_login'] == 'mmedina'
    assert kwargs['observacion'] == 'Ingreso'
    assert kwargs['detalles'][0]['bien_id'] == 8
    assert updated.numero_planilla == 4
    assert updated.anio_planilla == 2026
    assert updated.integrante_receptor_id == 100
    assert updated.fecha_entrega == date(2026, 10, 19)
    assert updated.estado_planilla_id == 1
    assert updated.observacion == 'Entrega'
    assert updated.fecha_emision == datetime(2026, 10, 19, 10, 0)
    assert updated.fecha_anulacion == FECHA_ANULACION
    assert updated.motivo_anulacion == 'Error de registro'
    assert updated.c_usuari_login == 'mmedina'
    assert updated.fecha_creacion == ORIGINAL_CREATED
    assert updated.fecha_modificacion == FIXED_NOW
    assert updated.movimiento_almacen is mocks['movimiento_row']
    assert updated.movimiento_almacen_id == 15
    assert 'fecha_anulacion' not in updated.update_fields
    assert 'motivo_anulacion' not in updated.update_fields
    assert 'fecha_creacion' not in updated.update_fields
    assert 'fecha_modificacion' in updated.update_fields
    mocks['atomic'].assert_called_once_with(using='sgbh')


def test_update_asigna_el_maximo_siguiente_del_anio():
    with _patched(maximo=7) as mocks:
        updated = PlanillaEntregaService.update(21, **_payload(numero_planilla=None))

    mocks['planilla'].objects.filter.assert_any_call(anio_planilla=2026)
    assert updated.numero_planilla == 8


def test_update_rechaza_planilla_inexistente():
    with _patched() as mocks:
        mocks['planilla'].objects.get.side_effect = _DoesNotExist()
        with pytest.raises(PlanillaEntregaServiceError) as exc:
            PlanillaEntregaService.update(21, **_payload())

    assert exc.value.not_found is True
    assert exc.value.message == 'La planilla BAH indicada no existe'
    mocks['movimiento'].update.assert_not_called()


def test_update_rechaza_planilla_sin_movimiento():
    with _patched(row=_Row(movimiento_almacen_id=None)) as mocks:
        with pytest.raises(PlanillaEntregaServiceError) as exc:
            PlanillaEntregaService.update(21, **_payload())

    assert exc.value.message == 'La planilla BAH no tiene un movimiento de almacén'
    mocks['movimiento'].update.assert_not_called()
    assert mocks['row'].update_fields is None


def test_update_rechaza_formulario_que_ya_tiene_planilla():
    with _patched(tiene_planilla=True) as mocks:
        with pytest.raises(PlanillaEntregaServiceError) as exc:
            PlanillaEntregaService.update(21, **_payload())

    assert exc.value.conflict is True
    assert 'ya tiene registrada una planilla BAH' in exc.value.message
    mocks['movimiento'].update.assert_not_called()
    assert mocks['row'].update_fields is None


def test_update_rechaza_integrante_inexistente():
    with _patched(formulario_2a_id=None) as mocks:
        with pytest.raises(PlanillaEntregaServiceError) as exc:
            PlanillaEntregaService.update(21, **_payload())

    assert exc.value.message == 'El integrante receptor indicado no existe'
    mocks['movimiento'].update.assert_not_called()


def test_update_rechaza_estado_de_planilla_inactivo():
    with _patched(estado=SimpleNamespace(esta_activo=False)) as mocks:
        with pytest.raises(PlanillaEntregaServiceError) as exc:
            PlanillaEntregaService.update(21, **_payload())

    assert exc.value.message == 'El estado de planilla indicado no está activo'
    mocks['movimiento'].update.assert_not_called()


def test_update_propaga_el_error_del_movimiento_sin_grabar_planilla():
    with _patched() as mocks:
        mocks['movimiento'].update.side_effect = MovimientoServiceError(
            'El almacén indicado no está activo'
        )
        with pytest.raises(MovimientoServiceError):
            PlanillaEntregaService.update(21, **_payload())

    assert mocks['row'].update_fields is None


def test_update_oculta_un_error_de_integridad_al_grabar_la_planilla():
    with _patched() as mocks:
        mocks['row'].save = Mock(side_effect=IntegrityError())
        with pytest.raises(PlanillaEntregaServiceError) as exc:
            PlanillaEntregaService.update(21, **_payload())

    assert exc.value.message == 'No se pudo modificar la planilla BAH'


def _authenticate(request):
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))


def _body(**overrides):
    data = {
        'almacen_id': 1,
        'tipo_movimiento_id': 2,
        'estado_movimiento_id': 1,
        'fecha_movimiento': '2026-10-19T09:30:00',
        'documento_referencia': 'FAC-1',
        'fecha_documento': '2026-10-15',
        'destinatario': 'Municipalidad',
        'observacion': 'Ingreso',
        'encargado_almacen_id': 4,
        'c_usuari_login': 'intruso',
        'detalles': [
            {
                'bien_id': 8,
                'cantidad': '3',
                'cantidad_texto': '3',
                'es_devolvible': False,
                'observacion': 'Caja',
            }
        ],
        'anio_planilla': 2026,
        'numero_planilla': 4,
        'integrante_receptor_id': 100,
        'fecha_entrega': '2026-10-19',
        'estado_planilla_id': 1,
        'planilla_entrega_observacion': 'Entrega',
        'fecha_emision': '2026-10-19T10:00:00',
    }
    data.update(overrides)
    return data


def _stored_planilla():
    return SimpleNamespace(
        planilla_entrega_id=21,
        numero_planilla=8,
        anio_planilla=2026,
        integrante_receptor_id=100,
        fecha_entrega=date(2026, 10, 19),
        estado_planilla_id=1,
        observacion='Entrega',
        fecha_emision=datetime(2026, 10, 19, 10, 0, tzinfo=dt_timezone.utc),
        fecha_anulacion=FECHA_ANULACION,
        motivo_anulacion='Error de registro',
        c_usuari_login='mmedina',
        fecha_creacion=ORIGINAL_CREATED,
        fecha_modificacion=FIXED_NOW,
        movimiento_almacen_id=15,
        movimiento_almacen=_stored_movimiento(),
    )


def test_put_planillas_bah_modifica_movimiento_y_planilla():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/planillas-bah/21/', _body(), format='json')
    _authenticate(request)
    updated = _stored_planilla()

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.update',
        return_value=updated,
    ) as update:
        response = PlanillaEntregaDetailView.as_view()(request, planilla_entrega_id=21)

    assert response.status_code == 200
    assert update.call_args.args == (21,)
    kwargs = update.call_args.kwargs
    assert kwargs['c_usuari_login'] == 'mmedina'
    assert kwargs['anio_planilla'] == 2026
    assert kwargs['numero_planilla'] == 4
    assert kwargs['integrante_receptor_id'] == 100
    assert kwargs['fecha_entrega'] == date(2026, 10, 19)
    assert kwargs['estado_planilla_id'] == 1
    assert kwargs['planilla_entrega_observacion'] == 'Entrega'
    assert kwargs['observacion'] == 'Ingreso'
    assert kwargs['detalles'][0]['bien_id'] == 8
    assert response.data['planilla_entrega_id'] == 21
    assert response.data['fecha_anulacion'] is not None
    assert response.data['motivo_anulacion'] == 'Error de registro'
    assert response.data['movimiento']['movimiento_id'] == 15
    assert response.data['movimiento']['detalles'][0]['bien_id'] == 8


def test_put_planillas_bah_omite_numero_planilla():
    factory = APIRequestFactory()
    body = _body()
    body.pop('numero_planilla')
    request = factory.put('/api/sgbh/planillas-bah/21/', body, format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.update',
        return_value=_stored_planilla(),
    ) as update:
        response = PlanillaEntregaDetailView.as_view()(request, planilla_entrega_id=21)

    assert response.status_code == 200
    assert update.call_args.kwargs['numero_planilla'] is None


def test_put_planillas_bah_devuelve_no_encontrado():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/planillas-bah/21/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.update',
        side_effect=PlanillaEntregaServiceError(
            'La planilla BAH indicada no existe',
            not_found=True,
        ),
    ):
        response = PlanillaEntregaDetailView.as_view()(request, planilla_entrega_id=21)

    assert response.status_code == 404
    assert response.data['error'] == 'La planilla BAH indicada no existe'


def test_put_planillas_bah_devuelve_conflicto_si_el_formulario_ya_tiene_planilla():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/planillas-bah/21/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.update',
        side_effect=PlanillaEntregaServiceError(
            'El formulario EDAN 2A ya tiene registrada una planilla BAH',
            conflict=True,
        ),
    ):
        response = PlanillaEntregaDetailView.as_view()(request, planilla_entrega_id=21)

    assert response.status_code == 409
    assert 'planilla BAH' in response.data['error']


def test_put_planillas_bah_devuelve_el_error_del_movimiento():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/planillas-bah/21/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.update',
        side_effect=MovimientoServiceError('El almacén indicado no está activo'),
    ):
        response = PlanillaEntregaDetailView.as_view()(request, planilla_entrega_id=21)

    assert response.status_code == 400
    assert response.data['error'] == 'El almacén indicado no está activo'


def test_put_planillas_bah_oculta_errores_inesperados():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/planillas-bah/21/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.update',
        side_effect=RuntimeError('sql'),
    ):
        response = PlanillaEntregaDetailView.as_view()(request, planilla_entrega_id=21)

    assert response.status_code == 500
    assert response.data['error'] == 'No se pudo modificar la planilla BAH'


@pytest.mark.parametrize(
    ('planilla_entrega_id', 'body', 'message'),
    [
        (0, _body(), 'El campo planilla_entrega_id debe ser un número entero'),
        (21, {}, 'El campo almacen_id es obligatorio'),
        (21, _body(anio_planilla=None), 'El campo anio_planilla es obligatorio'),
        (
            21,
            _body(integrante_receptor_id=None),
            'El campo integrante_receptor_id es obligatorio',
        ),
        (21, _body(fecha_entrega=None), 'El campo fecha_entrega es obligatorio'),
        (
            21,
            _body(fecha_entrega='19/10/2026'),
            'El campo fecha_entrega debe tener el formato AAAA-MM-DD',
        ),
        (21, [], 'El cuerpo de la solicitud no es válido'),
    ],
)
def test_put_planillas_bah_rechaza_cuerpo_invalido(planilla_entrega_id, body, message):
    factory = APIRequestFactory()
    request = factory.put(
        f'/api/sgbh/planillas-bah/{planilla_entrega_id}/',
        body,
        format='json',
    )
    _authenticate(request)

    response = PlanillaEntregaDetailView.as_view()(
        request,
        planilla_entrega_id=planilla_entrega_id,
    )

    assert response.status_code == 400
    assert response.data['error'] == message
