from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers import first_error_message
from app_sgbh.serializers.formulario_2a_vivienda import ViviendaCreateSerializer
from app_sgbh.services.formulario_2a_vivienda import (
    Formulario2AViviendaService,
    Formulario2AViviendaServiceError,
)
from app_sgbh.views.formulario_2a_vivienda_view import Formulario2AViviendaCreateView


class _DoesNotExist(Exception):
    pass


def _parse_crear(data):
    serializer = ViviendaCreateSerializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data, None
    return None, first_error_message(serializer.errors)


def _body(**overrides):
    data = {
        'formulario_2a_id': 10,
        'numero_lote': 'L-1',
        'tipo_uso_instalacion_id': 2,
    }
    data.update(overrides)
    return data


def _create_kwargs(**overrides):
    data = {
        'formulario_2a_id': 10,
        'numero_lote': 'L-1',
        'tipo_uso_instalacion_id': 2,
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


def test_parse_crear_accepts_required_fields_and_null_optionals():
    parsed, error = _parse_crear(_body())

    assert error is None
    assert parsed['formulario_2a_id'] == 10
    assert 'numero_orden' not in parsed
    assert parsed['numero_lote'] == 'L-1'
    assert parsed['tenencia_propia'] is None
    assert parsed['tipo_uso_instalacion_id'] == 2
    assert parsed['condicion_vivienda_id'] is None
    assert parsed['material_techo_id'] is None
    assert parsed['material_pared_id'] is None
    assert parsed['material_piso_id'] is None


def test_parse_crear_trims_lote_and_reads_optional_fields():
    parsed, error = _parse_crear(
        _body(
            numero_lote='  L-12  ',
            tenencia_propia='1',
            condicion_vivienda_id=3,
            material_techo_id=4,
            material_pared_id=5,
            material_piso_id=6,
        )
    )

    assert error is None
    assert parsed['numero_lote'] == 'L-12'
    assert parsed['tenencia_propia'] is True
    assert parsed['condicion_vivienda_id'] == 3
    assert parsed['material_techo_id'] == 4
    assert parsed['material_pared_id'] == 5
    assert parsed['material_piso_id'] == 6


def test_parse_crear_stores_blank_tenencia_as_null():
    parsed, error = _parse_crear(_body(tenencia_propia='', condicion_vivienda_id=None))

    assert error is None
    assert parsed['tenencia_propia'] is None
    assert parsed['condicion_vivienda_id'] is None


@pytest.mark.parametrize(
    ('field', 'value', 'message'),
    [
        ('formulario_2a_id', None, 'formulario_2a_id es obligatorio'),
        ('formulario_2a_id', '10.5', 'formulario_2a_id debe ser un número entero'),
        ('numero_lote', None, 'numero_lote es obligatorio'),
        ('numero_lote', '   ', 'numero_lote es obligatorio'),
        ('numero_lote', 'a' * 51, 'numero_lote no debe superar 50'),
        ('tenencia_propia', 'si', 'tenencia_propia debe ser 1, 0, true o false'),
        ('tipo_uso_instalacion_id', None, 'tipo_uso_instalacion_id es obligatorio'),
        (
            'condicion_vivienda_id',
            'x',
            'condicion_vivienda_id debe ser un número entero',
        ),
        ('material_techo_id', '4.2', 'material_techo_id debe ser un número entero'),
        ('material_pared_id', True, 'material_pared_id debe ser un número entero'),
        ('material_piso_id', 'y', 'material_piso_id debe ser un número entero'),
    ],
)
def test_parse_crear_rejects_invalid_fields(field, value, message):
    _parsed, error = _parse_crear(_body(**{field: value}))

    assert error is not None
    assert message in error


def test_create_rejects_blank_numero_lote():
    with pytest.raises(Formulario2AViviendaServiceError) as exc:
        Formulario2AViviendaService.create(**_create_kwargs(numero_lote='   '))

    assert exc.value.message == 'El campo numero_lote es obligatorio'


def test_create_rejects_unknown_formulario():
    with (
        patch('app_sgbh.services.formulario_2a_vivienda.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a_vivienda.Formulario2A') as formulario,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'
        ) as vivienda,
    ):
        formulario.DoesNotExist = _DoesNotExist
        formulario.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.create(**_create_kwargs())

    assert exc.value.not_found is True
    assert exc.value.message == 'El formulario EDAN 2A indicado no existe'
    vivienda.assert_not_called()


def test_create_rejects_inactive_formulario():
    with (
        patch('app_sgbh.services.formulario_2a_vivienda.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a_vivienda.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'
        ) as vivienda,
    ):
        _formulario_existente(formulario, estado_registro_id=2)

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.create(**_create_kwargs())

    assert exc.value.conflict is True
    assert 'estado de registro es inactivo' in exc.value.message
    planilla.objects.filter.assert_not_called()
    vivienda.assert_not_called()


def test_create_rejects_planilla_emitida():
    with (
        patch('app_sgbh.services.formulario_2a_vivienda.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a_vivienda.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'
        ) as vivienda,
    ):
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.create(**_create_kwargs())

    assert exc.value.conflict is True
    assert 'planilla BAH emitida y activa' in exc.value.message
    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=10,
        estado_planilla__codigo='EMITIDA',
    )
    vivienda.assert_not_called()


def test_create_rejects_unknown_tipo_uso():
    with (
        patch('app_sgbh.services.formulario_2a_vivienda.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a_vivienda.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.TipoUsoInstalacion'
        ) as tipo_uso,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'
        ) as vivienda,
    ):
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        tipo_uso.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.create(**_create_kwargs())

    assert exc.value.message == 'El tipo de uso de instalación indicado no existe'
    vivienda.assert_not_called()


def test_create_rejects_unknown_optional_catalog():
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
        patch(
            'app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'
        ) as vivienda,
    ):
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        tipo_uso.objects.filter.return_value.exists.return_value = True
        condicion.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.create(
                **_create_kwargs(condicion_vivienda_id=3)
            )

    assert exc.value.message == 'La condición de vivienda indicada no existe'
    condicion.objects.filter.assert_called_once_with(pk=3)
    vivienda.assert_not_called()


def test_create_rejects_when_numero_orden_reaches_the_column_limit():
    with (
        patch('app_sgbh.services.formulario_2a_vivienda.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a_vivienda.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.TipoUsoInstalacion'
        ) as tipo_uso,
        patch(
            'app_sgbh.services.formulario_2a_vivienda.Formulario2AVivienda'
        ) as vivienda,
    ):
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        tipo_uso.objects.filter.return_value.exists.return_value = True
        vivienda.objects.filter.return_value.aggregate.return_value = {'maximo': 32767}

        with pytest.raises(Formulario2AViviendaServiceError) as exc:
            Formulario2AViviendaService.create(**_create_kwargs())

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede asignar otro número de orden en el formulario EDAN 2A'
    )
    vivienda.objects.filter.assert_called_once_with(formulario_2a_id=10)
    vivienda.assert_not_called()


def test_create_saves_when_references_exist():
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
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        tipo_uso.objects.filter.return_value.exists.return_value = True
        condicion.objects.filter.return_value.exists.return_value = True
        techo.objects.filter.return_value.exists.return_value = True
        pared.objects.filter.return_value.exists.return_value = True
        piso.objects.filter.return_value.exists.return_value = True
        vivienda.objects.filter.return_value.aggregate.return_value = {'maximo': 4}
        vivienda.return_value.pk = 21
        stored = vivienda.objects.select_related.return_value.get.return_value

        result = Formulario2AViviendaService.create(
            **_create_kwargs(
                numero_lote='  L-1  ',
                tenencia_propia=False,
                condicion_vivienda_id=3,
                material_techo_id=4,
                material_pared_id=5,
                material_piso_id=6,
            )
        )

    assert result is stored
    vivienda.assert_called_once_with(
        formulario_2a_id=10,
        numero_orden=5,
        numero_lote='L-1',
        tenencia_propia=False,
        tipo_uso_instalacion_id=2,
        condicion_vivienda_id=3,
        material_techo_id=4,
        material_pared_id=5,
        material_piso_id=6,
    )
    vivienda.return_value.save.assert_called_once_with()
    vivienda.objects.select_related.assert_called_once_with(
        'tipo_uso_instalacion',
        'condicion_vivienda',
        'material_techo',
        'material_pared',
        'material_piso',
    )
    vivienda.objects.select_related.return_value.get.assert_called_once_with(pk=21)


def test_create_skips_optional_catalogs_when_they_are_null():
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
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        tipo_uso.objects.filter.return_value.exists.return_value = True
        vivienda.objects.filter.return_value.aggregate.return_value = {'maximo': None}
        vivienda.return_value.pk = 21

        Formulario2AViviendaService.create(**_create_kwargs())

    assert vivienda.call_args.kwargs['numero_orden'] == 1
    condicion.objects.filter.assert_not_called()
    techo.objects.filter.assert_not_called()
    pared.objects.filter.assert_not_called()
    piso.objects.filter.assert_not_called()


def test_post_viviendas_returns_not_found_when_formulario_is_missing():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/viviendas/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.create',
        side_effect=Formulario2AViviendaServiceError(
            'El formulario EDAN 2A indicado no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AViviendaCreateView.as_view()(request)

    assert response.status_code == 404
    assert response.data['error'] == 'El formulario EDAN 2A indicado no existe'


def test_post_viviendas_rejects_numero_orden_from_the_client():
    factory = APIRequestFactory()
    request = factory.post(
        '/api/sgbh/viviendas/',
        _body(numero_orden=3),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.create',
    ) as create:
        response = Formulario2AViviendaCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo numero_orden lo asigna el sistema'
    create.assert_not_called()


def test_post_viviendas_returns_conflict_when_orden_cannot_be_assigned():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/viviendas/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.create',
        side_effect=Formulario2AViviendaServiceError(
            'No se puede asignar otro número de orden en el formulario EDAN 2A',
            conflict=True,
        ),
    ):
        response = Formulario2AViviendaCreateView.as_view()(request)

    assert response.status_code == 409
    assert response.data['error'] == (
        'No se puede asignar otro número de orden en el formulario EDAN 2A'
    )


def test_post_viviendas_rejects_invalid_body():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/viviendas/', [], format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AViviendaCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El cuerpo de la solicitud no es válido'


def test_post_viviendas_returns_created_vivienda():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/viviendas/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    created = {'vivienda_id': 21, 'formulario_2a_id': 10}
    instance = object()

    with (
        patch(
            'app_sgbh.views.formulario_2a_vivienda_view.Formulario2AViviendaService.create',
            return_value=instance,
        ) as create,
        patch(
            'app_sgbh.views.formulario_2a_vivienda_view.ViviendaBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = created
        response = Formulario2AViviendaCreateView.as_view()(request)

    assert response.status_code == 201
    assert response.data == created
    create.assert_called_once()
    serializer_cls.assert_called_once_with(instance)
    assert create.call_args.kwargs['formulario_2a_id'] == 10
    assert 'numero_orden' not in create.call_args.kwargs
    assert create.call_args.kwargs['tipo_uso_instalacion_id'] == 2
    assert create.call_args.kwargs['numero_lote'] == 'L-1'
