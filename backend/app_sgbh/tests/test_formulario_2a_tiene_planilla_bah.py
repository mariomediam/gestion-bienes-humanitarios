from unittest.mock import patch

from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.formulario_2a import Formulario2AServiceError
from app_sgbh.views.planilla_entrega_view import Formulario2ATienePlanillaBahView


def _authenticate(request):
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))


def test_get_tiene_planilla_bah_devuelve_verdadero():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/9/tiene-planilla-bah/')
    _authenticate(request)

    with (
        patch(
            'app_sgbh.views.planilla_entrega_view.Formulario2AService.get',
            return_value=object(),
        ) as get_formulario,
        patch(
            'app_sgbh.views.planilla_entrega_view.formulario_tiene_planilla_bah',
            return_value=True,
        ) as tiene_planilla,
    ):
        response = Formulario2ATienePlanillaBahView.as_view()(
            request,
            formulario_2a_id=9,
        )

    assert response.status_code == 200
    assert response.data == {'tiene_planilla_bah': True}
    get_formulario.assert_called_once_with(9)
    tiene_planilla.assert_called_once_with(9, excluir_planilla_entrega_id=None)


def test_get_tiene_planilla_bah_puede_excluir_la_planilla():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/formularios-2a/9/tiene-planilla-bah/',
        {'excluir_planilla_entrega_id': '4'},
    )
    _authenticate(request)

    with (
        patch(
            'app_sgbh.views.planilla_entrega_view.Formulario2AService.get',
            return_value=object(),
        ),
        patch(
            'app_sgbh.views.planilla_entrega_view.formulario_tiene_planilla_bah',
            return_value=False,
        ) as tiene_planilla,
    ):
        response = Formulario2ATienePlanillaBahView.as_view()(
            request,
            formulario_2a_id=9,
        )

    assert response.status_code == 200
    assert response.data == {'tiene_planilla_bah': False}
    tiene_planilla.assert_called_once_with(9, excluir_planilla_entrega_id=4)


def test_get_tiene_planilla_bah_responde_404_cuando_no_existe():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/9/tiene-planilla-bah/')
    _authenticate(request)

    with (
        patch(
            'app_sgbh.views.planilla_entrega_view.Formulario2AService.get',
            side_effect=Formulario2AServiceError(
                'El formulario EDAN 2A indicado no existe',
                not_found=True,
            ),
        ),
        patch(
            'app_sgbh.views.planilla_entrega_view.formulario_tiene_planilla_bah',
        ) as tiene_planilla,
    ):
        response = Formulario2ATienePlanillaBahView.as_view()(
            request,
            formulario_2a_id=9,
        )

    assert response.status_code == 404
    assert response.data['error'] == 'El formulario EDAN 2A indicado no existe'
    tiene_planilla.assert_not_called()


def test_get_tiene_planilla_bah_rechaza_exclusion_invalida():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/formularios-2a/9/tiene-planilla-bah/',
        {'excluir_planilla_entrega_id': 'abc'},
    )
    _authenticate(request)

    with patch(
        'app_sgbh.views.planilla_entrega_view.formulario_tiene_planilla_bah',
    ) as tiene_planilla:
        response = Formulario2ATienePlanillaBahView.as_view()(
            request,
            formulario_2a_id=9,
        )

    assert response.status_code == 400
    assert (
        response.data['error']
        == 'El filtro excluir_planilla_entrega_id debe ser un número entero'
    )
    tiene_planilla.assert_not_called()


def test_get_tiene_planilla_bah_rechaza_id_fuera_de_rango():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/0/tiene-planilla-bah/')
    _authenticate(request)

    response = Formulario2ATienePlanillaBahView.as_view()(
        request,
        formulario_2a_id=0,
    )

    assert response.status_code == 400
    assert response.data['error'] == 'El campo formulario_2a_id debe ser un número entero'


def test_get_tiene_planilla_bah_oculta_errores_inesperados():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/9/tiene-planilla-bah/')
    _authenticate(request)

    with (
        patch(
            'app_sgbh.views.planilla_entrega_view.Formulario2AService.get',
            return_value=object(),
        ),
        patch(
            'app_sgbh.views.planilla_entrega_view.formulario_tiene_planilla_bah',
            side_effect=RuntimeError('sql'),
        ),
    ):
        response = Formulario2ATienePlanillaBahView.as_view()(
            request,
            formulario_2a_id=9,
        )

    assert response.status_code == 500
    assert response.data['error'] == (
        'No se pudo consultar si el formulario EDAN 2A tiene planilla BAH'
    )
