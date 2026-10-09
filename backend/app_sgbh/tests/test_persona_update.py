from datetime import date, datetime, timezone
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.persona import PersonaService, PersonaServiceError
from app_sgbh.views.persona_view import PersonaDetailView


class _DoesNotExist(Exception):
    pass


class _Row:
    def __init__(self):
        self.pk = 4
        self.c_usuari_login = 'creador'
        self.fecha_creacion = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.saved = False

    def save(self):
        self.saved = True


def _body(**overrides):
    data = {
        'tipo_documento_id': 2,
        'numero_documento': '12345678',
        'apellido_paterno': 'Medina',
        'apellido_materno': 'Lopez',
        'nombres': 'Mario',
        'fecha_nacimiento': '1990-05-12',
        'sexo': 'M',
        'telefono': '969000000',
        'correo': 'mario@example.com',
        'esta_activo': False,
    }
    data.update(overrides)
    return data


def _service_kwargs(**overrides):
    data = {
        'apellido_paterno': 'Medina',
        'apellido_materno': 'Lopez',
        'nombres': 'Mario',
        'fecha_nacimiento': date(1990, 5, 12),
        'sexo': 'M',
        'telefono': '969000000',
        'correo': 'mario@example.com',
        'tipo_documento_id': 2,
        'numero_documento': '12345678',
        'esta_activo': False,
    }
    data.update(overrides)
    return data


def _patch_update():
    return (
        patch('app_sgbh.services.persona.transaction.atomic'),
        patch('app_sgbh.services.persona.TipoDocumento'),
        patch('app_sgbh.services.persona.Persona'),
        patch(
            'app_sgbh.services.persona.timezone.now',
            return_value=datetime(2026, 10, 9, 18, 0, tzinfo=timezone.utc),
        ),
    )


def test_update_rejects_document_used_by_another_person():
    patches = _patch_update()
    with patches[0], patches[1] as tipo_documento, patches[2] as persona, patches[3]:
        row = _Row()
        persona.DoesNotExist = _DoesNotExist
        persona.objects.get.return_value = row
        tipo_documento.objects.filter.return_value.exists.return_value = True
        persona.objects.filter.return_value.exclude.return_value.exists.return_value = True

        with pytest.raises(PersonaServiceError) as exc:
            PersonaService.update(4, **_service_kwargs(numero_documento='  12345678  '))

    assert exc.value.conflict is True
    assert exc.value.message == (
        'Ya existe una persona con el tipo y número de documento indicados'
    )
    persona.objects.filter.return_value.exclude.assert_called_once_with(pk=4)
    assert row.saved is False


def test_update_rejects_identity_used_by_another_person():
    patches = _patch_update()
    with patches[0], patches[1] as tipo_documento, patches[2] as persona, patches[3]:
        row = _Row()
        persona.DoesNotExist = _DoesNotExist
        persona.objects.get.return_value = row
        tipo_documento.objects.filter.return_value.exists.return_value = True
        persona.objects.filter.return_value.exclude.return_value.exists.side_effect = [
            False,
            True,
        ]

        with pytest.raises(PersonaServiceError) as exc:
            PersonaService.update(4, **_service_kwargs())

    assert exc.value.conflict is True
    assert exc.value.message == (
        'Ya existe una persona con los mismos apellidos, nombres y fecha de nacimiento'
    )
    assert persona.objects.filter.return_value.exclude.call_count == 2
    assert row.saved is False


def test_update_keeps_creator_and_sets_modification_date():
    patches = _patch_update()
    with patches[0], patches[1] as tipo_documento, patches[2] as persona, patches[3]:
        row = _Row()
        persona.DoesNotExist = _DoesNotExist
        persona.objects.get.return_value = row
        tipo_documento.objects.filter.return_value.exists.return_value = True
        persona.objects.filter.return_value.exclude.return_value.exists.return_value = False
        stored = persona.objects.select_related.return_value.get.return_value

        result = PersonaService.update(4, **_service_kwargs())

    assert result is stored
    assert row.saved is True
    assert row.tipo_documento_id == 2
    assert row.numero_documento == '12345678'
    assert row.apellido_paterno == 'Medina'
    assert row.apellido_materno == 'Lopez'
    assert row.nombres == 'Mario'
    assert row.fecha_nacimiento == date(1990, 5, 12)
    assert row.sexo == 'M'
    assert row.telefono == '969000000'
    assert row.correo == 'mario@example.com'
    assert row.esta_activo is False
    assert row.fecha_modificacion == datetime(2026, 10, 9, 18, 0, tzinfo=timezone.utc)
    assert row.c_usuari_login == 'creador'
    assert row.fecha_creacion == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert persona.objects.filter.return_value.exclude.call_count == 2


def test_update_allows_clearing_the_document():
    patches = _patch_update()
    with patches[0], patches[1] as tipo_documento, patches[2] as persona, patches[3]:
        row = _Row()
        persona.DoesNotExist = _DoesNotExist
        persona.objects.get.return_value = row
        persona.objects.filter.return_value.exclude.return_value.exists.return_value = False

        PersonaService.update(
            4,
            **_service_kwargs(tipo_documento_id=None, numero_documento=None, esta_activo=True),
        )

    tipo_documento.objects.filter.assert_not_called()
    persona.objects.filter.return_value.exclude.assert_called_once_with(pk=4)
    assert row.tipo_documento_id is None
    assert row.numero_documento is None
    assert row.esta_activo is True
    assert row.saved is True


def test_update_rejects_missing_person():
    patches = _patch_update()
    with patches[0], patches[1], patches[2] as persona, patches[3]:
        persona.DoesNotExist = _DoesNotExist
        persona.objects.get.side_effect = _DoesNotExist

        with pytest.raises(PersonaServiceError) as exc:
            PersonaService.update(4, **_service_kwargs())

    assert exc.value.not_found is True
    assert exc.value.message == 'La persona indicada no existe'


def test_put_personas_returns_bad_request_for_invalid_id():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/personas/0/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = PersonaDetailView.as_view()(request, persona_id=0)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo persona_id debe ser un número entero'


def test_put_personas_returns_not_found():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/personas/4/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.persona_view.PersonaService.update',
        side_effect=PersonaServiceError(
            'La persona indicada no existe',
            not_found=True,
        ),
    ):
        response = PersonaDetailView.as_view()(request, persona_id=4)

    assert response.status_code == 404
    assert response.data['error'] == 'La persona indicada no existe'


def test_put_personas_returns_conflict_when_identity_exists():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/personas/4/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.persona_view.PersonaService.update',
        side_effect=PersonaServiceError(
            'Ya existe una persona con los mismos apellidos, nombres y fecha de nacimiento',
            conflict=True,
        ),
    ):
        response = PersonaDetailView.as_view()(request, persona_id=4)

    assert response.status_code == 409
    assert response.data['error'] == (
        'Ya existe una persona con los mismos apellidos, nombres y fecha de nacimiento'
    )


def test_put_personas_returns_updated_person():
    factory = APIRequestFactory()
    request = factory.put('/api/sgbh/personas/4/', _body(), format='json')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    updated = {'persona_id': 4, 'nombres': 'Mario'}
    instance = object()

    with (
        patch(
            'app_sgbh.views.persona_view.PersonaService.update',
            return_value=instance,
        ) as update,
        patch('app_sgbh.views.persona_view.PersonaSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = updated
        response = PersonaDetailView.as_view()(request, persona_id=4)

    assert response.status_code == 200
    assert response.data == updated
    update.assert_called_once()
    assert update.call_args.args == (4,)
    assert update.call_args.kwargs['numero_documento'] == '12345678'
    assert update.call_args.kwargs['esta_activo'] is False
    assert 'c_usuari_login' not in update.call_args.kwargs
    serializer_cls.assert_called_once_with(instance)
