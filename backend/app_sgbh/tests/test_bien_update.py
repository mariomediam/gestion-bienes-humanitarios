from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.bien import BienService, BienServiceError
from app_sgbh.views.bien_view import BienDetailView


class _DoesNotExist(Exception):
    pass


class _Row:
    def __init__(self):
        self.pk = 4
        self.bien_id = 4
        self.categoria_bien_id = 1
        self.unidad_medida_id = 1
        self.codigo = 'CLAV-01'
        self.nombre = 'Clavos'
        self.descripcion = 'Texto'
        self.orden_impresion = 5
        self.esta_activo = True
        self.visible_planilla = True
        self.saved_fields = None

    def save(self, update_fields=None):
        self.saved_fields = update_fields


def _patch_update():
    return (
        patch('app_sgbh.services.bien.transaction.atomic'),
        patch('app_sgbh.services.bien.Bien'),
        patch('app_sgbh.services.bien.CategoriaBien'),
        patch('app_sgbh.services.bien.UnidadMedida'),
    )


def _stored_bien():
    return SimpleNamespace(
        bien_id=4,
        categoria_bien_id=2,
        unidad_medida_id=3,
        codigo='CLAV-01',
        nombre='Pala',
        descripcion=None,
        orden_impresion=None,
        esta_activo=False,
        visible_planilla=False,
        categoria_bien=SimpleNamespace(codigo='HERR', nombre='Herramientas'),
        unidad_medida=SimpleNamespace(
            codigo='UND',
            nombre='Unidad',
            abreviatura='und',
        ),
    )


def _authenticate(request):
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))


def test_update_changes_only_sent_fields():
    patches = _patch_update()
    with patches[0], patches[1] as bien, patches[2] as categoria, patches[3] as unidad:
        row = _Row()
        bien.DoesNotExist = _DoesNotExist
        bien.objects.get.return_value = row
        stored = _stored_bien()
        bien.objects.select_related.return_value.get.return_value = stored
        categoria.objects.filter.return_value.exists.return_value = True

        result = BienService.update(
            4,
            nombre='  Pala  ',
            categoria_bien_id=2,
            esta_activo=False,
        )

    assert result is stored
    assert row.saved_fields == ['categoria_bien_id', 'nombre', 'esta_activo']
    assert row.categoria_bien_id == 2
    assert row.nombre == 'Pala'
    assert row.esta_activo is False
    assert row.codigo == 'CLAV-01'
    assert row.unidad_medida_id == 1
    assert row.descripcion == 'Texto'
    assert row.orden_impresion == 5
    assert row.visible_planilla is True
    categoria.objects.filter.assert_called_once_with(pk=2)
    unidad.objects.filter.assert_not_called()
    bien.objects.select_related.assert_called_once_with(
        'categoria_bien',
        'unidad_medida',
    )


def test_update_accepts_inactive_category_and_unit():
    patches = _patch_update()
    with patches[0], patches[1] as bien, patches[2] as categoria, patches[3] as unidad:
        row = _Row()
        bien.DoesNotExist = _DoesNotExist
        bien.objects.get.return_value = row
        bien.objects.select_related.return_value.get.return_value = _stored_bien()
        categoria.objects.filter.return_value.exists.return_value = True
        unidad.objects.filter.return_value.exists.return_value = True

        BienService.update(4, categoria_bien_id=2, unidad_medida_id=3)

    categoria.objects.filter.assert_called_once_with(pk=2)
    unidad.objects.filter.assert_called_once_with(pk=3)
    assert row.saved_fields == ['categoria_bien_id', 'unidad_medida_id']
    assert row.categoria_bien_id == 2
    assert row.unidad_medida_id == 3


def test_update_clears_nullable_fields_when_sent_empty():
    patches = _patch_update()
    with patches[0], patches[1] as bien, patches[2], patches[3]:
        row = _Row()
        bien.DoesNotExist = _DoesNotExist
        bien.objects.get.return_value = row
        bien.objects.select_related.return_value.get.return_value = _stored_bien()

        BienService.update(4, descripcion='   ', orden_impresion=None)

    assert row.descripcion is None
    assert row.orden_impresion is None
    assert row.saved_fields == ['descripcion', 'orden_impresion']


def test_update_without_fields_does_not_save():
    patches = _patch_update()
    with patches[0], patches[1] as bien, patches[2] as categoria, patches[3] as unidad:
        row = _Row()
        bien.DoesNotExist = _DoesNotExist
        bien.objects.get.return_value = row
        stored = _stored_bien()
        bien.objects.select_related.return_value.get.return_value = stored

        result = BienService.update(4)

    assert result is stored
    assert row.saved_fields is None
    assert row.nombre == 'Clavos'
    categoria.objects.filter.assert_not_called()
    unidad.objects.filter.assert_not_called()


def test_update_rejects_codigo():
    with pytest.raises(BienServiceError) as exc:
        BienService.update(4, codigo='OTRO', nombre='Pala')

    assert exc.value.not_found is False
    assert exc.value.message == 'El campo codigo no se puede modificar'


def test_update_rejects_missing_bien():
    patches = _patch_update()
    with patches[0], patches[1] as bien, patches[2], patches[3]:
        bien.DoesNotExist = _DoesNotExist
        bien.objects.get.side_effect = _DoesNotExist

        with pytest.raises(BienServiceError) as exc:
            BienService.update(4, nombre='Pala')

    assert exc.value.not_found is True
    assert exc.value.message == 'El bien indicado no existe'
    bien.objects.select_related.assert_not_called()


@pytest.mark.parametrize(
    ('changes', 'message', 'model_name'),
    [
        (
            {'categoria_bien_id': 9},
            'La categoría de bien indicada no existe',
            'categoria',
        ),
        (
            {'unidad_medida_id': 9},
            'La unidad de medida indicada no existe',
            'unidad',
        ),
    ],
)
def test_update_rejects_missing_foreign_key(changes, message, model_name):
    patches = _patch_update()
    with patches[0], patches[1] as bien, patches[2] as categoria, patches[3] as unidad:
        row = _Row()
        bien.DoesNotExist = _DoesNotExist
        bien.objects.get.return_value = row
        categoria.objects.filter.return_value.exists.return_value = False
        unidad.objects.filter.return_value.exists.return_value = False

        with pytest.raises(BienServiceError) as exc:
            BienService.update(4, **changes)

    assert exc.value.message == message
    assert row.saved_fields is None
    bien.objects.select_related.assert_not_called()
    if model_name == 'categoria':
        unidad.objects.filter.assert_not_called()
    else:
        categoria.objects.filter.assert_not_called()


def test_patch_bienes_returns_search_shape_for_sent_fields():
    factory = APIRequestFactory()
    request = factory.patch(
        '/api/sgbh/bienes/4/',
        {'nombre': '  Pala  ', 'visible_planilla': False},
        format='json',
    )
    _authenticate(request)
    updated = _stored_bien()

    with patch(
        'app_sgbh.views.bien_view.BienService.update',
        return_value=updated,
    ) as update:
        response = BienDetailView.as_view()(request, bien_id=4)

    assert response.status_code == 200
    update.assert_called_once_with(4, nombre='Pala', visible_planilla=False)
    assert response.data == {
        'bien_id': 4,
        'categoria_bien_id': 2,
        'unidad_medida_id': 3,
        'codigo': 'CLAV-01',
        'nombre': 'Pala',
        'descripcion': None,
        'orden_impresion': None,
        'esta_activo': False,
        'visible_planilla': False,
        'categoria_bien_codigo': 'HERR',
        'categoria_bien_nombre': 'Herramientas',
        'unidad_medida_codigo': 'UND',
        'unidad_medida_nombre': 'Unidad',
        'unidad_medida_abreviatura': 'und',
    }


def test_patch_bienes_rejects_codigo():
    factory = APIRequestFactory()
    request = factory.patch(
        '/api/sgbh/bienes/4/',
        {'codigo': 'OTRO', 'nombre': 'Pala'},
        format='json',
    )
    _authenticate(request)

    with patch('app_sgbh.views.bien_view.BienService.update') as update:
        response = BienDetailView.as_view()(request, bien_id=4)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo codigo no se puede modificar'
    update.assert_not_called()


def test_patch_bienes_returns_not_found():
    factory = APIRequestFactory()
    request = factory.patch('/api/sgbh/bienes/4/', {'nombre': 'Pala'}, format='json')
    _authenticate(request)

    with patch(
        'app_sgbh.views.bien_view.BienService.update',
        side_effect=BienServiceError(
            'El bien indicado no existe',
            not_found=True,
        ),
    ):
        response = BienDetailView.as_view()(request, bien_id=4)

    assert response.status_code == 404
    assert response.data['error'] == 'El bien indicado no existe'


def test_patch_bienes_returns_bad_request_for_invalid_id():
    factory = APIRequestFactory()
    request = factory.patch('/api/sgbh/bienes/0/', {'nombre': 'Pala'}, format='json')
    _authenticate(request)

    response = BienDetailView.as_view()(request, bien_id=0)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo bien_id debe ser un número entero'


@pytest.mark.parametrize(
    ('body', 'message'),
    [
        ({'nombre': '   '}, 'El campo nombre es obligatorio'),
        ({'nombre': 'N' * 251}, 'El campo nombre no debe superar 250 caracteres'),
        ({'orden_impresion': 0}, 'El campo orden_impresion debe ser mayor que 0'),
        (
            {'orden_impresion': 40000},
            'El campo orden_impresion debe ser un número entero',
        ),
        ({'categoria_bien_id': None}, 'El campo categoria_bien_id es obligatorio'),
        ({'esta_activo': None}, 'El campo esta_activo es obligatorio'),
        (
            {'visible_planilla': 'x'},
            'El campo visible_planilla debe ser 1, 0, true o false',
        ),
        ({'descripcion': 'D' * 501}, 'El campo descripcion no debe superar 500 caracteres'),
        ([], 'El cuerpo de la solicitud no es válido'),
    ],
)
def test_patch_bienes_rejects_invalid_body(body, message):
    factory = APIRequestFactory()
    request = factory.patch('/api/sgbh/bienes/4/', body, format='json')
    _authenticate(request)

    response = BienDetailView.as_view()(request, bien_id=4)

    assert response.status_code == 400
    assert response.data['error'] == message
