from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers import first_error_message
from app_sgbh.serializers.formulario_2a_integrante import IntegranteUpdateSerializer
from app_sgbh.services.formulario_2a_integrante import (
    Formulario2AIntegranteService,
    Formulario2AIntegranteServiceError,
)
from app_sgbh.views.formulario_2a_integrante_view import Formulario2AIntegranteDetailView


class _DoesNotExist(Exception):
    pass


class _Integrante:
    def __init__(self):
        self.pk = 31
        self.familia_id = 8
        self.persona_id = 15
        self.rol_familiar_id = 2
        self.numero_orden = 3
        self.edad = 34
        self.condicion_persona_id = 1
        self.tipo_danio_personal_id = None
        self.grado_lesion_id = None
        self.gestante_semanas = None
        self.tipo_discapacidad_id = None
        self.enfermedad_cronica_id = None
        self.fecha_creacion = 'fecha-original'
        self.saved = False

    def save(self):
        self.saved = True


def _parse_modificar(data):
    serializer = IntegranteUpdateSerializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data, None
    return None, first_error_message(serializer.errors)


def _body(**overrides):
    data = {
        'persona_id': 16,
        'rol_familiar_id': 4,
        'edad': 40,
        'condicion_persona_id': 2,
    }
    data.update(overrides)
    return data


def _update_kwargs(**overrides):
    data = {
        'persona_id': 16,
        'rol_familiar_id': 4,
        'edad': 40,
        'condicion_persona_id': 2,
        'tipo_danio_personal_id': None,
        'grado_lesion_id': None,
        'gestante_semanas': None,
        'tipo_discapacidad_id': None,
        'enfermedad_cronica_id': None,
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


def _referencias_validas(persona, rol, condicion, integrante):
    persona.objects.filter.return_value.exists.return_value = True
    rol.objects.filter.return_value.exists.return_value = True
    condicion.objects.filter.return_value.exists.return_value = True
    integrante.objects.filter.return_value.exclude.return_value.exists.return_value = (
        False
    )


def test_parse_modificar_accepts_editable_fields_without_familia():
    parsed, error = _parse_modificar(_body(edad=0, gestante_semanas=12))

    assert error is None
    assert 'familia_id' not in parsed
    assert 'numero_orden' not in parsed
    assert parsed['persona_id'] == 16
    assert parsed['rol_familiar_id'] == 4
    assert parsed['edad'] == 0
    assert parsed['condicion_persona_id'] == 2
    assert parsed['gestante_semanas'] == 12


def test_parse_modificar_ignores_familia_id_when_the_view_already_rejected_it():
    parsed, error = _parse_modificar(_body(familia_id=99, numero_orden=1))

    assert error is None
    assert 'familia_id' not in parsed
    assert 'numero_orden' not in parsed


def test_update_rejects_missing_integrante():
    with (
        patch('app_sgbh.services.formulario_2a_integrante.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
    ):
        integrante.DoesNotExist = _DoesNotExist
        integrante.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.update(31, **_update_kwargs())

    assert exc.value.not_found is True
    assert exc.value.message == 'El integrante indicado no existe'
    familia.objects.select_for_update.assert_not_called()


def test_update_rejects_inactive_formulario():
    row = _Integrante()
    with (
        patch('app_sgbh.services.formulario_2a_integrante.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_integrante.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
    ):
        integrante.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario, estado_registro_id=2)

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.update(31, **_update_kwargs())

    assert exc.value.conflict is True
    assert 'estado de registro es inactivo' in exc.value.message
    planilla.objects.filter.assert_not_called()
    assert row.saved is False
    assert row.persona_id == 15


def test_update_rejects_planilla_emitida():
    row = _Integrante()
    with (
        patch('app_sgbh.services.formulario_2a_integrante.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_integrante.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
    ):
        integrante.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.update(31, **_update_kwargs())

    assert exc.value.conflict is True
    assert 'planilla BAH emitida y activa' in exc.value.message
    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=10,
        estado_planilla__codigo='EMITIDA',
    )
    assert row.saved is False


def test_update_rejects_duplicated_persona_in_the_familia():
    row = _Integrante()
    with (
        patch('app_sgbh.services.formulario_2a_integrante.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_integrante.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch('app_sgbh.services.formulario_2a_integrante.Persona') as persona,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
    ):
        integrante.objects.select_for_update.return_value.get.return_value = row
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        persona.objects.filter.return_value.exists.return_value = True
        integrante.objects.filter.return_value.exclude.return_value.exists.return_value = (
            True
        )

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.update(31, **_update_kwargs())

    assert exc.value.conflict is True
    assert exc.value.message == (
        'La persona ya está registrada como integrante de esta familia'
    )
    integrante.objects.filter.assert_called_once_with(familia_id=8, persona_id=16)
    integrante.objects.filter.return_value.exclude.assert_called_once_with(pk=31)
    assert row.saved is False


def test_update_keeps_familia_orden_and_fecha_creacion():
    row = _Integrante()
    with (
        patch('app_sgbh.services.formulario_2a_integrante.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AVivienda'
        ) as vivienda,
        patch('app_sgbh.services.formulario_2a_integrante.Formulario2A') as formulario,
        patch('app_sgbh.services.formulario_2a.PlanillaEntrega') as planilla,
        patch('app_sgbh.services.formulario_2a_integrante.Persona') as persona,
        patch('app_sgbh.services.formulario_2a_integrante.RolFamiliar') as rol,
        patch(
            'app_sgbh.services.formulario_2a_integrante.CondicionPersona'
        ) as condicion,
        patch(
            'app_sgbh.services.formulario_2a_integrante.TipoDanioPersonal'
        ) as tipo_danio,
        patch('app_sgbh.services.formulario_2a_integrante.GradoLesion') as grado,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
    ):
        integrante.objects.select_for_update.return_value.get.return_value = row
        stored = object()
        integrante.objects.select_related.return_value.get.return_value = stored
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        _referencias_validas(persona, rol, condicion, integrante)
        tipo_danio.objects.filter.return_value.exists.return_value = True
        grado.objects.filter.return_value.exists.return_value = True

        result = Formulario2AIntegranteService.update(
            31,
            **_update_kwargs(
                tipo_danio_personal_id=1,
                grado_lesion_id=3,
                gestante_semanas=20,
            ),
        )

    assert result is stored
    assert row.saved is True
    assert row.familia_id == 8
    assert row.numero_orden == 3
    assert row.fecha_creacion == 'fecha-original'
    assert row.persona_id == 16
    assert row.rol_familiar_id == 4
    assert row.edad == 40
    assert row.condicion_persona_id == 2
    assert row.tipo_danio_personal_id == 1
    assert row.grado_lesion_id == 3
    assert row.gestante_semanas == 20
    assert row.tipo_discapacidad_id is None
    assert row.enfermedad_cronica_id is None
    integrante.objects.select_for_update.return_value.get.assert_called_once_with(pk=31)
    integrante.objects.filter.return_value.exclude.assert_called_once_with(pk=31)
    integrante.objects.select_related.return_value.get.assert_called_once_with(pk=31)


def test_put_integrantes_rejects_familia_id():
    factory = APIRequestFactory()
    request = factory.put(
        '/api/sgbh/integrantes/31/',
        _body(familia_id=99),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.update',
    ) as update:
        response = Formulario2AIntegranteDetailView.as_view()(request, integrante_id=31)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo familia_id no puede modificarse'
    update.assert_not_called()


def test_put_integrantes_rejects_numero_orden():
    factory = APIRequestFactory()
    request = factory.put(
        '/api/sgbh/integrantes/31/',
        _body(numero_orden=1),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.update',
    ) as update:
        response = Formulario2AIntegranteDetailView.as_view()(request, integrante_id=31)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo numero_orden no puede modificarse'
    update.assert_not_called()


def test_put_integrantes_rejects_invalid_integrante_id():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/integrantes/0/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.update',
    ) as update:
        response = Formulario2AIntegranteDetailView.as_view()(request, integrante_id=0)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo integrante_id debe ser un número entero'
    update.assert_not_called()


def test_put_integrantes_returns_not_found():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/integrantes/31/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.update',
        side_effect=Formulario2AIntegranteServiceError(
            'El integrante indicado no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AIntegranteDetailView.as_view()(request, integrante_id=31)

    assert response.status_code == 404
    assert response.data['error'] == 'El integrante indicado no existe'


def test_put_integrantes_rejects_invalid_body():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/integrantes/31/', [], format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AIntegranteDetailView.as_view()(request, integrante_id=31)

    assert response.status_code == 400
    assert response.data['error'] == 'El cuerpo de la solicitud no es válido'


def test_put_integrantes_returns_updated_integrante():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/integrantes/31/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    updated = {'integrante_id': 31, 'persona_id': 16}
    instance = object()

    with (
        patch(
            'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.update',
            return_value=instance,
        ) as update,
        patch(
            'app_sgbh.views.formulario_2a_integrante_view.IntegranteBusquedaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = updated
        response = Formulario2AIntegranteDetailView.as_view()(request, integrante_id=31)

    assert response.status_code == 200
    assert response.data == updated
    update.assert_called_once()
    serializer_cls.assert_called_once_with(instance)
    assert update.call_args.args == (31,)
    assert update.call_args.kwargs['persona_id'] == 16
    assert update.call_args.kwargs['rol_familiar_id'] == 4
    assert update.call_args.kwargs['edad'] == 40
    assert 'familia_id' not in update.call_args.kwargs
    assert 'numero_orden' not in update.call_args.kwargs
