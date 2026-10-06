from datetime import date, datetime, time
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.models import Formulario2A
from app_sgbh.serializers.formulario_2a import Formulario2ADetalleSerializer
from app_sgbh.services.formulario_2a import (
    Formulario2AService,
    Formulario2AServiceError,
)
from app_sgbh.views.formulario_2a_view import Formulario2ADetailView


def _formulario():
    return SimpleNamespace(
        formulario_2a_id=3,
        emergencia_id=8,
        departamento_id='20',
        provincia_id='01',
        distrito_id='01',
        fecha_empadronamiento=date(2026, 3, 1),
        hora_empadronamiento=time(8, 30),
        localidad='Centro',
        barrio_sector_urbanizacion='Santa Rosa',
        centro_poblado=None,
        caserio=None,
        anexo=None,
        calle_manzana=None,
        edificio_piso_dpto=None,
        otros_ubicacion=None,
        numero_hoja=1,
        total_hojas=2,
        institucion=None,
        evaluador_id=4,
        estado_registro_id=1,
        c_usuari_login='mmedina',
        fecha_creacion=datetime(2026, 3, 1, 8, 0),
        fecha_modificacion=None,
        distrito_nombre='Piura',
        emergencia=SimpleNamespace(
            codigo_sinpad='45821',
            tipo_peligro_id=2,
            tipo_peligro=SimpleNamespace(nombre='Inundación'),
        ),
        evaluador=SimpleNamespace(
            apellido_paterno='Perez',
            apellido_materno='Lopez',
            nombres='Ana',
        ),
    )


def test_get_returns_the_formulario():
    queryset = MagicMock()
    stored = object()
    queryset.get.return_value = stored

    with patch(
        'app_sgbh.services.formulario_2a._formularios_con_distrito',
        return_value=queryset,
    ):
        result = Formulario2AService.get(3)

    assert result is stored
    queryset.get.assert_called_once_with(pk=3)


def test_get_rejects_unknown_formulario():
    queryset = MagicMock()
    queryset.get.side_effect = Formulario2A.DoesNotExist

    with patch(
        'app_sgbh.services.formulario_2a._formularios_con_distrito',
        return_value=queryset,
    ):
        with pytest.raises(Formulario2AServiceError) as exc:
            Formulario2AService.get(3)

    assert exc.value.not_found is True
    assert exc.value.message == 'El formulario EDAN 2A indicado no existe'


def test_detalle_serializer_returns_the_query_columns():
    data = Formulario2ADetalleSerializer(_formulario()).data

    assert data['formulario_2a_id'] == 3
    assert data['emergencia_id'] == 8
    assert data['codigo_sinpad'] == '45821'
    assert data['tipo_peligro_id'] == 2
    assert data['nombre_tipo_peligro'] == 'Inundación'
    assert data['distrito_nombre'] == 'Piura'
    assert data['evaluador_nombre'] == 'Perez Lopez Ana'
    assert 'viviendas' not in data


def test_get_formulario_2a_returns_the_row():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/3/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    instance = _formulario()

    with patch(
        'app_sgbh.views.formulario_2a_view.Formulario2AService.get',
        return_value=instance,
    ) as get:
        response = Formulario2ADetailView.as_view()(request, formulario_2a_id=3)

    assert response.status_code == 200
    assert response.data['formulario_2a_id'] == 3
    assert response.data['evaluador_nombre'] == 'Perez Lopez Ana'
    get.assert_called_once_with(3)


def test_get_formulario_2a_returns_not_found():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/3/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_view.Formulario2AService.get',
        side_effect=Formulario2AServiceError(
            'El formulario EDAN 2A indicado no existe',
            not_found=True,
        ),
    ):
        response = Formulario2ADetailView.as_view()(request, formulario_2a_id=3)

    assert response.status_code == 404
    assert response.data['error'] == 'El formulario EDAN 2A indicado no existe'


def test_get_formulario_2a_rejects_id_out_of_range():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/0/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = Formulario2ADetailView.as_view()(request, formulario_2a_id=0)

    assert response.status_code == 400
    assert response.data['error'] == (
        'El campo formulario_2a_id debe ser un número entero'
    )


def test_get_formulario_2a_returns_server_error():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/3/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_view.Formulario2AService.get',
        side_effect=RuntimeError('db'),
    ):
        response = Formulario2ADetailView.as_view()(request, formulario_2a_id=3)

    assert response.status_code == 500
    assert response.data['error'] == 'No se pudo obtener el formulario EDAN 2A'
