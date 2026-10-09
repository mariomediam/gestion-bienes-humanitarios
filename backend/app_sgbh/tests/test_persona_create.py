from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers import (
    PersonaCreateSerializer,
    PersonaSerializer,
    first_error_message,
)
from app_sgbh.services.persona import PersonaService, PersonaServiceError
from app_sgbh.views.persona_view import PersonaCreateView


def _parse_crear(data):
    serializer = PersonaCreateSerializer(data=data)
    if serializer.is_valid():
        return serializer.validated_data, None
    return None, first_error_message(serializer.errors)


def _body(**overrides):
    data = {
        'apellido_paterno': 'Medina',
        'apellido_materno': 'Lopez',
        'nombres': 'Mario',
        'fecha_nacimiento': '1990-05-12',
        'sexo': 'M',
        'telefono': '969000000',
        'correo': 'mario@example.com',
    }
    data.update(overrides)
    return data


def test_parse_crear_accepts_required_fields_and_defaults():
    parsed, error = _parse_crear(_body())

    assert error is None
    assert parsed == {
        'tipo_documento_id': None,
        'numero_documento': None,
        'apellido_paterno': 'Medina',
        'apellido_materno': 'Lopez',
        'nombres': 'Mario',
        'fecha_nacimiento': date(1990, 5, 12),
        'sexo': 'M',
        'telefono': '969000000',
        'correo': 'mario@example.com',
        'esta_activo': True,
    }


def test_parse_crear_trims_text_and_reads_optional_fields():
    parsed, error = _parse_crear(
        _body(
            tipo_documento_id='2',
            numero_documento='  12345678  ',
            apellido_paterno='  Medina  ',
            sexo=' F ',
            esta_activo=False,
        )
    )

    assert error is None
    assert parsed['tipo_documento_id'] == 2
    assert parsed['numero_documento'] == '12345678'
    assert parsed['apellido_paterno'] == 'Medina'
    assert parsed['sexo'] == 'F'
    assert parsed['esta_activo'] is False


def test_parse_crear_treats_blank_document_as_empty():
    parsed, error = _parse_crear(
        _body(tipo_documento_id='', numero_documento='   ')
    )

    assert error is None
    assert parsed['tipo_documento_id'] is None
    assert parsed['numero_documento'] is None


@pytest.mark.parametrize(
    ('field', 'value', 'message'),
    [
        ('apellido_paterno', '   ', 'apellido_paterno es obligatorio'),
        ('apellido_materno', '', 'apellido_materno es obligatorio'),
        ('nombres', None, 'nombres es obligatorio'),
        ('nombres', 'N' * 151, 'nombres no debe superar 150'),
        ('fecha_nacimiento', '12/05/1990', 'fecha_nacimiento debe tener el formato'),
        ('sexo', '', 'sexo es obligatorio'),
        ('sexo', 'MF', 'sexo debe tener 1 carácter'),
        ('telefono', 'T' * 51, 'telefono no debe superar 50'),
        ('correo', '', 'correo es obligatorio'),
        ('numero_documento', 'D' * 21, 'numero_documento no debe superar 20'),
        ('tipo_documento_id', '2.5', 'tipo_documento_id debe ser un número entero'),
        ('tipo_documento_id', 40000, 'tipo_documento_id debe ser un número entero'),
        ('esta_activo', 'si', 'esta_activo debe ser 1, 0, true o false'),
    ],
)
def test_parse_crear_rejects_invalid_fields(field, value, message):
    _parsed, error = _parse_crear(_body(**{field: value}))

    assert error is not None
    assert message in error


@pytest.mark.parametrize(
    'overrides',
    [
        {'tipo_documento_id': 1},
        {'numero_documento': '12345678'},
    ],
)
def test_parse_crear_rejects_incomplete_document(overrides):
    _parsed, error = _parse_crear(_body(**overrides))

    assert error is not None
    assert 'tipo_documento_id y numero_documento' in error


def test_create_rejects_blank_user():
    with pytest.raises(PersonaServiceError) as exc:
        PersonaService.create(**_service_kwargs(c_usuari_login='   '))

    assert exc.value.message == 'No se pudo identificar al usuario'


def test_create_rejects_incomplete_document_before_saving():
    with patch('app_sgbh.services.persona.Persona') as persona:
        with pytest.raises(PersonaServiceError) as exc:
            PersonaService.create(**_service_kwargs(numero_documento='12345678'))

    assert 'tipo_documento_id y numero_documento' in exc.value.message
    persona.assert_not_called()


def test_create_rejects_unknown_tipo_documento():
    with (
        patch('app_sgbh.services.persona.transaction.atomic'),
        patch('app_sgbh.services.persona.TipoDocumento') as tipo_documento,
        patch('app_sgbh.services.persona.Persona') as persona,
    ):
        tipo_documento.objects.filter.return_value.exists.return_value = False

        with pytest.raises(PersonaServiceError) as exc:
            PersonaService.create(
                **_service_kwargs(tipo_documento_id=9, numero_documento='12345678')
            )

    assert exc.value.message == 'El tipo de documento indicado no existe'
    persona.assert_not_called()


def test_create_saves_without_document():
    with (
        patch('app_sgbh.services.persona.transaction.atomic'),
        patch('app_sgbh.services.persona.TipoDocumento') as tipo_documento,
        patch('app_sgbh.services.persona.Persona') as persona,
    ):
        persona.return_value.pk = 4
        persona.objects.filter.return_value.exists.return_value = False
        stored = persona.objects.select_related.return_value.get.return_value

        result = PersonaService.create(**_service_kwargs(c_usuari_login=' mmedina '))

    assert result is stored
    tipo_documento.objects.filter.assert_not_called()
    persona.objects.filter.assert_called_once_with(
        apellido_paterno__iexact='Medina',
        apellido_materno__iexact='Lopez',
        nombres__iexact='Mario',
        fecha_nacimiento=date(1990, 5, 12),
    )
    persona.assert_called_once_with(
        tipo_documento_id=None,
        numero_documento=None,
        apellido_paterno='Medina',
        apellido_materno='Lopez',
        nombres='Mario',
        fecha_nacimiento=date(1990, 5, 12),
        sexo='M',
        telefono='969000000',
        correo='mario@example.com',
        esta_activo=True,
        c_usuari_login='mmedina',
    )
    persona.return_value.save.assert_called_once_with()


def test_create_saves_with_document():
    with (
        patch('app_sgbh.services.persona.transaction.atomic'),
        patch('app_sgbh.services.persona.TipoDocumento') as tipo_documento,
        patch('app_sgbh.services.persona.Persona') as persona,
    ):
        tipo_documento.objects.filter.return_value.exists.return_value = True
        persona.objects.filter.return_value.exists.return_value = False
        persona.return_value.pk = 8

        PersonaService.create(
            **_service_kwargs(
                tipo_documento_id=2,
                numero_documento='  12345678  ',
                esta_activo=False,
            )
        )

    tipo_documento.objects.filter.assert_called_once_with(pk=2)
    assert persona.call_args.kwargs['tipo_documento_id'] == 2
    assert persona.call_args.kwargs['numero_documento'] == '12345678'
    assert persona.call_args.kwargs['esta_activo'] is False


def test_create_rejects_existing_document():
    with (
        patch('app_sgbh.services.persona.transaction.atomic'),
        patch('app_sgbh.services.persona.TipoDocumento') as tipo_documento,
        patch('app_sgbh.services.persona.Persona') as persona,
    ):
        tipo_documento.objects.filter.return_value.exists.return_value = True
        persona.objects.filter.return_value.exists.return_value = True

        with pytest.raises(PersonaServiceError) as exc:
            PersonaService.create(
                **_service_kwargs(
                    tipo_documento_id=2,
                    numero_documento='  12345678  ',
                )
            )

    assert exc.value.conflict is True
    assert exc.value.message == (
        'Ya existe una persona con el tipo y número de documento indicados'
    )
    persona.objects.filter.assert_called_once_with(
        tipo_documento_id=2,
        numero_documento__iexact='12345678',
    )
    persona.assert_not_called()


def test_create_rejects_existing_identity():
    with (
        patch('app_sgbh.services.persona.transaction.atomic'),
        patch('app_sgbh.services.persona.Persona') as persona,
    ):
        persona.objects.filter.return_value.exists.return_value = True

        with pytest.raises(PersonaServiceError) as exc:
            PersonaService.create(
                **_service_kwargs(
                    apellido_paterno='  medina  ',
                    apellido_materno='lopez',
                    nombres='MARIO',
                )
            )

    assert exc.value.conflict is True
    assert exc.value.message == (
        'Ya existe una persona con los mismos apellidos, nombres y fecha de nacimiento'
    )
    persona.objects.filter.assert_called_once_with(
        apellido_paterno__iexact='medina',
        apellido_materno__iexact='lopez',
        nombres__iexact='MARIO',
        fecha_nacimiento=date(1990, 5, 12),
    )
    persona.assert_not_called()


def test_create_rejects_existing_identity_when_document_is_new():
    with (
        patch('app_sgbh.services.persona.transaction.atomic'),
        patch('app_sgbh.services.persona.TipoDocumento') as tipo_documento,
        patch('app_sgbh.services.persona.Persona') as persona,
    ):
        tipo_documento.objects.filter.return_value.exists.return_value = True
        persona.objects.filter.return_value.exists.side_effect = [False, True]

        with pytest.raises(PersonaServiceError) as exc:
            PersonaService.create(
                **_service_kwargs(tipo_documento_id=2, numero_documento='12345678')
            )

    assert exc.value.conflict is True
    assert 'apellidos, nombres y fecha de nacimiento' in exc.value.message
    assert persona.objects.filter.call_count == 2
    persona.assert_not_called()


def test_persona_serializer_returns_tipo_documento_name():
    persona = SimpleNamespace(
        persona_id=4,
        tipo_documento_id=2,
        tipo_documento=SimpleNamespace(nombre='DNI'),
        numero_documento='12345678',
        apellido_paterno='Medina',
        apellido_materno='Lopez',
        nombres='Mario',
        fecha_nacimiento=date(1990, 5, 12),
        sexo='M',
        telefono='969000000',
        correo='mario@example.com',
        esta_activo=True,
        c_usuari_login='mmedina',
        fecha_creacion='2026-10-09T12:00:00Z',
        fecha_modificacion=None,
    )

    data = PersonaSerializer(persona).data

    assert data['persona_id'] == 4
    assert data['nombre_tipo_documento'] == 'DNI'
    assert data['fecha_modificacion'] is None


def test_persona_serializer_returns_null_tipo_documento_name():
    persona = SimpleNamespace(
        persona_id=4,
        tipo_documento_id=None,
        tipo_documento=None,
        numero_documento=None,
        apellido_paterno='Medina',
        apellido_materno='Lopez',
        nombres='Mario',
        fecha_nacimiento=date(1990, 5, 12),
        sexo='M',
        telefono='969000000',
        correo='mario@example.com',
        esta_activo=True,
        c_usuari_login='mmedina',
        fecha_creacion='2026-10-09T12:00:00Z',
        fecha_modificacion=None,
    )

    data = PersonaSerializer(persona).data

    assert data['nombre_tipo_documento'] is None
    assert data['numero_documento'] is None


def test_post_personas_returns_bad_request_when_document_is_incomplete():
    factory = APIRequestFactory()
    request = factory.post(
        '/api/sgbh/personas/',
        _body(numero_documento='12345678'),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = PersonaCreateView.as_view()(request)

    assert response.status_code == 400
    assert 'tipo_documento_id y numero_documento' in response.data['error']


def test_post_personas_returns_bad_request_when_tipo_documento_does_not_exist():
    factory = APIRequestFactory()
    request = factory.post(
        '/api/sgbh/personas/',
        _body(tipo_documento_id=9, numero_documento='12345678'),
        format='json',
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.persona_view.PersonaService.create',
        side_effect=PersonaServiceError('El tipo de documento indicado no existe'),
    ):
        response = PersonaCreateView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El tipo de documento indicado no existe'


def test_post_personas_returns_conflict_when_person_already_exists():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/personas/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.persona_view.PersonaService.create',
        side_effect=PersonaServiceError(
            'Ya existe una persona con los mismos apellidos, nombres y fecha de nacimiento',
            conflict=True,
        ),
    ):
        response = PersonaCreateView.as_view()(request)

    assert response.status_code == 409
    assert response.data['error'] == (
        'Ya existe una persona con los mismos apellidos, nombres y fecha de nacimiento'
    )


def test_post_personas_returns_created_person():
    factory = APIRequestFactory()
    request = factory.post('/api/sgbh/personas/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    created = {'persona_id': 4, 'nombres': 'Mario'}
    instance = object()

    with (
        patch(
            'app_sgbh.views.persona_view.PersonaService.create',
            return_value=instance,
        ) as create,
        patch('app_sgbh.views.persona_view.PersonaSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = created
        response = PersonaCreateView.as_view()(request)

    assert response.status_code == 201
    assert response.data == created
    create.assert_called_once()
    serializer_cls.assert_called_once_with(instance)
    assert create.call_args.kwargs['c_usuari_login'] == 'mmedina'
    assert create.call_args.kwargs['apellido_paterno'] == 'Medina'
    assert create.call_args.kwargs['tipo_documento_id'] is None


def _service_kwargs(**overrides):
    data = {
        'apellido_paterno': 'Medina',
        'apellido_materno': 'Lopez',
        'nombres': 'Mario',
        'fecha_nacimiento': date(1990, 5, 12),
        'sexo': 'M',
        'telefono': '969000000',
        'correo': 'mario@example.com',
        'c_usuari_login': 'mmedina',
    }
    data.update(overrides)
    return data
