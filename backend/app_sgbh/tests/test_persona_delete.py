from unittest.mock import patch

import pytest
from django.db.models import ProtectedError
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.persona import PersonaService, PersonaServiceError
from app_sgbh.views.persona_view import PersonaDetailView


class _DoesNotExist(Exception):
    pass


def _patch_delete():
    return (
        patch('app_sgbh.services.persona.transaction.atomic'),
        patch('app_sgbh.services.persona.Persona'),
        patch('app_sgbh.services.persona.Formulario2AIntegrante'),
    )


def test_delete_rejects_person_referenced_by_integrante():
    patches = _patch_delete()
    with patches[0], patches[1] as persona, patches[2] as integrante:
        row = persona.objects.get.return_value
        persona.DoesNotExist = _DoesNotExist
        integrante.objects.filter.return_value.exists.return_value = True

        with pytest.raises(PersonaServiceError) as exc:
            PersonaService.delete(4)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar la persona porque tiene integrantes asociados'
    )
    integrante.objects.filter.assert_called_once_with(persona_id=4)
    row.delete.assert_not_called()


def test_delete_removes_person_without_integrantes():
    patches = _patch_delete()
    with patches[0], patches[1] as persona, patches[2] as integrante:
        row = persona.objects.get.return_value
        persona.DoesNotExist = _DoesNotExist
        integrante.objects.filter.return_value.exists.return_value = False

        PersonaService.delete(4)

    row.delete.assert_called_once_with()


def test_delete_rejects_missing_person():
    patches = _patch_delete()
    with patches[0], patches[1] as persona, patches[2] as integrante:
        persona.DoesNotExist = _DoesNotExist
        persona.objects.get.side_effect = _DoesNotExist

        with pytest.raises(PersonaServiceError) as exc:
            PersonaService.delete(4)

    assert exc.value.not_found is True
    assert exc.value.message == 'La persona indicada no existe'
    integrante.objects.filter.assert_not_called()


def test_delete_rejects_when_database_protects_related_integrante():
    patches = _patch_delete()
    with patches[0], patches[1] as persona, patches[2] as integrante:
        row = persona.objects.get.return_value
        persona.DoesNotExist = _DoesNotExist
        integrante.objects.filter.return_value.exists.return_value = False
        row.delete.side_effect = ProtectedError('protected', {object()})

        with pytest.raises(PersonaServiceError) as exc:
            PersonaService.delete(4)

    assert exc.value.conflict is True
    assert exc.value.message == (
        'No se puede eliminar la persona porque tiene integrantes asociados'
    )


def test_delete_personas_returns_conflict_when_integrante_exists():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/personas/4/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.persona_view.PersonaService.delete',
        side_effect=PersonaServiceError(
            'No se puede eliminar la persona porque tiene integrantes asociados',
            conflict=True,
        ),
    ):
        response = PersonaDetailView.as_view()(request, persona_id=4)

    assert response.status_code == 409
    assert response.data['error'] == (
        'No se puede eliminar la persona porque tiene integrantes asociados'
    )


def test_delete_personas_returns_no_content():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/personas/4/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch('app_sgbh.views.persona_view.PersonaService.delete') as delete:
        response = PersonaDetailView.as_view()(request, persona_id=4)

    assert response.status_code == 204
    assert response.data is None
    delete.assert_called_once_with(4)


def test_delete_personas_rejects_invalid_id():
    factory = APIRequestFactory()
    request = factory.delete('/api/sgbh/personas/0/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch('app_sgbh.views.persona_view.PersonaService.delete') as delete:
        response = PersonaDetailView.as_view()(request, persona_id=0)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo persona_id debe ser un número entero'
    delete.assert_not_called()
