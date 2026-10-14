from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers import first_error_message
from app_sgbh.serializers.formulario_2a_medio_vida import MedioVidaUpdateSerializer
from app_sgbh.services.formulario_2a_medio_vida import (
    Formulario2AMedioVidaService,
    Formulario2AMedioVidaServiceError,
)
from app_sgbh.views.formulario_2a_medio_vida_view import (
    Formulario2AMedioVidaDetailView,
)


class _DoesNotExist(Exception):
    pass


class _MedioVida:
    def __init__(self):
        self.pk = 21
        self.familia_id = 8
        self.tipo_medio_vida_id = 3
        self.cantidad = 2
        self.observacion = 'parcela original'
        self.fecha_creacion = 'fecha-original'
        self.saved = False

    def save(self):
        self.saved = True


def _parse_modificar(data):
    serializer = MedioVidaUpdateSerializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data, None
    return None, first_error_message(serializer.errors)


def _body(**overrides):
    data = {
        'tipo_medio_vida_id': 5,
        'cantidad': 4,
    }
    data.update(overrides)
    return data


def _update_kwargs(**overrides):
    data = {
        'tipo_medio_vida_id': 5,
        'cantidad': 4,
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


def test_parse_modificar_accepts_editable_fields_without_familia():
    parsed, error = _parse_modificar(_body(observacion='  cultivo  '))

    assert error is None
    assert 'familia_id' not in parsed
    assert parsed['tipo_medio_vida_id'] == 5
    assert parsed['cantidad'] == 4
    assert parsed['observacion'] == 'cultivo'


def test_parse_modificar_stores_blank_observacion_as_null():
    parsed, error = _parse_modificar(_body(observacion='   ', familia_id=99))

    assert error is None
    assert 'familia_id' not in parsed
    assert parsed['observacion'] is None


@pytest.mark.parametrize(
    ('field', 'value', 'message'),
    [
        ('tipo_medio_vida_id', None, 'tipo_medio_vida_id es obligatorio'),
        ('cantidad', 0, 'cantidad debe ser mayor que cero'),
        ('cantidad', True, 'cantidad debe ser un número entero'),
        ('observacion', 'a' * 501, 'observacion no debe superar 500'),
    ],
)
def test_parse_modificar_rejects_invalid_fields(field, value, message):
    _parsed, error = _parse_modificar(_body(**{field: value}))

    assert error is not None
    assert message in error


def test_update_rejects_missing_medio_vida():
    with (
        patch('app_sgbh.services.formulario_2a_medio_vida.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_medio_vida.Formulario2AMedioVida'
        ) as medio_vida,
    ):
        medio_vida.DoesNotExist = _DoesNotExist
        medio_vida.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.update(21, **_update_kwargs())

    assert exc.value.not_found is True
    assert exc.value.message == 'El medio de vida indicado no existe'
    familia.objects.select_for_update.assert_not_called()


def test_update_rejects_inactive_formulario():
    row = _MedioVida()
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
        medio_vida.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario, estado_registro_id=2)

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.update(21, **_update_kwargs())

    assert exc.value.conflict is True
    assert 'estado de registro es inactivo' in exc.value.message
    planilla.objects.filter.assert_not_called()
    assert row.saved is False
    assert row.tipo_medio_vida_id == 3
    assert row.cantidad == 2


def test_update_rejects_planilla_emitida():
    row = _MedioVida()
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
        medio_vida.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.update(21, **_update_kwargs())

    assert exc.value.conflict is True
    assert 'planilla BAH emitida y activa' in exc.value.message
    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=10,
        estado_planilla__codigo='EMITIDA',
    )
    assert row.saved is False


def test_update_rejects_unknown_tipo():
    row = _MedioVida()
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
        medio_vida.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        tipo.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.update(21, **_update_kwargs())

    assert exc.value.message == 'El tipo de medio de vida indicado no existe'
    tipo.objects.filter.assert_called_once_with(pk=5)
    assert row.saved is False


def test_update_rejects_duplicate_tipo_in_the_same_familia():
    row = _MedioVida()
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
        medio_vida.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        tipo.objects.filter.return_value.exists.return_value = True
        medio_vida.objects.filter.return_value.exclude.return_value.exists.return_value = (
            True
        )

        with pytest.raises(Formulario2AMedioVidaServiceError) as exc:
            Formulario2AMedioVidaService.update(21, **_update_kwargs())

    assert exc.value.conflict is True
    assert exc.value.message == (
        'La familia ya tiene registrado este tipo de medio de vida'
    )
    medio_vida.objects.filter.assert_called_once_with(
        familia_id=8,
        tipo_medio_vida_id=5,
    )
    medio_vida.objects.filter.return_value.exclude.assert_called_once_with(pk=21)
    assert row.saved is False


def test_update_keeps_familia_and_fecha_creacion():
    row = _MedioVida()
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
        medio_vida.objects.select_for_update.return_value.get.return_value = row
        stored = object()
        medio_vida.objects.select_related.return_value.get.return_value = stored
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        tipo.objects.filter.return_value.exists.return_value = True
        medio_vida.objects.filter.return_value.exclude.return_value.exists.return_value = (
            False
        )

        result = Formulario2AMedioVidaService.update(
            21,
            **_update_kwargs(observacion='  parcela familiar  '),
        )

    assert result is stored
    assert row.saved is True
    assert row.familia_id == 8
    assert row.fecha_creacion == 'fecha-original'
    assert row.tipo_medio_vida_id == 5
    assert row.cantidad == 4
    assert row.observacion == 'parcela familiar'
    medio_vida.objects.select_for_update.return_value.get.assert_called_once_with(
        pk=21
    )
    medio_vida.objects.filter.return_value.exclude.assert_called_once_with(pk=21)
    medio_vida.objects.select_related.return_value.get.assert_called_once_with(pk=21)


def test_put_medios_vida_rejects_familia_id():
    factory = APIRequestFactory()
    request = factory.put(
        '/api/sgbh/medios-vida/21/',
        _body(familia_id=99),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.update',
    ) as update:
        response = Formulario2AMedioVidaDetailView.as_view()(
            request,
            medio_vida_id=21,
        )

    assert response.status_code == 400
    assert response.data['error'] == 'El campo familia_id no puede modificarse'
    update.assert_not_called()


def test_put_medios_vida_rejects_invalid_medio_vida_id():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/medios-vida/0/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.update',
    ) as update:
        response = Formulario2AMedioVidaDetailView.as_view()(
            request,
            medio_vida_id=0,
        )

    assert response.status_code == 400
    assert response.data['error'] == 'El campo medio_vida_id debe ser un número entero'
    update.assert_not_called()


def test_put_medios_vida_returns_not_found():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/medios-vida/21/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.update',
        side_effect=Formulario2AMedioVidaServiceError(
            'El medio de vida indicado no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AMedioVidaDetailView.as_view()(
            request,
            medio_vida_id=21,
        )

    assert response.status_code == 404
    assert response.data['error'] == 'El medio de vida indicado no existe'


def test_put_medios_vida_returns_conflict_when_tipo_is_duplicated():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/medios-vida/21/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.update',
        side_effect=Formulario2AMedioVidaServiceError(
            'La familia ya tiene registrado este tipo de medio de vida',
            conflict=True,
        ),
    ):
        response = Formulario2AMedioVidaDetailView.as_view()(
            request,
            medio_vida_id=21,
        )

    assert response.status_code == 409
    assert response.data['error'] == (
        'La familia ya tiene registrado este tipo de medio de vida'
    )


def test_put_medios_vida_rejects_invalid_body():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/medios-vida/21/', [], format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AMedioVidaDetailView.as_view()(request, medio_vida_id=21)

    assert response.status_code == 400
    assert response.data['error'] == 'El cuerpo de la solicitud no es válido'


def test_put_medios_vida_returns_updated_medio_vida():
    factory = APIRequestFactory()
    request = factory.put(
        '/api/sgbh/medios-vida/21/',
        _body(observacion='parcela'),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    updated = {'medio_vida_id': 21, 'tipo_medio_vida_id': 5}
    instance = object()

    with (
        patch(
            'app_sgbh.views.formulario_2a_medio_vida_view.Formulario2AMedioVidaService.update',
            return_value=instance,
        ) as update,
        patch(
            'app_sgbh.views.formulario_2a_medio_vida_view.MedioVidaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = updated
        response = Formulario2AMedioVidaDetailView.as_view()(
            request,
            medio_vida_id=21,
        )

    assert response.status_code == 200
    assert response.data == updated
    update.assert_called_once()
    serializer_cls.assert_called_once_with(instance)
    assert update.call_args.args == (21,)
    assert update.call_args.kwargs['tipo_medio_vida_id'] == 5
    assert update.call_args.kwargs['cantidad'] == 4
    assert update.call_args.kwargs['observacion'] == 'parcela'
    assert 'familia_id' not in update.call_args.kwargs
