from contextlib import ExitStack, contextmanager
from unittest.mock import patch

import pytest
from django.db.models import ProtectedError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.movimiento import MovimientoService, MovimientoServiceError
from app_sgbh.views.movimiento_view import MovimientoDetailView


class _DoesNotExist(Exception):
    pass


class _Row:
    def __init__(self, pk=15):
        self.pk = pk
        self.deleted = False

    def delete(self):
        self.deleted = True


@contextmanager
def _patched(*, row=None, linked=False, origen=False):
    with ExitStack() as stack:
        mocks = {
            'atomic': stack.enter_context(
                patch('app_sgbh.services.movimiento.transaction.atomic')
            ),
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
        if row is None:
            row = _Row()
        mocks['row'] = row
        mocks['movimiento'].DoesNotExist = _DoesNotExist
        mocks['movimiento'].objects.get.return_value = row
        mocks['movimiento'].objects.filter.return_value.exists.return_value = origen
        mocks['planilla'].objects.filter.return_value.exists.return_value = linked
        yield mocks


def test_delete_removes_details_and_then_the_movement():
    with _patched() as mocks:
        MovimientoService.delete(15)

    row = mocks['row']
    mocks['atomic'].assert_called_once_with(using='sgbh')
    mocks['movimiento'].objects.get.assert_called_once_with(pk=15)
    mocks['planilla'].objects.filter.assert_called_once_with(movimiento_almacen_id=15)
    mocks['movimiento'].objects.filter.assert_called_once_with(movimiento_origen_id=15)
    mocks['detalle'].objects.filter.assert_called_once_with(movimiento_id=15)
    mocks['detalle'].objects.filter.return_value.delete.assert_called_once_with()
    assert row.deleted is True


def test_delete_rejects_missing_movement():
    with _patched() as mocks:
        mocks['movimiento'].objects.get.side_effect = _DoesNotExist()
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.delete(15)

    assert exc.value.not_found is True
    assert exc.value.message == 'El movimiento de almacén indicado no existe'
    mocks['planilla'].objects.filter.assert_not_called()
    mocks['detalle'].objects.filter.assert_not_called()


def test_delete_rejects_movement_linked_to_planilla():
    with _patched(linked=True) as mocks:
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.delete(15)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar el movimiento de almacén porque '
        'está vinculado a una planilla BAH'
    )
    mocks['detalle'].objects.filter.assert_not_called()
    mocks['movimiento'].objects.filter.assert_not_called()
    assert mocks['row'].deleted is False


def test_delete_rejects_movement_used_as_origin():
    with _patched(origen=True) as mocks:
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.delete(15)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar el movimiento de almacén porque '
        'es origen de otro movimiento'
    )
    mocks['detalle'].objects.filter.assert_not_called()
    assert mocks['row'].deleted is False


def test_delete_maps_protected_error_to_planilla_conflict():
    row = _Row()

    def boom():
        raise ProtectedError('protected', {object()})

    row.delete = boom
    with _patched(row=row) as mocks:
        mocks['planilla'].objects.filter.return_value.exists.side_effect = [
            False,
            True,
        ]
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.delete(15)

    assert exc.value.conflict is True
    assert 'planilla BAH' in exc.value.message


def test_delete_maps_protected_error_to_associated_records():
    row = _Row()

    def boom():
        raise ProtectedError('protected', {object()})

    row.delete = boom
    with _patched(row=row) as mocks:
        with pytest.raises(MovimientoServiceError) as exc:
            MovimientoService.delete(15)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar el movimiento de almacén porque '
        'tiene registros asociados'
    )
    mocks['detalle'].objects.filter.return_value.delete.assert_called_once_with()


def _authenticate(request):
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))


def test_delete_movimientos_returns_no_content():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/movimientos/15/')
    _authenticate(request)

    with patch('app_sgbh.views.movimiento_view.MovimientoService.delete') as delete:
        response = MovimientoDetailView.as_view()(request, movimiento_id=15)

    assert response.status_code == 204
    delete.assert_called_once_with(15)


def test_delete_movimientos_returns_conflict():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/movimientos/15/')
    _authenticate(request)

    with patch(
        'app_sgbh.views.movimiento_view.MovimientoService.delete',
        side_effect=MovimientoServiceError(
            'No se puede eliminar el movimiento de almacén porque '
            'está vinculado a una planilla BAH',
            conflict=True,
        ),
    ):
        response = MovimientoDetailView.as_view()(request, movimiento_id=15)

    assert response.status_code == 409
    assert 'planilla BAH' in response.data['error']


def test_delete_movimientos_returns_not_found():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/movimientos/15/')
    _authenticate(request)

    with patch(
        'app_sgbh.views.movimiento_view.MovimientoService.delete',
        side_effect=MovimientoServiceError(
            'El movimiento de almacén indicado no existe',
            not_found=True,
        ),
    ):
        response = MovimientoDetailView.as_view()(request, movimiento_id=15)

    assert response.status_code == 404
    assert response.data['error'] == 'El movimiento de almacén indicado no existe'


def test_delete_movimientos_hides_unexpected_errors():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/movimientos/15/')
    _authenticate(request)

    with patch(
        'app_sgbh.views.movimiento_view.MovimientoService.delete',
        side_effect=RuntimeError('sql'),
    ):
        response = MovimientoDetailView.as_view()(request, movimiento_id=15)

    assert response.status_code == 500
    assert response.data['error'] == 'No se pudo eliminar el movimiento de almacén'


@pytest.mark.parametrize('movimiento_id', [0, 2147483648])
def test_delete_movimientos_rejects_invalid_id(movimiento_id):
    factory = APIRequestFactory()
    request = factory.delete(f'/api/sgbh/movimientos/{movimiento_id}/')
    _authenticate(request)

    with patch('app_sgbh.views.movimiento_view.MovimientoService.delete') as delete:
        response = MovimientoDetailView.as_view()(
            request,
            movimiento_id=movimiento_id,
        )

    assert response.status_code == 400
    assert response.data['error'] == 'El campo movimiento_id debe ser un número entero'
    delete.assert_not_called()
