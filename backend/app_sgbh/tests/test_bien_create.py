from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.db import IntegrityError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.bien import BienService, BienServiceError
from app_sgbh.views.bien_view import BienCreateView


def _patch_create():
    return (
        patch('app_sgbh.services.bien.transaction.atomic'),
        patch('app_sgbh.services.bien.Bien'),
        patch('app_sgbh.services.bien.CategoriaBien'),
        patch('app_sgbh.services.bien.UnidadMedida'),
    )


def _stored_bien():
    return SimpleNamespace(
        bien_id=9,
        categoria_bien_id=1,
        unidad_medida_id=3,
        codigo='CLAV-02',
        nombre='Clavos',
        descripcion=None,
        orden_impresion=8,
        esta_activo=True,
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


def _prepare(bien, categoria, unidad, max_orden=7):
    categoria.objects.filter.return_value.exists.return_value = True
    unidad.objects.filter.return_value.exists.return_value = True
    bien.objects.filter.return_value.exists.return_value = False
    bien.objects.aggregate.return_value = {'max_orden': max_orden}
    bien.return_value.pk = 9
    stored = _stored_bien()
    bien.objects.select_related.return_value.get.return_value = stored
    return stored


def test_create_sets_null_description_and_next_print_order():
    patches = _patch_create()
    with patches[0], patches[1] as bien, patches[2] as categoria, patches[3] as unidad:
        stored = _prepare(bien, categoria, unidad, max_orden=7)

        result = BienService.create(
            categoria_bien_id=1,
            unidad_medida_id=3,
            codigo='  CLAV-02  ',
            nombre='  Clavos  ',
            esta_activo=True,
            visible_planilla=False,
        )

    assert result is stored
    bien.assert_called_once_with(
        categoria_bien_id=1,
        unidad_medida_id=3,
        codigo='CLAV-02',
        nombre='Clavos',
        descripcion=None,
        orden_impresion=8,
        esta_activo=True,
        visible_planilla=False,
    )
    bien.return_value.save.assert_called_once_with()
    bien.objects.filter.assert_called_once_with(codigo='CLAV-02')
    bien.objects.select_related.assert_called_once_with(
        'categoria_bien',
        'unidad_medida',
    )


def test_create_uses_one_when_print_order_is_missing():
    patches = _patch_create()
    with patches[0], patches[1] as bien, patches[2] as categoria, patches[3] as unidad:
        _prepare(bien, categoria, unidad, max_orden=None)

        BienService.create(
            categoria_bien_id=1,
            unidad_medida_id=3,
            codigo='CLAV-02',
            nombre='Clavos',
            esta_activo=True,
            visible_planilla=True,
        )

    assert bien.call_args.kwargs['orden_impresion'] == 1
    assert bien.call_args.kwargs['descripcion'] is None


def test_create_rejects_duplicate_codigo_before_insert():
    patches = _patch_create()
    with patches[0], patches[1] as bien, patches[2] as categoria, patches[3] as unidad:
        _prepare(bien, categoria, unidad)
        bien.objects.filter.return_value.exists.return_value = True

        with pytest.raises(BienServiceError) as exc:
            BienService.create(
                categoria_bien_id=1,
                unidad_medida_id=3,
                codigo='CLAV-02',
                nombre='Clavos',
                esta_activo=True,
                visible_planilla=True,
            )

    assert exc.value.conflict is True
    assert exc.value.message == 'Ya existe un bien con el código indicado'
    bien.objects.aggregate.assert_not_called()
    bien.assert_not_called()


def test_create_maps_integrity_error_to_duplicate_codigo():
    patches = _patch_create()
    with patches[0], patches[1] as bien, patches[2] as categoria, patches[3] as unidad:
        _prepare(bien, categoria, unidad)
        bien.return_value.save.side_effect = IntegrityError

        with pytest.raises(BienServiceError) as exc:
            BienService.create(
                categoria_bien_id=1,
                unidad_medida_id=3,
                codigo='CLAV-02',
                nombre='Clavos',
                esta_activo=True,
                visible_planilla=True,
            )

    assert exc.value.conflict is True
    assert exc.value.message == 'Ya existe un bien con el código indicado'
    bien.objects.select_related.assert_not_called()


def test_create_rejects_print_order_above_smallint():
    patches = _patch_create()
    with patches[0], patches[1] as bien, patches[2] as categoria, patches[3] as unidad:
        _prepare(bien, categoria, unidad, max_orden=32767)

        with pytest.raises(BienServiceError) as exc:
            BienService.create(
                categoria_bien_id=1,
                unidad_medida_id=3,
                codigo='CLAV-02',
                nombre='Clavos',
                esta_activo=True,
                visible_planilla=True,
            )

    assert exc.value.message == 'No se pudo calcular el orden de impresión del bien'
    bien.assert_not_called()


def test_create_rejects_missing_category():
    patches = _patch_create()
    with patches[0], patches[1] as bien, patches[2] as categoria, patches[3] as unidad:
        _prepare(bien, categoria, unidad)
        categoria.objects.filter.return_value.exists.return_value = False

        with pytest.raises(BienServiceError) as exc:
            BienService.create(
                categoria_bien_id=9,
                unidad_medida_id=3,
                codigo='CLAV-02',
                nombre='Clavos',
                esta_activo=True,
                visible_planilla=True,
            )

    assert exc.value.message == 'La categoría de bien indicada no existe'
    unidad.objects.filter.assert_not_called()
    bien.assert_not_called()


def test_post_bienes_returns_search_shape():
    factory = APIRequestFactory()
    request = factory.post(
        '/api/sgbh/bienes/',
        {
            'categoria_bien_id': 1,
            'unidad_medida_id': 3,
            'codigo': '  CLAV-02  ',
            'nombre': '  Clavos  ',
            'esta_activo': True,
            'visible_planilla': False,
            'descripcion': 'No se guarda',
            'orden_impresion': 99,
        },
        format='json',
    )
    _authenticate(request)
    created = _stored_bien()

    with patch(
        'app_sgbh.views.bien_view.BienService.create',
        return_value=created,
    ) as create:
        response = BienCreateView.as_view()(request)

    assert response.status_code == 201
    create.assert_called_once_with(
        categoria_bien_id=1,
        unidad_medida_id=3,
        codigo='CLAV-02',
        nombre='Clavos',
        esta_activo=True,
        visible_planilla=False,
    )
    assert response.data['bien_id'] == 9
    assert response.data['descripcion'] is None
    assert response.data['orden_impresion'] == 8
    assert response.data['categoria_bien_nombre'] == 'Herramientas'
    assert response.data['unidad_medida_nombre'] == 'Unidad'


def test_post_bienes_returns_conflict_for_duplicate_codigo():
    factory = APIRequestFactory()
    request = factory.post(
        '/api/sgbh/bienes/',
        {
            'categoria_bien_id': 1,
            'unidad_medida_id': 3,
            'codigo': 'CLAV-02',
            'nombre': 'Clavos',
            'esta_activo': True,
            'visible_planilla': True,
        },
        format='json',
    )
    _authenticate(request)

    with patch(
        'app_sgbh.views.bien_view.BienService.create',
        side_effect=BienServiceError(
            'Ya existe un bien con el código indicado',
            conflict=True,
        ),
    ):
        response = BienCreateView.as_view()(request)

    assert response.status_code == 409
    assert response.data['error'] == 'Ya existe un bien con el código indicado'


@pytest.mark.parametrize(
    ('body', 'message'),
    [
        ({}, 'El campo categoria_bien_id es obligatorio'),
        (
            {
                'categoria_bien_id': 1,
                'unidad_medida_id': 3,
                'codigo': '   ',
                'nombre': 'Clavos',
                'esta_activo': True,
                'visible_planilla': True,
            },
            'El campo codigo es obligatorio',
        ),
        (
            {
                'categoria_bien_id': 1,
                'unidad_medida_id': 3,
                'codigo': 'C' * 51,
                'nombre': 'Clavos',
                'esta_activo': True,
                'visible_planilla': True,
            },
            'El campo codigo no debe superar 50 caracteres',
        ),
        (
            {
                'categoria_bien_id': 1,
                'unidad_medida_id': 3,
                'codigo': 'CLAV-02',
                'nombre': '   ',
                'esta_activo': True,
                'visible_planilla': True,
            },
            'El campo nombre es obligatorio',
        ),
        (
            {
                'categoria_bien_id': 1,
                'unidad_medida_id': 3,
                'codigo': 'CLAV-02',
                'nombre': 'Clavos',
                'esta_activo': None,
                'visible_planilla': True,
            },
            'El campo esta_activo es obligatorio',
        ),
        (
            {
                'categoria_bien_id': 1,
                'unidad_medida_id': 3,
                'codigo': 'CLAV-02',
                'nombre': 'Clavos',
                'esta_activo': True,
                'visible_planilla': 'x',
            },
            'El campo visible_planilla debe ser 1, 0, true o false',
        ),
        ([], 'El cuerpo de la solicitud no es válido'),
    ],
)
def test_post_bienes_rejects_invalid_body(body, message):
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/bienes/', body, format='json')
    _authenticate(request)

    with patch('app_sgbh.views.bien_view.BienService.create') as create:
        response = BienCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == message
    create.assert_not_called()
