from contextlib import ExitStack, contextmanager
from datetime import date, datetime, timezone as dt_timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from django.db import IntegrityError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.movimiento import MovimientoService, MovimientoServiceError
from app_sgbh.views.movimiento_view import MovimientoDetailView

FIXED_NOW = datetime(2026, 10, 16, 18, 59, tzinfo=dt_timezone.utc)
ORIGINAL_CREATED = datetime(2026, 1, 2, tzinfo=dt_timezone.utc)


class _DoesNotExist(Exception):
    pass


class _Row:
    def __init__(self, pk=15):
        self.pk = pk
        self.fecha_creacion = ORIGINAL_CREATED
        self.update_fields = None

    def save(self, update_fields=None):
        self.update_fields = update_fields


@contextmanager
def _patched(*, row=None, tipo=None, bienes=None, origen=None, stored=None, linked=False):
    with ExitStack() as stack:
        mocks = {
            'atomic': stack.enter_context(
                patch('app_sgbh.services.movimiento.transaction.atomic')
            ),
            'now': stack.enter_context(
                patch(
                    'app_sgbh.services.movimiento.timezone.now',
                    return_value=FIXED_NOW,
                )
            ),
            'almacen': stack.enter_context(
                patch('app_sgbh.services.movimiento.Almacen')
            ),
            'tipo': stack.enter_context(
                patch('app_sgbh.services.movimiento.TipoMovimiento')
            ),
            'estado': stack.enter_context(
                patch('app_sgbh.services.movimiento.EstadoMovimiento')
            ),
            'personal': stack.enter_context(
                patch('app_sgbh.services.movimiento.Personal')
            ),
            'bien': stack.enter_context(patch('app_sgbh.services.movimiento.Bien')),
            'movimiento': stack.enter_context(
                patch('app_sgbh.services.movimiento.Movimiento')
            ),
            'detalle': stack.enter_context(
                patch('app_sgbh.services.movimiento.MovimientoDetalle')
            ),
            'planilla': stack.enter_context(
                patch('app_sgbh.services.movimiento.PlanillaEntrega')
            ),
        }
        tipo_row = tipo or SimpleNamespace(
            naturaleza='E',
            requiere_movimiento_origen=False,
            esta_activo=True,
        )
        if row is None:
            row = _Row()
        mocks['row'] = row
        mocks['movimiento'].DoesNotExist = _DoesNotExist
        mocks['movimiento'].objects.get.return_value = row
        mocks['movimiento'].objects.filter.return_value.first.return_value = origen
        mocks['almacen'].objects.filter.return_value.first.return_value = (
            SimpleNamespace(esta_activo=True)
        )
        mocks['tipo'].objects.filter.return_value.first.return_value = tipo_row
        mocks['estado'].objects.filter.return_value.first.return_value = (
            SimpleNamespace(esta_activo=True)
        )
        mocks['personal'].objects.filter.return_value.first.return_value = (
            SimpleNamespace(esta_activo=True, es_encargado_almacen=True)
        )
        if bienes is None:
            bienes = [SimpleNamespace(bien_id=8, esta_activo=True)]
        mocks['bien'].objects.filter.return_value = bienes
        mocks['planilla'].objects.filter.return_value.exists.return_value = linked
        mocks['detalle'].objects.order_by.return_value = Mock(spec=[])
        if stored is None:
            stored = SimpleNamespace(movimiento_id=row.pk, detalles=[])
        mocks['movimiento'].objects.prefetch_related.return_value.get.return_value = (
            stored
        )
        yield mocks


def _line(**overrides):
    data = {
        'bien_id': 8,
        'cantidad': Decimal('3.000000'),
        'cantidad_texto': '3',
        'es_devolvible': False,
        'observacion': 'Caja',
    }
    data.update(overrides)
    return data


def _payload(**overrides):
    data = {
        'almacen_id': 1,
        'tipo_movimiento_id': 2,
        'estado_movimiento_id': 1,
        'movimiento_origen_id': None,
        'fecha_movimiento': datetime(2026, 10, 16, 9, 30),
        'documento_referencia': 'FAC-1',
        'fecha_documento': date(2026, 10, 15),
        'destinatario': 'Municipalidad',
        'observacion': 'Ingreso',
        'fecha_confirmacion': None,
        'encargado_almacen_id': 4,
        'c_usuari_login': 'mmedina',
        'detalles': [_line()],
    }
    data.update(overrides)
    return data


def test_update_replaces_header_and_inserts_new_details():
    stored = SimpleNamespace(movimiento_id=15, detalles=[])
    with _patched(
        stored=stored,
        bienes=[
            SimpleNamespace(bien_id=8, esta_activo=True),
            SimpleNamespace(bien_id=9, esta_activo=True),
        ],
    ) as mocks:
        result = MovimientoService.update(
            15,
            **_payload(
                estado_movimiento_id=2,
                documento_referencia='  FAC-2  ',
                c_usuari_login='  otro  ',
                detalles=[
                    _line(cantidad_texto='   ', observacion='  '),
                    _line(bien_id=9, cantidad=Decimal('1.500000')),
                ],
            ),
        )

    row = mocks['row']
    assert result is stored
    assert row.fecha_creacion == ORIGINAL_CREATED
    assert row.fecha_modificacion == FIXED_NOW
    assert row.c_usuari_login == 'otro'
    assert row.estado_movimiento_id == 2
    assert row.documento_referencia == 'FAC-2'
    assert row.almacen_id == 1
    assert row.encargado_almacen_id == 4
    assert 'fecha_creacion' not in row.update_fields
    assert 'fecha_modificacion' in row.update_fields
    mocks['atomic'].assert_called_once_with(using='sgbh')
    mocks['movimiento'].objects.get.assert_called_once_with(pk=15)
    mocks['planilla'].objects.filter.assert_called_once_with(movimiento_almacen_id=15)
    mocks['detalle'].objects.filter.assert_called_once_with(movimiento_id=15)
    mocks['detalle'].objects.filter.return_value.delete.assert_called_once_with()
    assert mocks['detalle'].call_count == 2
    mocks['detalle'].assert_any_call(
        movimiento_id=15,
        bien_id=8,
        cantidad=Decimal('3.000000'),
        cantidad_texto=None,
        es_devolvible=False,
        observacion=None,
        fecha_creacion=FIXED_NOW,
    )
    mocks['detalle'].assert_any_call(
        movimiento_id=15,
        bien_id=9,
        cantidad=Decimal('1.500000'),
        cantidad_texto='3',
        es_devolvible=False,
        observacion='Caja',
        fecha_creacion=FIXED_NOW,
    )


def test_update_rejects_missing_movement():
    with _patched() as mocks:
        mocks['movimiento'].objects.get.side_effect = _DoesNotExist()
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.update(15, **_payload())

    assert exc.value.not_found is True
    assert exc.value.message == 'El movimiento de almacén indicado no existe'
    mocks['planilla'].objects.filter.assert_not_called()
    mocks['detalle'].objects.filter.assert_not_called()


def test_update_rejects_movement_linked_to_planilla():
    with _patched(linked=True) as mocks:
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.update(15, **_payload())

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede modificar el movimiento de almacén porque '
        'está vinculado a una planilla BAH'
    )
    assert mocks['row'].update_fields is None
    mocks['detalle'].objects.filter.assert_not_called()


def test_update_rejects_origin_equal_to_the_movement():
    with _patched() as mocks:
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.update(15, **_payload(movimiento_origen_id=15))

    assert exc.value.conflict is False
    assert exc.value.message == (
        'El movimiento de origen debe ser distinto de este movimiento'
    )
    assert mocks['row'].update_fields is None
    mocks['detalle'].objects.filter.assert_not_called()


def test_update_rejects_unidentified_user():
    with _patched() as mocks:
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.update(15, **_payload(c_usuari_login='   '))

    assert exc.value.message == 'No se pudo identificar al usuario'
    mocks['atomic'].assert_not_called()


def test_update_rejects_inactive_almacen_before_replacing_details():
    with _patched() as mocks:
        mocks['almacen'].objects.filter.return_value.first.return_value = (
            SimpleNamespace(esta_activo=False)
        )
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.update(15, **_payload())

    assert exc.value.message == 'El almacén indicado no está activo'
    assert mocks['row'].update_fields is None
    mocks['detalle'].objects.filter.assert_not_called()


def test_update_rejects_duplicate_detail_before_delete():
    with _patched() as mocks:
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.update(
                15,
                **_payload(detalles=[_line(), _line()]),
            )

    assert exc.value.conflict is True
    assert 'misma modalidad' in exc.value.message
    mocks['detalle'].objects.filter.assert_not_called()


def test_update_maps_header_integrity_error():
    row = _Row()

    def boom(update_fields=None):
        raise IntegrityError()

    row.save = boom
    with _patched(row=row) as mocks:
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.update(15, **_payload())

    assert exc.value.conflict is False
    assert exc.value.message == 'No se pudo modificar el movimiento de almacén'
    mocks['detalle'].objects.filter.assert_not_called()


def test_update_maps_detail_integrity_error_to_conflict():
    with _patched() as mocks:
        mocks['detalle'].return_value.save.side_effect = IntegrityError()
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.update(15, **_payload())

    assert exc.value.conflict is True
    assert 'misma modalidad' in exc.value.message
    mocks['detalle'].objects.filter.return_value.delete.assert_called_once_with()
    mocks['movimiento'].objects.prefetch_related.assert_not_called()


def _authenticate(request, login='mmedina'):
    force_authenticate(request, user=ExternalUser(login=login, nombre='Mario'))


def _body(**overrides):
    data = {
        'almacen_id': 1,
        'tipo_movimiento_id': 2,
        'estado_movimiento_id': 1,
        'fecha_movimiento': '2026-10-16T09:30:00',
        'documento_referencia': '  FAC-2  ',
        'fecha_documento': '2026-10-15',
        'destinatario': ' Municipalidad ',
        'observacion': ' Ingreso ',
        'encargado_almacen_id': 4,
        'detalles': [
            {
                'bien_id': 8,
                'cantidad': '3',
                'cantidad_texto': ' 3 ',
                'es_devolvible': False,
                'observacion': ' Caja ',
            }
        ],
    }
    data.update(overrides)
    return data


def _stored_movimiento():
    return SimpleNamespace(
        movimiento_id=15,
        almacen_id=1,
        tipo_movimiento_id=2,
        estado_movimiento_id=2,
        movimiento_origen_id=None,
        fecha_movimiento=datetime(2026, 10, 16, 9, 30, tzinfo=dt_timezone.utc),
        documento_referencia='FAC-2',
        fecha_documento=date(2026, 10, 15),
        destinatario='Municipalidad',
        observacion='Ingreso',
        fecha_confirmacion=None,
        encargado_almacen_id=4,
        c_usuari_login='mmedina',
        fecha_creacion=ORIGINAL_CREATED,
        fecha_modificacion=FIXED_NOW,
        detalles=[
            SimpleNamespace(
                movimiento_detalle_id=101,
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


def test_put_movimientos_returns_updated_movement_and_uses_token_login():
    factory = APIRequestFactory()
    request = factory.put(
        '/api/sgbh/movimientos/15/',
        _body(c_usuari_login='intruso'),
        format='json',
    )
    _authenticate(request, login=' mmedina ')
    updated = _stored_movimiento()

    with patch(
        'app_sgbh.views.movimiento_view.MovimientoService.update',
        return_value=updated,
    ) as update:
        response = MovimientoDetailView.as_view()(request, movimiento_id=15)

    assert response.status_code == 200
    kwargs = update.call_args.kwargs
    assert update.call_args.args == (15,)
    assert kwargs['c_usuari_login'] == ' mmedina '
    assert kwargs['documento_referencia'] == 'FAC-2'
    assert kwargs['detalles'][0]['bien_id'] == 8
    assert kwargs['detalles'][0]['cantidad'] == Decimal('3.000000')
    assert response.data['movimiento_id'] == 15
    assert response.data['c_usuari_login'] == 'mmedina'
    assert response.data['fecha_modificacion'] is not None
    assert response.data['detalles'][0]['movimiento_detalle_id'] == 101


def test_put_movimientos_returns_conflict_when_linked_to_planilla():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/movimientos/15/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.movimiento_view.MovimientoService.update',
        side_effect=MovimientoServiceError(
            'No se puede modificar el movimiento de almacén porque '
            'está vinculado a una planilla BAH',
            conflict=True,
        ),
    ):
        response = MovimientoDetailView.as_view()(request, movimiento_id=15)

    assert response.status_code == 409
    assert 'planilla BAH' in response.data['error']


def test_put_movimientos_returns_not_found():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/movimientos/15/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.movimiento_view.MovimientoService.update',
        side_effect=MovimientoServiceError(
            'El movimiento de almacén indicado no existe',
            not_found=True,
        ),
    ):
        response = MovimientoDetailView.as_view()(request, movimiento_id=15)

    assert response.status_code == 404
    assert response.data['error'] == 'El movimiento de almacén indicado no existe'


def test_put_movimientos_hides_unexpected_errors():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/movimientos/15/', _body(), format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.movimiento_view.MovimientoService.update',
        side_effect=RuntimeError('sql'),
    ):
        response = MovimientoDetailView.as_view()(request, movimiento_id=15)

    assert response.status_code == 500
    assert response.data['error'] == 'No se pudo modificar el movimiento de almacén'


@pytest.mark.parametrize(
    ('movimiento_id', 'body', 'message'),
    [
        (0, _body(), 'El campo movimiento_id debe ser un número entero'),
        (2147483648, _body(), 'El campo movimiento_id debe ser un número entero'),
        (15, {}, 'El campo almacen_id es obligatorio'),
        (15, _body(detalles=[]), 'Debe registrar al menos un detalle'),
        (15, [], 'El cuerpo de la solicitud no es válido'),
    ],
)
def test_put_movimientos_rejects_invalid_request(movimiento_id, body, message):
    factory = APIRequestFactory()
    request = factory.put(
        f'/api/sgbh/movimientos/{movimiento_id}/',
        body,
        format='json',
    )
    _authenticate(request)

    with patch('app_sgbh.views.movimiento_view.MovimientoService.update') as update:
        response = MovimientoDetailView.as_view()(
            request,
            movimiento_id=movimiento_id,
        )

    assert response.status_code == 400
    assert response.data['error'] == message
    update.assert_not_called()
