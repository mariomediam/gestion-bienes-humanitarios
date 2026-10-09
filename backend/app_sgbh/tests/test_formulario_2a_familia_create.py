from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers import first_error_message
from app_sgbh.serializers.formulario_2a_familia import FamiliaCreateSerializer
from app_sgbh.services.formulario_2a_familia import (
    Formulario2AFamiliaService,
    Formulario2AFamiliaServiceError,
)
from app_sgbh.views.formulario_2a_familia_view import Formulario2AFamiliaCreateView


class _DoesNotExist(Exception):
    pass


def _parse_crear(data):
    serializer = FamiliaCreateSerializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data, None
    return None, first_error_message(serializer.errors)


def _body(**overrides):
    data = {'vivienda_id': 8}
    data.update(overrides)
    return data


def _vivienda_existente(vivienda, formulario_2a_id=10):
    vivienda.objects.select_for_update.return_value.get.return_value = (
        SimpleNamespace(pk=8, formulario_2a_id=formulario_2a_id)
    )


def _formulario_existente(formulario, estado_registro_id=1):
    formulario.objects.select_for_update.return_value.get.return_value = (
        SimpleNamespace(pk=10, estado_registro_id=estado_registro_id)
    )


def test_parse_crear_accepts_vivienda_id():
    parsed, error = _parse_crear(_body())

    assert error is None
    assert parsed['vivienda_id'] == 8
    assert 'numero_orden' not in parsed


@pytest.mark.parametrize(
    ('value', 'message'),
    [
        (None, 'vivienda_id es obligatorio'),
        ('8.5', 'vivienda_id debe ser un número entero'),
        (True, 'vivienda_id debe ser un número entero'),
    ],
)
def test_parse_crear_rejects_invalid_vivienda_id(value, message):
    _parsed, error = _parse_crear(_body(vivienda_id=value))

    assert error is not None
    assert message in error


def test_create_rejects_unknown_vivienda():
    with (
        patch('app_sgbh.services.formulario_2a_familia.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_familia.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2AFamilia') as familia,
    ):
        vivienda.DoesNotExist = _DoesNotExist
        vivienda.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AFamiliaServiceError) as exc:
            Formulario2AFamiliaService.create(vivienda_id=8)

    assert exc.value.not_found is True
    assert exc.value.message == 'La vivienda indicada no existe'
    familia.assert_not_called()


def test_create_rejects_unknown_formulario():
    with (
        patch('app_sgbh.services.formulario_2a_familia.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_familia.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2AFamilia') as familia,
    ):
        _vivienda_existente(vivienda)
        formulario.DoesNotExist = _DoesNotExist
        formulario.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AFamiliaServiceError) as exc:
            Formulario2AFamiliaService.create(vivienda_id=8)

    assert exc.value.not_found is True
    assert exc.value.message == 'El formulario EDAN 2A indicado no existe'
    familia.assert_not_called()


def test_create_rejects_inactive_formulario():
    with (
        patch('app_sgbh.services.formulario_2a_familia.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_familia.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2AFamilia') as familia,
    ):
        _vivienda_existente(vivienda)
        _formulario_existente(formulario, estado_registro_id=2)

        with pytest.raises(Formulario2AFamiliaServiceError) as exc:
            Formulario2AFamiliaService.create(vivienda_id=8)

    assert exc.value.conflict is True
    assert 'estado de registro es inactivo' in exc.value.message
    planilla.objects.filter.assert_not_called()
    familia.assert_not_called()


def test_create_rejects_planilla_emitida():
    with (
        patch('app_sgbh.services.formulario_2a_familia.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_familia.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2AFamilia') as familia,
    ):
        _vivienda_existente(vivienda)
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AFamiliaServiceError) as exc:
            Formulario2AFamiliaService.create(vivienda_id=8)

    assert exc.value.conflict is True
    assert 'planilla BAH emitida y activa' in exc.value.message
    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=10,
        estado_planilla__codigo='EMITIDA',
    )
    familia.assert_not_called()


def test_create_rejects_when_numero_orden_reaches_the_column_limit():
    with (
        patch('app_sgbh.services.formulario_2a_familia.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_familia.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2AFamilia') as familia,
    ):
        _vivienda_existente(vivienda)
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        familia.objects.filter.return_value.aggregate.return_value = {'maximo': 32767}

        with pytest.raises(Formulario2AFamiliaServiceError) as exc:
            Formulario2AFamiliaService.create(vivienda_id=8)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede asignar otro número de orden en la vivienda'
    )
    familia.objects.filter.assert_called_once_with(vivienda_id=8)
    familia.assert_not_called()


def test_create_saves_when_references_exist():
    with (
        patch('app_sgbh.services.formulario_2a_familia.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_familia.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2AFamilia') as familia,
    ):
        _vivienda_existente(vivienda)
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        familia.objects.filter.return_value.aggregate.return_value = {'maximo': 4}
        familia.return_value.pk = 33
        stored = familia.objects.get.return_value

        result = Formulario2AFamiliaService.create(vivienda_id=8)

    assert result is stored
    familia.assert_called_once_with(vivienda_id=8, numero_orden=5)
    familia.return_value.save.assert_called_once_with()
    familia.objects.get.assert_called_once_with(pk=33)


def test_create_assigns_orden_one_when_the_vivienda_has_no_familias():
    with (
        patch('app_sgbh.services.formulario_2a_familia.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_familia.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch('app_sgbh.services.formulario_2a_familia.Formulario2AFamilia') as familia,
    ):
        _vivienda_existente(vivienda)
        _formulario_existente(formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        familia.objects.filter.return_value.aggregate.return_value = {'maximo': None}
        familia.return_value.pk = 33

        Formulario2AFamiliaService.create(vivienda_id=8)

    assert familia.call_args.kwargs['numero_orden'] == 1


def test_post_familias_returns_not_found_when_vivienda_is_missing():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/familias/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_familia_view.Formulario2AFamiliaService.create',
        side_effect=Formulario2AFamiliaServiceError(
            'La vivienda indicada no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AFamiliaCreateView.as_view()(request)

    assert response.status_code == 404
    assert response.data['error'] == 'La vivienda indicada no existe'


def test_post_familias_rejects_numero_orden_from_the_client():
    factory = APIRequestFactory()
    request = factory.post(
        '/api/sgbh/familias/',
        _body(numero_orden=3),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_familia_view.Formulario2AFamiliaService.create',
    ) as create:
        response = Formulario2AFamiliaCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo numero_orden lo asigna el sistema'
    create.assert_not_called()


def test_post_familias_returns_conflict_when_orden_cannot_be_assigned():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/familias/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_familia_view.Formulario2AFamiliaService.create',
        side_effect=Formulario2AFamiliaServiceError(
            'No se puede asignar otro número de orden en la vivienda',
            conflict=True,
        ),
    ):
        response = Formulario2AFamiliaCreateView.as_view()(request)

    assert response.status_code == 409
    assert response.data['error'] == (
        'No se puede asignar otro número de orden en la vivienda'
    )


def test_post_familias_rejects_invalid_body():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/familias/', [], format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AFamiliaCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El cuerpo de la solicitud no es válido'


def test_post_familias_returns_created_familia():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/familias/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    created = {'familia_id': 33, 'vivienda_id': 8}
    instance = object()

    with (
        patch(
            'app_sgbh.views.formulario_2a_familia_view.Formulario2AFamiliaService.create',
            return_value=instance,
        ) as create,
        patch(
            'app_sgbh.views.formulario_2a_familia_view.FamiliaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = created
        response = Formulario2AFamiliaCreateView.as_view()(request)

    assert response.status_code == 201
    assert response.data == created
    create.assert_called_once_with(vivienda_id=8)
    serializer_cls.assert_called_once_with(instance)
