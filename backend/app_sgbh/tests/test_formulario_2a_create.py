from datetime import date, time
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers import Formulario2ACreateSerializer, first_error_message
from app_sgbh.services.formulario_2a import (
    Formulario2AService,
    Formulario2AServiceError,
)
from app_sgbh.views.formulario_2a_view import Formulario2ACreateView


def _parse_crear(data):
    serializer = Formulario2ACreateSerializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data, None
    return None, first_error_message(serializer.errors)


def _body(**overrides):
    data = {
        'emergencia_id': 4,
        'departamento_id': '20',
        'provincia_id': '01',
        'distrito_id': '01',
        'fecha_empadronamiento': '2026-10-01',
        'evaluador_id': 7,
        'estado_registro_id': 2,
    }
    data.update(overrides)
    return data


def _create_kwargs(**overrides):
    data = {
        'emergencia_id': 4,
        'departamento_id': '20',
        'provincia_id': '01',
        'distrito_id': '01',
        'fecha_empadronamiento': date(2026, 10, 1),
        'evaluador_id': 7,
        'estado_registro_id': 2,
        'c_usuari_login': 'mmedina',
        'hora_empadronamiento': None,
        'localidad': None,
        'barrio_sector_urbanizacion': None,
        'centro_poblado': None,
        'caserio': None,
        'anexo': None,
        'calle_manzana': None,
        'edificio_piso_dpto': None,
        'otros_ubicacion': None,
        'numero_hoja': 1,
        'total_hojas': None,
        'institucion': None,
    }
    data.update(overrides)
    return data


def test_parse_crear_accepts_required_fields_and_defaults():
    parsed, error = _parse_crear(_body())

    assert error is None
    assert parsed['emergencia_id'] == 4
    assert parsed['departamento_id'] == '20'
    assert parsed['provincia_id'] == '01'
    assert parsed['distrito_id'] == '01'
    assert parsed['fecha_empadronamiento'] == date(2026, 10, 1)
    assert parsed['hora_empadronamiento'] is None
    assert parsed['numero_hoja'] == 1
    assert parsed['total_hojas'] is None
    assert parsed['evaluador_id'] == 7
    assert parsed['estado_registro_id'] == 2
    assert parsed['localidad'] is None
    assert parsed['institucion'] is None


def test_parse_crear_trims_text_and_reads_optional_fields():
    parsed, error = _parse_crear(
        _body(
            departamento_id=' 20 ',
            localidad='  Centro  ',
            barrio_sector_urbanizacion='   ',
            hora_empadronamiento='08:15',
            numero_hoja='2',
            total_hojas=3,
            institucion=' Municipalidad ',
        )
    )

    assert error is None
    assert parsed['departamento_id'] == '20'
    assert parsed['localidad'] == 'Centro'
    assert parsed['barrio_sector_urbanizacion'] is None
    assert parsed['hora_empadronamiento'] == time(8, 15)
    assert parsed['numero_hoja'] == 2
    assert parsed['total_hojas'] == 3
    assert parsed['institucion'] == 'Municipalidad'


@pytest.mark.parametrize(
    ('field', 'value', 'message'),
    [
        ('emergencia_id', None, 'emergencia_id es obligatorio'),
        ('departamento_id', '2', 'departamento_id debe tener 2 caracteres'),
        ('provincia_id', '001', 'provincia_id debe tener 2 caracteres'),
        ('distrito_id', '', 'distrito_id es obligatorio'),
        ('fecha_empadronamiento', '01/10/2026', 'fecha_empadronamiento debe tener el formato'),
        ('hora_empadronamiento', '8pm', 'hora_empadronamiento debe tener el formato'),
        ('localidad', 'a' * 201, 'localidad no debe superar 200'),
        ('numero_hoja', 0, 'numero_hoja debe ser un número entero mayor que cero'),
        ('total_hojas', 'x', 'total_hojas debe ser un número entero mayor que cero'),
        ('evaluador_id', None, 'evaluador_id es obligatorio'),
        ('evaluador_id', '7.5', 'evaluador_id debe ser un número entero'),
        ('estado_registro_id', None, 'estado_registro_id es obligatorio'),
    ],
)
def test_parse_crear_rejects_invalid_fields(field, value, message):
    _parsed, error = _parse_crear(_body(**{field: value}))

    assert error is not None
    assert message in error


def test_parse_crear_rejects_total_hojas_lower_than_numero_hoja():
    _parsed, error = _parse_crear(_body(numero_hoja=3, total_hojas=2))

    assert error is not None
    assert 'total_hojas debe ser mayor o igual que numero_hoja' in error


def test_create_rejects_blank_user_before_saving():
    with pytest.raises(Formulario2AServiceError) as exc:
        Formulario2AService.create(**_create_kwargs(c_usuari_login='   '))

    assert 'usuario' in exc.value.message


def test_create_rejects_total_hojas_lower_than_numero_hoja():
    with pytest.raises(Formulario2AServiceError) as exc:
        Formulario2AService.create(**_create_kwargs(numero_hoja=3, total_hojas=1))

    assert exc.value.message == (
        'El campo total_hojas debe ser mayor o igual que numero_hoja'
    )


def test_create_rejects_unknown_emergencia():
    with (
        patch('app_sgbh.services.formulario_2a.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a.Emergencia') as emergencia,
        patch('app_sgbh.services.formulario_2a.Formulario2A') as formulario,
    ):
        emergencia.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.create(**_create_kwargs())

    assert exc.value.message == 'La emergencia indicada no existe'
    formulario.assert_not_called()


def test_create_rejects_unknown_distrito():
    with (
        patch('app_sgbh.services.formulario_2a.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a.Emergencia') as emergencia,
        patch('app_sgbh.services.formulario_2a.Distrito') as distrito,
        patch('app_sgbh.services.formulario_2a.Formulario2A') as formulario,
    ):
        emergencia.objects.filter.return_value.exists.return_value = True
        distrito.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.create(**_create_kwargs())

    assert exc.value.message == 'El distrito indicado no existe'
    distrito.objects.filter.assert_called_once_with(
        departamento_id='20',
        provincia_id='01',
        distrito_id='01',
    )
    formulario.assert_not_called()


def test_create_rejects_personal_that_is_not_evaluador():
    with (
        patch('app_sgbh.services.formulario_2a.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a.Emergencia') as emergencia,
        patch('app_sgbh.services.formulario_2a.Distrito') as distrito,
        patch('app_sgbh.services.formulario_2a.Personal') as personal,
        patch('app_sgbh.services.formulario_2a.Formulario2A') as formulario,
    ):
        emergencia.objects.filter.return_value.exists.return_value = True
        distrito.objects.filter.return_value.exists.return_value = True
        personal.objects.filter.return_value.first.return_value = SimpleNamespace(
            es_evaluador_edan=False,
        )

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.create(**_create_kwargs())

    assert exc.value.message == (
        'El personal indicado no puede registrarse como evaluador EDAN'
    )
    formulario.assert_not_called()


def test_create_rejects_unknown_estado_registro():
    with (
        patch('app_sgbh.services.formulario_2a.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a.Emergencia') as emergencia,
        patch('app_sgbh.services.formulario_2a.Distrito') as distrito,
        patch('app_sgbh.services.formulario_2a.Personal') as personal,
        patch('app_sgbh.services.formulario_2a.EstadoRegistro') as estado,
        patch('app_sgbh.services.formulario_2a.Formulario2A') as formulario,
    ):
        emergencia.objects.filter.return_value.exists.return_value = True
        distrito.objects.filter.return_value.exists.return_value = True
        personal.objects.filter.return_value.first.return_value = SimpleNamespace(
            es_evaluador_edan=True,
        )
        estado.objects.filter.return_value.exists.return_value = False

        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.create(**_create_kwargs())

    assert exc.value.message == 'El estado de registro indicado no existe'
    formulario.assert_not_called()


def test_create_saves_when_references_exist():
    with (
        patch('app_sgbh.services.formulario_2a.transaction.atomic'),
        patch('app_sgbh.services.formulario_2a.Emergencia') as emergencia,
        patch('app_sgbh.services.formulario_2a.Distrito') as distrito,
        patch('app_sgbh.services.formulario_2a.Personal') as personal,
        patch('app_sgbh.services.formulario_2a.EstadoRegistro') as estado,
        patch('app_sgbh.services.formulario_2a.Formulario2A') as formulario,
        patch(
            'app_sgbh.services.formulario_2a._formularios_busqueda',
        ) as busqueda,
    ):
        emergencia.objects.filter.return_value.exists.return_value = True
        distrito.objects.filter.return_value.exists.return_value = True
        personal.objects.filter.return_value.first.return_value = SimpleNamespace(
            es_evaluador_edan=True,
        )
        estado.objects.filter.return_value.exists.return_value = True
        formulario.return_value.pk = 15
        stored = busqueda.return_value.get.return_value

        result = Formulario2AService.create(
            **_create_kwargs(
                c_usuari_login=' mmedina ',
                hora_empadronamiento=time(8, 30),
                localidad='Centro',
                numero_hoja=2,
                total_hojas=4,
            )
        )

    assert result is stored
    formulario.assert_called_once_with(
        emergencia_id=4,
        departamento_id='20',
        provincia_id='01',
        distrito_id='01',
        fecha_empadronamiento=date(2026, 10, 1),
        hora_empadronamiento=time(8, 30),
        localidad='Centro',
        barrio_sector_urbanizacion=None,
        centro_poblado=None,
        caserio=None,
        anexo=None,
        calle_manzana=None,
        edificio_piso_dpto=None,
        otros_ubicacion=None,
        numero_hoja=2,
        total_hojas=4,
        institucion=None,
        evaluador_id=7,
        estado_registro_id=2,
        c_usuari_login='mmedina',
    )
    formulario.return_value.save.assert_called_once_with()
    busqueda.return_value.get.assert_called_once_with(pk=15)


def test_post_formularios_2a_returns_bad_request_when_emergencia_is_missing():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/formularios-2a/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_view.Formulario2AService.create',
        side_effect=Formulario2AServiceError('La emergencia indicada no existe'),
    ):
        response = Formulario2ACreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'La emergencia indicada no existe'


def test_post_formularios_2a_returns_created_formulario():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/formularios-2a/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    created = {'formulario_2a_id': 15}
    instance = object()

    with (
        patch(
            'app_sgbh.views.formulario_2a_view.Formulario2AService.create',
            return_value=instance,
        ) as create,
        patch(
            'app_sgbh.views.formulario_2a_view.Formulario2ABusquedaSerializer',
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = created
        response = Formulario2ACreateView.as_view()(request)

    assert response.status_code == 201
    assert response.data == created
    create.assert_called_once()
    serializer_cls.assert_called_once_with(instance)
    assert create.call_args.kwargs['c_usuari_login'] == 'mmedina'
    assert create.call_args.kwargs['emergencia_id'] == 4
    assert create.call_args.kwargs['numero_hoja'] == 1
