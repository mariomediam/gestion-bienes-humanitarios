from contextlib import ExitStack, contextmanager
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.movimiento import MovimientoServiceError
from app_sgbh.services.planilla_entrega import (
    PlanillaEntregaService,
    PlanillaEntregaServiceError,
)
from app_sgbh.views.planilla_entrega_view import PlanillaEntregaDetailView


class _DoesNotExist(Exception):
    pass


class _Row:
    def __init__(self, *, movimiento_almacen_id=15):
        self.pk = 21
        self.movimiento_almacen_id = movimiento_almacen_id
        self.deleted = False

    def delete(self):
        self.deleted = True


@contextmanager
def _patched(*, row=None):
    with ExitStack() as stack:
        mocks = {
            'atomic': stack.enter_context(
                patch('app_sgbh.services.planilla_entrega.transaction.atomic')
            ),
            'planilla': stack.enter_context(
                patch('app_sgbh.services.planilla_entrega.PlanillaEntrega')
            ),
            'movimiento': stack.enter_context(
                patch('app_sgbh.services.planilla_entrega.MovimientoService')
            ),
        }
        mocks['planilla'].DoesNotExist = _DoesNotExist
        if row is None:
            row = _Row()
        mocks['row'] = row
        mocks['planilla'].objects.get.return_value = row
        yield mocks


def test_delete_elimina_la_planilla_y_luego_el_movimiento():
    with _patched() as mocks:
        PlanillaEntregaService.delete(21)

    mocks['planilla'].objects.get.assert_called_once_with(pk=21)
    assert mocks['row'].deleted is True
    mocks['movimiento'].delete.assert_called_once_with(15)
    mocks['atomic'].assert_called_once_with(using='sgbh')


def test_delete_sin_movimiento_solo_elimina_la_planilla():
    with _patched(row=_Row(movimiento_almacen_id=None)) as mocks:
        PlanillaEntregaService.delete(21)

    assert mocks['row'].deleted is True
    mocks['movimiento'].delete.assert_not_called()


def test_delete_rechaza_planilla_inexistente():
    with _patched() as mocks:
        mocks['planilla'].objects.get.side_effect = _DoesNotExist()
        with pytest.raises(PlanillaEntregaServiceError) as exc:
            PlanillaEntregaService.delete(21)

    assert exc.value.not_found is True
    assert exc.value.message == 'La planilla BAH indicada no existe'
    assert mocks['row'].deleted is False
    mocks['movimiento'].delete.assert_not_called()


def test_delete_propaga_el_rechazo_si_el_movimiento_es_origen():
    with _patched() as mocks:
        mocks['movimiento'].delete.side_effect = MovimientoServiceError(
            'No se puede eliminar el movimiento de almacén porque '
            'es origen de otro movimiento',
            conflict=True,
        )
        with pytest.raises(MovimientoServiceError) as exc:
            PlanillaEntregaService.delete(21)

    assert exc.value.conflict is True
    assert 'es origen de otro movimiento' in exc.value.message
    mocks['movimiento'].delete.assert_called_once_with(15)


def _authenticate(request):
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))


def test_delete_planillas_bah_responde_sin_contenido():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/planillas-bah/21/')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.delete'
    ) as delete:
        response = PlanillaEntregaDetailView.as_view()(
            request,
            planilla_entrega_id=21,
        )

    assert response.status_code == 204
    delete.assert_called_once_with(21)


def test_delete_planillas_bah_devuelve_no_encontrado():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/planillas-bah/21/')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.delete',
        side_effect=PlanillaEntregaServiceError(
            'La planilla BAH indicada no existe',
            not_found=True,
        ),
    ):
        response = PlanillaEntregaDetailView.as_view()(
            request,
            planilla_entrega_id=21,
        )

    assert response.status_code == 404
    assert response.data['error'] == 'La planilla BAH indicada no existe'


def test_delete_planillas_bah_devuelve_conflicto_si_el_movimiento_es_origen():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/planillas-bah/21/')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.delete',
        side_effect=MovimientoServiceError(
            'No se puede eliminar el movimiento de almacén porque '
            'es origen de otro movimiento',
            conflict=True,
        ),
    ):
        response = PlanillaEntregaDetailView.as_view()(
            request,
            planilla_entrega_id=21,
        )

    assert response.status_code == 409
    assert response.data['error'] == (
        'No se puede eliminar el movimiento de almacén porque '
        'es origen de otro movimiento'
    )


def test_delete_planillas_bah_oculta_errores_inesperados():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/planillas-bah/21/')
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.PlanillaEntregaService.delete',
        side_effect=RuntimeError('sql'),
    ):
        response = PlanillaEntregaDetailView.as_view()(
            request,
            planilla_entrega_id=21,
        )

    assert response.status_code == 500
    assert response.data['error'] == 'No se pudo eliminar la planilla BAH'


@pytest.mark.parametrize('planilla_entrega_id', [0, 2147483648])
def test_delete_planillas_bah_rechaza_id_invalido(planilla_entrega_id):
    factory = APIRequestFactory()
    request = factory.delete(f'/api/sgbh/planillas-bah/{planilla_entrega_id}/')
    _authenticate(request)

    response = PlanillaEntregaDetailView.as_view()(
        request,
        planilla_entrega_id=planilla_entrega_id,
    )

    assert response.status_code == 400
    assert response.data['error'] == (
        'El campo planilla_entrega_id debe ser un número entero'
    )
