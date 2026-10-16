from unittest.mock import patch

import pytest
from django.db.models import ProtectedError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.bien import BienService, BienServiceError
from app_sgbh.views.bien_view import BienDetailView


class _DoesNotExist(Exception):
    pass


def _patch_delete():
    return (
        patch('app_sgbh.services.bien.transaction.atomic'),
        patch('app_sgbh.services.bien.Bien'),
        patch('app_sgbh.services.bien.MovimientoDetalle'),
        patch('app_sgbh.services.bien.ReglaEntrega'),
    )


def _authenticate(request):
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))


def test_delete_rejects_bien_with_warehouse_movements():
    patches = _patch_delete()
    with patches[0], patches[1] as bien, patches[2] as detalle, patches[3] as regla:
        row = bien.objects.get.return_value
        bien.DoesNotExist = _DoesNotExist
        detalle.objects.filter.return_value.exists.return_value = True

        with pytest.raises(BienServiceError) as exc:
            BienService.delete(4)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar el bien porque tiene movimientos de almacén asociados'
    )
    detalle.objects.filter.assert_called_once_with(bien_id=4)
    regla.objects.filter.assert_not_called()
    row.delete.assert_not_called()


def test_delete_rejects_bien_with_delivery_rules():
    patches = _patch_delete()
    with patches[0], patches[1] as bien, patches[2] as detalle, patches[3] as regla:
        row = bien.objects.get.return_value
        bien.DoesNotExist = _DoesNotExist
        detalle.objects.filter.return_value.exists.return_value = False
        regla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(BienServiceError) as exc:
            BienService.delete(4)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar el bien porque tiene reglas de entrega asociadas'
    )
    regla.objects.filter.assert_called_once_with(bien_id=4)
    row.delete.assert_not_called()


def test_delete_removes_bien_without_references():
    patches = _patch_delete()
    with patches[0], patches[1] as bien, patches[2] as detalle, patches[3] as regla:
        row = bien.objects.get.return_value
        bien.DoesNotExist = _DoesNotExist
        detalle.objects.filter.return_value.exists.return_value = False
        regla.objects.filter.return_value.exists.return_value = False

        BienService.delete(4)

    row.delete.assert_called_once_with()


def test_delete_rejects_missing_bien():
    patches = _patch_delete()
    with patches[0], patches[1] as bien, patches[2] as detalle, patches[3]:
        bien.DoesNotExist = _DoesNotExist
        bien.objects.get.side_effect = _DoesNotExist

        with pytest.raises(BienServiceError) as exc:
            BienService.delete(4)

    assert exc.value.not_found is True
    assert exc.value.message == 'El bien indicado no existe'
    detalle.objects.filter.assert_not_called()


def test_delete_rejects_when_database_protects_related_movement():
    patches = _patch_delete()
    with patches[0], patches[1] as bien, patches[2] as detalle, patches[3] as regla:
        row = bien.objects.get.return_value
        bien.DoesNotExist = _DoesNotExist
        detalle.objects.filter.return_value.exists.side_effect = [False, True]
        regla.objects.filter.return_value.exists.return_value = False
        row.delete.side_effect = ProtectedError('protected', {object()})

        with pytest.raises(BienServiceError) as exc:
            BienService.delete(4)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar el bien porque tiene movimientos de almacén asociados'
    )


def test_delete_bienes_returns_no_content():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/bienes/4/')
    _authenticate(request)

    with patch('app_sgbh.views.bien_view.BienService.delete') as delete:
        response = BienDetailView.as_view()(request, bien_id=4)

    assert response.status_code == 204
    assert response.data is None
    delete.assert_called_once_with(4)


def test_delete_bienes_returns_conflict_when_movements_exist():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/bienes/4/')
    _authenticate(request)

    with patch(
        'app_sgbh.views.bien_view.BienService.delete',
        side_effect=BienServiceError(
            'No se puede eliminar el bien porque tiene movimientos de almacén asociados',
            conflict=True,
        ),
    ):
        response = BienDetailView.as_view()(request, bien_id=4)

    assert response.status_code == 409
    assert response.data['error'] == (
        'No se puede eliminar el bien porque tiene movimientos de almacén asociados'
    )


def test_delete_bienes_returns_not_found():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/bienes/4/')
    _authenticate(request)

    with patch(
        'app_sgbh.views.bien_view.BienService.delete',
        side_effect=BienServiceError(
            'El bien indicado no existe',
            not_found=True,
        ),
    ):
        response = BienDetailView.as_view()(request, bien_id=4)

    assert response.status_code == 404
    assert response.data['error'] == 'El bien indicado no existe'


def test_delete_bienes_rejects_invalid_id():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/bienes/0/')
    _authenticate(request)

    with patch('app_sgbh.views.bien_view.BienService.delete') as delete:
        response = BienDetailView.as_view()(request, bien_id=0)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo bien_id debe ser un número entero'
    delete.assert_not_called()
