from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers import first_error_message
from app_sgbh.serializers.formulario_2a_integrante import IntegranteCreateSerializer
from app_sgbh.services.formulario_2a_integrante import (
    Formulario2AIntegranteService,
    Formulario2AIntegranteServiceError,
)
from app_sgbh.views.formulario_2a_integrante_view import Formulario2AIntegranteCreateView


class _DoesNotExist(Exception):
    pass


def _parse_crear(data):
    serializer = IntegranteCreateSerializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data, None
    return None, first_error_message(serializer.errors)


def _body(**overrides):
    data = {
        'familia_id': 8,
        'persona_id': 15,
        'rol_familiar_id': 2,
        'edad': 34,
        'condicion_persona_id': 1,
    }
    data.update(overrides)
    return data


def _create_kwargs(**overrides):
    data = {
        'familia_id': 8,
        'persona_id': 15,
        'rol_familiar_id': 2,
        'edad': 34,
        'condicion_persona_id': 1,
        'tipo_danio_personal_id': None,
        'grado_lesion_id': None,
        'gestante_semanas': None,
        'tipo_discapacidad_id': None,
        'enfermedad_cronica_id': None,
    }
    data.update(overrides)
    return data


@contextmanager
def _persona_libre_en_emergencia(codigo_sinpad='261404'):
    with (
        patch(
            'app_sgbh.services.formulario_2a_integrante.codigo_sinpad_de_familia',
            return_value=codigo_sinpad,
        ) as codigo,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegranteService.search',
        ) as search,
    ):
        search.return_value.exists.return_value = False
        yield codigo, search


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


def test_parse_crear_accepts_required_fields_and_null_optionals():
    parsed, error = _parse_crear(_body())

    assert error is None
    assert parsed['familia_id'] == 8
    assert parsed['persona_id'] == 15
    assert 'numero_orden' not in parsed
    assert parsed['rol_familiar_id'] == 2
    assert parsed['edad'] == 34
    assert parsed['condicion_persona_id'] == 1
    assert parsed['tipo_danio_personal_id'] is None
    assert parsed['grado_lesion_id'] is None
    assert parsed['gestante_semanas'] is None
    assert parsed['tipo_discapacidad_id'] is None
    assert parsed['enfermedad_cronica_id'] is None


def test_parse_crear_reads_optional_fields_and_age_bounds():
    parsed, error = _parse_crear(
        _body(
            edad=0,
            tipo_danio_personal_id=1,
            grado_lesion_id=3,
            gestante_semanas=45,
            tipo_discapacidad_id=4,
            enfermedad_cronica_id=5,
        )
    )

    assert error is None
    assert parsed['edad'] == 0
    assert parsed['tipo_danio_personal_id'] == 1
    assert parsed['grado_lesion_id'] == 3
    assert parsed['gestante_semanas'] == 45
    assert parsed['tipo_discapacidad_id'] == 4
    assert parsed['enfermedad_cronica_id'] == 5


@pytest.mark.parametrize(
    ('field', 'value', 'message'),
    [
        ('familia_id', None, 'familia_id es obligatorio'),
        ('familia_id', '8.5', 'familia_id debe ser un número entero'),
        ('persona_id', None, 'persona_id es obligatorio'),
        ('persona_id', True, 'persona_id debe ser un número entero'),
        ('rol_familiar_id', None, 'rol_familiar_id es obligatorio'),
        ('edad', None, 'edad es obligatorio'),
        ('edad', 'treinta', 'edad debe ser un número entero'),
        ('edad', -1, 'edad debe estar entre 0 y 130'),
        ('edad', 131, 'edad debe estar entre 0 y 130'),
        ('condicion_persona_id', None, 'condicion_persona_id es obligatorio'),
        (
            'tipo_danio_personal_id',
            'x',
            'tipo_danio_personal_id debe ser un número entero',
        ),
        ('grado_lesion_id', '3.2', 'grado_lesion_id debe ser un número entero'),
        ('gestante_semanas', 0, 'gestante_semanas debe estar entre 1 y 45'),
        ('gestante_semanas', 46, 'gestante_semanas debe estar entre 1 y 45'),
        (
            'tipo_discapacidad_id',
            True,
            'tipo_discapacidad_id debe ser un número entero',
        ),
        (
            'enfermedad_cronica_id',
            'y',
            'enfermedad_cronica_id debe ser un número entero',
        ),
    ],
)
def test_parse_crear_rejects_invalid_fields(field, value, message):
    _parsed, error = _parse_crear(_body(**{field: value}))

    assert error is not None
    assert message in error


def test_create_rejects_edad_out_of_range():
    with pytest.raises(Formulario2AIntegranteServiceError) as exc:
        Formulario2AIntegranteService.create(**_create_kwargs(edad=131))

    assert exc.value.message == 'El campo edad debe estar entre 0 y 130'


def test_create_rejects_gestante_out_of_range():
    with pytest.raises(Formulario2AIntegranteServiceError) as exc:
        Formulario2AIntegranteService.create(**_create_kwargs(gestante_semanas=0))

    assert exc.value.message == 'El campo gestante_semanas debe estar entre 1 y 45'


def test_create_rejects_grado_when_tipo_danio_is_not_1():
    with pytest.raises(Formulario2AIntegranteServiceError) as exc:
        Formulario2AIntegranteService.create(
            **_create_kwargs(tipo_danio_personal_id=2, grado_lesion_id=3)
        )

    assert exc.value.message == (
        'El campo grado_lesion_id solo puede enviarse cuando tipo_danio_personal_id es 1'
    )


def test_create_rejects_unknown_familia():
    with (
        patch('app_sgbh.services.formulario_2a_integrante.transaction.atomic'),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AFamilia'
        ) as familia,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
    ):
        familia.DoesNotExist = _DoesNotExist
        familia.objects.select_for_update.return_value.get.side_effect = (
            _DoesNotExist
        )

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.create(**_create_kwargs())

    assert exc.value.not_found is True
    assert exc.value.message == 'La familia indicada no existe'
    integrante.assert_not_called()


def test_create_rejects_inactive_formulario():
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
        _padres_existentes(familia, vivienda, formulario, estado_registro_id=2)

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.create(**_create_kwargs())

    assert exc.value.conflict is True
    assert 'estado de registro es inactivo' in exc.value.message
    planilla.objects.filter.assert_not_called()
    integrante.assert_not_called()


def test_create_rejects_planilla_emitida():
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
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.create(**_create_kwargs())

    assert exc.value.conflict is True
    assert 'planilla BAH emitida y activa' in exc.value.message
    planilla.objects.filter.assert_called_once_with(
        integrante_receptor__familia__vivienda__formulario_2a_id=10,
        estado_planilla__codigo='EMITIDA',
    )
    integrante.assert_not_called()


def test_create_rejects_unknown_persona():
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
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        persona.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.create(**_create_kwargs())

    assert exc.value.message == 'La persona indicada no existe'
    persona.objects.filter.assert_called_once_with(pk=15)
    integrante.assert_not_called()


def test_create_rejects_duplicated_persona_in_the_familia():
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
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        persona.objects.filter.return_value.exists.return_value = True
        integrante.objects.filter.return_value.exists.return_value = True

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.create(**_create_kwargs())

    assert exc.value.conflict is True
    assert exc.value.message == (
        'La persona ya está registrada como integrante de esta familia'
    )
    integrante.objects.filter.assert_called_once_with(familia_id=8, persona_id=15)
    integrante.assert_not_called()


def test_create_rejects_persona_already_in_the_same_emergencia():
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
        patch(
            'app_sgbh.services.formulario_2a_integrante.codigo_sinpad_de_familia',
            return_value='261404',
        ) as codigo_sinpad,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegranteService.search',
        ) as search,
    ):
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        persona.objects.filter.return_value.exists.return_value = True
        integrante.objects.filter.return_value.exists.return_value = False
        search.return_value.exists.return_value = True

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.create(**_create_kwargs())

    assert exc.value.conflict is True
    assert exc.value.message == (
        'La persona ya está registrada como integrante de esta emergencia'
    )
    codigo_sinpad.assert_called_once_with(8)
    search.assert_called_once_with(codigo_sinpad='261404', persona_id=15)
    integrante.assert_not_called()


def test_create_skips_emergencia_check_when_codigo_sinpad_is_missing():
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
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
        patch(
            'app_sgbh.services.formulario_2a_integrante.codigo_sinpad_de_familia',
            return_value=None,
        ),
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegranteService.search',
        ) as search,
    ):
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        persona.objects.filter.return_value.exists.return_value = True
        integrante.objects.filter.return_value.exists.return_value = False
        rol.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.create(**_create_kwargs())

    assert exc.value.message == 'El rol familiar indicado no existe'
    search.assert_not_called()
    integrante.assert_not_called()


def test_create_rejects_unknown_rol_familiar():
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
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
        _persona_libre_en_emergencia(),
    ):
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        persona.objects.filter.return_value.exists.return_value = True
        integrante.objects.filter.return_value.exists.return_value = False
        rol.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.create(**_create_kwargs())

    assert exc.value.message == 'El rol familiar indicado no existe'
    integrante.assert_not_called()


def test_create_rejects_unknown_optional_catalog():
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
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
        _persona_libre_en_emergencia(),
    ):
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        persona.objects.filter.return_value.exists.return_value = True
        integrante.objects.filter.return_value.exists.return_value = False
        rol.objects.filter.return_value.exists.return_value = True
        condicion.objects.filter.return_value.exists.return_value = True
        tipo_danio.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.create(
                **_create_kwargs(tipo_danio_personal_id=7)
            )

    assert exc.value.message == 'El tipo de daño personal indicado no existe'
    tipo_danio.objects.filter.assert_called_once_with(pk=7)
    integrante.assert_not_called()


def test_create_rejects_when_numero_orden_reaches_the_column_limit():
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
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
        _persona_libre_en_emergencia(),
    ):
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        persona.objects.filter.return_value.exists.return_value = True
        rol.objects.filter.return_value.exists.return_value = True
        condicion.objects.filter.return_value.exists.return_value = True
        integrante.objects.filter.return_value.exists.return_value = False
        integrante.objects.filter.return_value.aggregate.return_value = {
            'maximo': 32767
        }

        with pytest.raises(Formulario2AIntegranteServiceError) as exc:
            Formulario2AIntegranteService.create(**_create_kwargs())

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede asignar otro número de orden en la familia'
    )
    integrante.assert_not_called()


def test_create_saves_when_references_exist():
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
            'app_sgbh.services.formulario_2a_integrante.TipoDiscapacidad'
        ) as discapacidad,
        patch(
            'app_sgbh.services.formulario_2a_integrante.EnfermedadCronica'
        ) as enfermedad,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
        _persona_libre_en_emergencia(),
    ):
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        persona.objects.filter.return_value.exists.return_value = True
        rol.objects.filter.return_value.exists.return_value = True
        condicion.objects.filter.return_value.exists.return_value = True
        tipo_danio.objects.filter.return_value.exists.return_value = True
        grado.objects.filter.return_value.exists.return_value = True
        discapacidad.objects.filter.return_value.exists.return_value = True
        enfermedad.objects.filter.return_value.exists.return_value = True
        integrante.objects.filter.return_value.exists.return_value = False
        integrante.objects.filter.return_value.aggregate.return_value = {'maximo': 4}
        integrante.return_value.pk = 31
        stored = integrante.objects.select_related.return_value.get.return_value

        result = Formulario2AIntegranteService.create(
            **_create_kwargs(
                tipo_danio_personal_id=1,
                grado_lesion_id=3,
                gestante_semanas=12,
                tipo_discapacidad_id=4,
                enfermedad_cronica_id=5,
            )
        )

    assert result is stored
    integrante.assert_called_once_with(
        familia_id=8,
        persona_id=15,
        rol_familiar_id=2,
        numero_orden=5,
        edad=34,
        condicion_persona_id=1,
        tipo_danio_personal_id=1,
        grado_lesion_id=3,
        gestante_semanas=12,
        tipo_discapacidad_id=4,
        enfermedad_cronica_id=5,
    )
    integrante.return_value.save.assert_called_once_with()
    integrante.objects.select_related.assert_called_once_with(
        'rol_familiar',
        'condicion_persona',
        'tipo_danio_personal',
        'grado_lesion',
        'tipo_discapacidad',
        'enfermedad_cronica',
    )
    integrante.objects.select_related.return_value.get.assert_called_once_with(pk=31)


def test_create_skips_optional_catalogs_when_they_are_null():
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
            'app_sgbh.services.formulario_2a_integrante.TipoDiscapacidad'
        ) as discapacidad,
        patch(
            'app_sgbh.services.formulario_2a_integrante.EnfermedadCronica'
        ) as enfermedad,
        patch(
            'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante'
        ) as integrante,
        _persona_libre_en_emergencia(),
    ):
        _padres_existentes(familia, vivienda, formulario)
        planilla.objects.filter.return_value.exists.return_value = False
        persona.objects.filter.return_value.exists.return_value = True
        rol.objects.filter.return_value.exists.return_value = True
        condicion.objects.filter.return_value.exists.return_value = True
        integrante.objects.filter.return_value.exists.return_value = False
        integrante.objects.filter.return_value.aggregate.return_value = {'maximo': None}
        integrante.return_value.pk = 31

        Formulario2AIntegranteService.create(**_create_kwargs(edad=0))

    assert integrante.call_args.kwargs['numero_orden'] == 1
    assert integrante.call_args.kwargs['edad'] == 0
    tipo_danio.objects.filter.assert_not_called()
    grado.objects.filter.assert_not_called()
    discapacidad.objects.filter.assert_not_called()
    enfermedad.objects.filter.assert_not_called()


def test_post_integrantes_returns_not_found_when_familia_is_missing():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/integrantes/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.create',
        side_effect=Formulario2AIntegranteServiceError(
            'La familia indicada no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AIntegranteCreateView.as_view()(request)

    assert response.status_code == 404
    assert response.data['error'] == 'La familia indicada no existe'


def test_post_integrantes_rejects_numero_orden_from_the_client():
    factory = APIRequestFactory()
    request = factory.post(
        '/api/sgbh/integrantes/',
        _body(numero_orden=3),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.create',
    ) as create:
        response = Formulario2AIntegranteCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo numero_orden lo asigna el sistema'
    create.assert_not_called()


def test_post_integrantes_returns_conflict_when_persona_is_duplicated():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/integrantes/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.create',
        side_effect=Formulario2AIntegranteServiceError(
            'La persona ya está registrada como integrante de esta familia',
            conflict=True,
        ),
    ):
        response = Formulario2AIntegranteCreateView.as_view()(request)

    assert response.status_code == 409
    assert response.data['error'] == (
        'La persona ya está registrada como integrante de esta familia'
    )


def test_post_integrantes_rejects_invalid_body():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/integrantes/', [], format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2AIntegranteCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El cuerpo de la solicitud no es válido'


def test_post_integrantes_returns_created_integrante():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/integrantes/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    created = {'integrante_id': 31, 'familia_id': 8}
    instance = object()

    with (
        patch(
            'app_sgbh.views.formulario_2a_integrante_view.Formulario2AIntegranteService.create',
            return_value=instance,
        ) as create,
        patch(
            'app_sgbh.views.formulario_2a_integrante_view.IntegranteSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = created
        response = Formulario2AIntegranteCreateView.as_view()(request)

    assert response.status_code == 201
    assert response.data == created
    create.assert_called_once()
    serializer_cls.assert_called_once_with(instance)
    assert create.call_args.kwargs['familia_id'] == 8
    assert create.call_args.kwargs['persona_id'] == 15
    assert 'numero_orden' not in create.call_args.kwargs
    assert create.call_args.kwargs['edad'] == 34
