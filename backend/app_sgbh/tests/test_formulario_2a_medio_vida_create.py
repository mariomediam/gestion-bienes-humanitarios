from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers import first_error_message
from app_sgbh.serializers.formulario_2a_medio_vida import MedioVidaCreateSerializer
from app_sgbh.services.formulario_2a_medio_vida import (
    Formulario2AMedioVidaService,
    Formulario2AMedioVidaServiceError,
)
from app_sgbh.views.formulario_2a_medio_vida_view import (
    Formulario2AMedioVidaCreateView,
)


class _DoesNotExist(Exception):
    pass


def _parse_crear(data):
    serializer = MedioVidaCreateSerializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data, None
    return None, first_error_message(serializer.errors)


def _body(**overrides):
    data = {
        'familia_id': 8,
        'tipo_medio_vida_id': 3,
        'cantidad': 2,
    }
    data.update(overrides)
    return data


def _create_kwargs(**overrides):
    data = {
        'familia_id': 8,
        'tipo_medio_vida_id': 3,
        'cantidad': 2,
        'observacion': None,
    }
    data.update(overrides)
    return data


def _padres_existentes(familia, vivienda, formulario, estado_registro_id=1):
    familia.objects.select_for_update.return_value.get.return_value = SimpleNamespace(
        pk=8,
        vivienda_id=4,
    )
    vivienda.objects.select_for_update.return_value.get.return_value = SimpleNamespace(
        pk=4,
        formulario_2a_id=10,
    )
    formulario.objects.select_for_update.return_value.get.return_value = (
        SimpleNamespace(pk=10, estado_registro_id=estado_registro_id)
    )


def test_parse_crear_accepts_required_fields_and_null_observacion():
    parsed, error = _parse_crear(_body())

    assert error is None
    assert parsed['familia_id'] == 8
    assert parsed['tipo_medio_vida_id'] == 3
    assert parsed['cantidad'] == 2
    assert parsed['observacion'] is None


def test_parse_crear_trims_observacion():
    parsed, error = _parse_crear(_body(observacion='  cultivo de arroz  '))

    assert error is None
    assert parsed['observacion'] == 'cultivo de arroz'


def test_parse_crear_stores_blank_observacion_as_null():
    parsed, error = _parse_crear(_body(observacion='   '))

    assert error is None
    assert parsed['observacion'] is None


@pytest.mark.parametrize(
    ('field', 'value', 'message'),
    [
        ('familia_id', None, 'familia_id es obligatorio'),
        ('familia_id', '8.5', 'familia_id debe ser un número entero'),
        ('tipo_medio_vida_id', None, 'tipo_medio_vida_id es obligatorio'),
        (
            'tipo_medio_vida_id',
            'x',
            'tipo_medio_vida_id debe ser un número entero',
        ),
        ('cantidad', None, 'cantidad es obligatorio'),
        ('cantidad', '2.5', 'cantidad debe ser un número entero'),
        ('cantidad', True, 'cantidad debe ser un número entero'),
        ('cantidad', 0, 'cantidad debe ser mayor que cero'),
        ('cantidad', -1, 'cantidad debe ser mayor que cero'),
        ('observacion', 'a' * 501, 'observacion no debe superar 500'),
    ],
)
def test_parse_crear_rejects_invalid_fields(field, value, message):
    _parsed, error = _parse_crear(_body(**{field: value}))

    assert error is not None
    assert message in error


def test_create_rejects_non_text_observacion():
    with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
        Formulario2AMedioVidaService.create(**_create_kwargs(observacion=12))

    assert exc.value.message == 'El campo observacion debe ser texto'


def test_create_rejects_cantidad_zero():
    with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
        Formulario2AMedioVidaService.create(**_create_kwargs(cantidad=0))

    assert exc.value.message == 'El campo cantidad debe ser mayor que cero'


def test_create_rejects_unknown_familia():
    with (
        patch('app_sgbh.services.formulario_2a_medio_vida.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
        ) as medio_vida,
    ):
        familia.DoesNotExist = _DoesNotExist
        familia.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.create(**_create_kwargs())

    assert exc.value.not_found is True
    assert exc.value.message == 'La familia indicada no existe'
    medio_vida.assert_not_called()


def test_create_rejects_inactive_formulario():
    with (
        patch('app_sgbh.services.formulario_2a_medio_vida.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AVivienda'
        ) as vivienda,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2A'
        ) as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
        ) as medio_vida,
    ):
        _padres_existentes(familia, vivienda, formulario, estado_registro_id=2)

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.create(**_create_kwargs())

    assert exc.value.conflict is True
    assert 'estado de registro es inactivo' in exc.value.message
    planilla.objects.filter.assert_not_called()
    medio_vida.assert_not_called()


def test_create_rejects_planilla_emitida():
    with (
        patch('app_sgbh.services.formulario_2a_medio_vida.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AVivienda'
        ) as vivienda,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2A'
        ) as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
        ) as medio_vida,
    ):
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.create(**_create_kwargs())

    assert exc.value.conflict is True
    assert 'planilla BAH emitida y activa' in exc.value.message
    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=10,
        estado_planilla__codigo='EMITIDA',
    )
    medio_vida.assert_not_called()


def test_create_rejects_unknown_tipo():
    with (
        patch('app_sgbh.services.formulario_2a_medio_vida.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AVivienda'
        ) as vivienda,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2A'
        ) as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.TipoMedioVida'
        ) as tipo,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
        ) as medio_vida,
    ):
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        tipo.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.create(**_create_kwargs())

    assert exc.value.message == 'El tipo de medio de vida indicado no existe'
    tipo.objects.filter.assert_called_once_with(pk=3)
    medio_vida.assert_not_called()


def test_create_rejects_duplicate_tipo_in_the_same_familia():
    with (
        patch('app_sgbh.services.formulario_2a_medio_vida.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AVivienda'
        ) as vivienda,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2A'
        ) as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.TipoMedioVida'
        ) as tipo,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
        ) as medio_vida,
    ):
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        tipo.objects.filter.return_value.exists.return_value = True
        medio_vida.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.create(**_create_kwargs())

    assert exc.value.conflict is True
    assert exc.value.message == (
        'La familia ya tiene registrado este tipo de medio de vida'
    )
    medio_vida.objects.filter.assert_called_once_with(
        familia_id=8,
        tipo_medio_vida_id=3,
    )
    medio_vida.assert_not_called()


def test_create_saves_when_references_exist():
    with (
        patch('app_sgbh.services.formulario_2a_medio_vida.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AVivienda'
        ) as vivienda,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2A'
        ) as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.TipoMedioVida'
        ) as tipo,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
        ) as medio_vida,
    ):
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        tipo.objects.filter.return_value.exists.return_value = True
        medio_vida.objects.filter.return_value.exists.return_value = False
        medio_vida.return_value.pk = 21
        stored = medio_vida.objects.select_related.return_value.get.return_value

        result = Formulario2AMedioVidaService.create(
            **_create_kwargs(observacion='  parcela familiar  ')
        )

    assert result is stored
    medio_vida.assert_called_once_with(
        familia_id=8,
        tipo_medio_vida_id=3,
        cantidad=2,
        observacion='parcela familiar',
    )
    medio_vida.return_value.save.assert_called_once_with()
    medio_vida.objects.select_related.assert_called_once_with(
        'tipo_medio_vida',
        'tipo_medio_vida__categoria_medio_vida',
    )
    medio_vida.objects.select_related.return_value.get.assert_called_once_with(
        pk=21
    )


def test_post_medios_vida_returns_not_found_when_familia_is_missing():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/medios-vida/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.create',
        side_effect=Formulario2AMedioVidaServiceError(
            'La familia indicada no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AMedioVidaCreateView.as_view()(request)

    assert response.status_code == 404
    assert response.data['error'] == 'La familia indicada no existe'


def test_post_medios_vida_returns_conflict_when_tipo_is_duplicated():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/medios-vida/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.create',
        side_effect=Formulario2AMedioVidaServiceError(
            'La familia ya tiene registrado este tipo de medio de vida',
            conflict=True,
        ),
    ):
        response = Formulario2AMedioVidaCreateView.as_view()(request)

    assert response.status_code == 409
    assert response.data['error'] == (
        'La familia ya tiene registrado este tipo de medio de vida'
    )


def test_post_medios_vida_rejects_invalid_body():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/medios-vida/', [], format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AMedioVidaCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El cuerpo de la solicitud no es válido'


def test_post_medios_vida_returns_created_medio_vida():
    factory = APIRequestFactory()
    request = factory.post(
        '/api/sgbh/medios-vida/',
        _body(observacion='parcela'),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    created = {'medio_vida_id': 21, 'familia_id': 8}
    instance = object()

    with (
        patch(
            'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.create',
            return_value=instance,
        ) as create,
        patch(
            'app_sgbh.views.formulario_2a_medio_vida_view.MedioVidaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = created
        response = Formulario2AMedioVidaCreateView.as_view()(request)

    assert response.status_code == 201
    assert response.data == created
    create.assert_called_once()
    serializer_cls.assert_called_once_with(instance)
    assert create.call_args.kwargs['familia_id'] == 8
    assert create.call_args.kwargs['tipo_medio_vida_id'] == 3
    assert create.call_args.kwargs['cantidad'] == 2
    assert create.call_args.kwargs['observacion'] == 'parcela'
