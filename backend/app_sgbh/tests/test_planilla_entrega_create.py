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
    formulario_2a_id_de_integrante,
    formulario_tiene_planilla_bah,
)
from app_sgbh.views.planilla_entrega_view import PlanillaEntregaCreateView

FIXED_NOW = datetime(2026, 10, 19, 15, 0, tzinfo=dt_timezone.utc)


@contextmanager
def _patched(*, formulario_2a_id=9, tiene_planilla=False, estado=None, maximo=7):
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
        consulta.exists.return_value = tiene_planilla
        consulta.aggregate.return_value = {'maximo': maximo}
        mocks['planilla'].objects.filter.return_value = consulta
        mocks['consulta'] = consulta
        if estado is None:
            estado = SimpleNamespace(esta_activo=True)
        mocks['estado'].objects.filter.return_value.first.return_value = estado
        movimiento = _stored_movimiento()
        mocks['movimiento'].create.return_value = movimiento
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
        fecha_modificacion=None,
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


def test_formulario_2a_id_de_integrante_recorre_la_cadena():
    with patch(
        'app_sgbh.services.planilla_entrega.Formulario2AIntegrante'
    ) as integrante:
        integrante.objects.filter.return_value.values_list.return_value.first.return_value = (
            9
        )
        assert formulario_2a_id_de_integrante(100) == 9

    integrante.objects.filter.assert_called_once_with(pk=100)
    integrante.objects.filter.return_value.values_list.assert_called_once_with(
        'familia__vivienda__formulario_2a_id',
        flat=True,
    )


def test_formulario_tiene_planilla_bah_no_filtra_por_estado():
    with patch('app_sgbh.services.planilla_entrega.PlanillaEntrega') as planilla:
        planilla.objects.filter.return_value.exists.return_value = True
        assert formulario_tiene_planilla_bah(9) is True

    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=9,
    )
    planilla.objects.filter.return_value.exclude.assert_not_called()


def test_formulario_tiene_planilla_bah_puede_excluir_la_planilla_editada():
    with patch('app_sgbh.services.planilla_entrega.PlanillaEntrega') as planilla:
        consulta = planilla.objects.filter.return_value
        consulta.exclude.return_value.exists.return_value = False
        assert (
            formulario_tiene_planilla_bah(9, excluir_planilla_entrega_id=4) is False
        )

    consulta.exclude.assert_called_once_with(pk=4)


def test_create_rechaza_formulario_que_ya_tiene_planilla():
    with _patched(tiene_planilla=True) as mocks:
        with pytest.raises(PlanillaEntregaServiceError) as exc:
            PlanillaEntregaService.create(**_payload())

    assert exc.value.conflict is True
    assert 'ya tiene registrada una planilla BAH' in exc.value.message
    mocks['movimiento'].create.assert_not_called()
    mocks['planilla'].assert_not_called()


def test_create_rechaza_integrante_inexistente():
    with _patched(formulario_2a_id=None) as mocks:
        with pytest.raises(PlanillaEntregaServiceError) as exc:
            PlanillaEntregaService.create(**_payload())

    assert exc.value.message == 'El integrante receptor indicado no existe'
    mocks['movimiento'].create.assert_not_called()


def test_create_rechaza_estado_de_planilla_inactivo():
    with _patched(estado=SimpleNamespace(esta_activo=False)) as mocks:
        with pytest.raises(PlanillaEntregaServiceError) as exc:
            PlanillaEntregaService.create(**_payload())

    assert exc.value.message == 'El estado de planilla indicado no está activo'
    mocks['movimiento'].create.assert_not_called()


def test_create_graba_numero_enviado_y_deja_anulacion_nula():
    with _patched() as mocks:
        PlanillaEntregaService.create(**_payload())

    mocks['consulta'].aggregate.assert_not_called()
    kwargs = mocks['movimiento'].create.call_args.kwargs
    assert kwargs['almacen_id'] == 1
    assert kwargs['tipo_movimiento_id'] == 2
    assert kwargs['c_usuari_login'] == 'mmedina'
    assert kwargs['observacion'] == 'Ingreso'
    assert kwargs['detalles'][0]['bien_id'] == 8
    guardada = mocks['planilla'].call_args.kwargs
    assert guardada['numero_planilla'] == 4
    assert guardada['anio_planilla'] == 2026
    assert guardada['integrante_receptor_id'] == 100
    assert guardada['fecha_entrega'] == date(2026, 10, 19)
    assert guardada['estado_planilla_id'] == 1
    assert guardada['observacion'] == 'Entrega'
    assert guardada['fecha_emision'] == datetime(2026, 10, 19, 10, 0)
    assert guardada['fecha_anulacion'] is None
    assert guardada['motivo_anulacion'] is None
    assert guardada['c_usuari_login'] == 'mmedina'
    assert guardada['fecha_creacion'] == FIXED_NOW
    assert guardada['fecha_modificacion'] is None
    assert guardada['movimiento_almacen'] is mocks['movimiento_row']
    mocks['atomic'].assert_called_once_with(using='sgbh')


def test_create_asigna_el_maximo_siguiente_del_anio():
    with _patched(maximo=7) as mocks:
        PlanillaEntregaService.create(**_payload(numero_planilla=None))

    mocks['planilla'].objects.filter.assert_any_call(anio_planilla=2026)
    assert mocks['planilla'].call_args.kwargs['numero_planilla'] == 8


def test_create_empieza_en_uno_cuando_el_anio_no_tiene_planillas():
    with _patched(maximo=None) as mocks:
        PlanillaEntregaService.create(**_payload(numero_planilla=None))

    assert mocks['planilla'].call_args.kwargs['numero_planilla'] == 1


def test_create_propaga_el_error_del_movimiento_sin_grabar_planilla():
    with _patched() as mocks:
        mocks['movimiento'].create.side_effect = MovimientoServiceError(
            'El almacén indicado no está activo'
        )
        with pytest.raises(MovimientoServiceError):
            PlanillaEntregaService.create(**_payload())

    mocks['planilla'].assert_not_called()


def test_create_oculta_un_error_de_integridad_al_grabar_la_planilla():
    with _patched() as mocks:
        mocks['planilla'].return_value.save.side_effect = IntegrityError()
        with pytest.raises(PlanillaEntregaServiceError) as exc:
            PlanillaEntregaService.create(**_payload())

    assert exc.value.message == 'No se pudo registrar la planilla BAH'


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
        fecha_anulacion=None,
        motivo_anulacion=None,
        c_usuari_login='mmedina',
        fecha_creacion=FIXED_NOW,
        fecha_modificacion=None,
        movimiento_almacen_id=15,
        movimiento_almacen=_stored_movimiento(),
    )


def test_post_planillas_bah_registra_movimiento_y_planilla():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/planillas-bah/', _body(), format='json')
    _authenticate(request)
    created = _stored_planilla()

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.create',
        return_value=created,
    ) as create:
        response = PlanillaEntregaCreateView.as_view()(request)

    assert response.status_code == 201
    kwargs = create.call_args.kwargs
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
    assert response.data['fecha_anulacion'] is None
    assert response.data['motivo_anulacion'] is None
    assert response.data['movimiento']['movimiento_id'] == 15
    assert response.data['movimiento']['detalles'][0]['bien_id'] == 8


def test_post_planillas_bah_omite_numero_planilla():
    factory = APIRequestFactory()
    body = _body()
    body.pop('numero_planilla')
    request = factory.post('/api/sgbh/planillas-bah/', body, format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.create',
        return_value=_stored_planilla(),
    ) as create:
        response = PlanillaEntregaCreateView.as_view()(request)

    assert response.status_code == 201
    assert create.call_args.kwargs['numero_planilla'] is None


def test_post_planillas_bah_devuelve_conflicto_si_el_formulario_ya_tiene_planilla():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/planillas-bah/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.create',
        side_effect=PlanillaEntregaServiceError(
            'El formulario EDAN 2A ya tiene registrada una planilla BAH',
            conflict=True,
        ),
    ):
        response = PlanillaEntregaCreateView.as_view()(request)

    assert response.status_code == 409
    assert 'planilla BAH' in response.data['error']


def test_post_planillas_bah_devuelve_el_error_del_movimiento():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/planillas-bah/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.create',
        side_effect=MovimientoServiceError('El almacén indicado no está activo'),
    ):
        response = PlanillaEntregaCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El almacén indicado no está activo'


def test_post_planillas_bah_oculta_errores_inesperados():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/planillas-bah/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.create',
        side_effect=RuntimeError('sql'),
    ):
        response = PlanillaEntregaCreateView.as_view()(request)

    assert response.status_code == 500
    assert response.data['error'] == 'No se pudo registrar la planilla BAH'


@pytest.mark.parametrize(
    ('body', 'message'),
    [
        ({}, 'El campo almacen_id es obligatorio'),
        (_body(anio_planilla=None), 'El campo anio_planilla es obligatorio'),
        (
            _body(integrante_receptor_id=None),
            'El campo integrante_receptor_id es obligatorio',
        ),
        (_body(fecha_entrega=None), 'El campo fecha_entrega es obligatorio'),
        (
            _body(fecha_entrega='19/10/2026'),
            'El campo fecha_entrega debe tener el formato AAAA-MM-DD',
        ),
        ([], 'El cuerpo de la solicitud no es válido'),
    ],
)
def test_post_planillas_bah_rechaza_cuerpo_invalido(body, message):
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/planillas-bah/', body, format='json')
    _authenticate(request)

    response = PlanillaEntregaCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == message
