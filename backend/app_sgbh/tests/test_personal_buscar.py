from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import (
    parse_es_encargado_almacen,
    parse_es_evaluador_edan,
    parse_personal_id,
)
from app_sgbh.services.personal import PersonalService
from app_sgbh.views.personal_view import (
    PersonalBuscarView,
    PersonalEncargadosAlmacenBuscarView,
    PersonalEvaluadoresBuscarView,
    _parse_busqueda,
)


def test_parse_busqueda_omits_every_filter_when_params_are_empty():
    parsed, error = _parse_busqueda({})

    assert error is None
    assert parsed == {
        'personal_id': None,
        'es_evaluador_edan': None,
        'es_encargado_almacen': None,
        'esta_activo': None,
    }


def test_parse_busqueda_accepts_several_filters_together():
    parsed, error = _parse_busqueda(
        {
            'personal_id': '12',
            'es_evaluador_edan': '1',
            'es_encargado_almacen': 'false',
            'esta_activo': 'true',
        }
    )

    assert error is None
    assert parsed == {
        'personal_id': 12,
        'es_evaluador_edan': True,
        'es_encargado_almacen': False,
        'esta_activo': True,
    }


@pytest.mark.parametrize(
    ('parser', 'value', 'message'),
    [
        (parse_personal_id, 'abc', 'personal_id debe ser un número entero'),
        (parse_personal_id, '40000', 'personal_id debe ser un número entero'),
        (parse_es_evaluador_edan, 'si', 'es_evaluador_edan debe ser 1, 0, true o false'),
        (
            parse_es_encargado_almacen,
            '2',
            'es_encargado_almacen debe ser 1, 0, true o false',
        ),
    ],
)
def test_parse_busqueda_rejects_invalid_filters(parser, value, message):
    _parsed, error = parser(value)

    assert error is not None
    assert message in error


def test_search_returns_every_row_when_no_filter_is_sent():
    with patch('app_sgbh.services.personal.Personal') as personal:
        queryset = personal.objects.all.return_value
        queryset.order_by.return_value = 'rows'

        result = PersonalService.search()

    assert result == 'rows'
    personal.objects.all.assert_called_once_with()
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with(
        'apellido_paterno',
        'apellido_materno',
        'nombres',
        'personal_id',
    )


def test_search_combines_filters_with_and():
    with patch('app_sgbh.services.personal.Personal') as personal:
        queryset = personal.objects.all.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = PersonalService.search(
            personal_id=4,
            es_evaluador_edan=True,
            es_encargado_almacen=False,
            esta_activo=True,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'personal_id': 4}),
        ((), {'es_evaluador_edan': True}),
        ((), {'es_encargado_almacen': False}),
        ((), {'esta_activo': True}),
    ]


def test_get_personal_buscar_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/personal/buscar/',
        {'es_evaluador_edan': '1', 'esta_activo': '1'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'personal_id': 1, 'nombres': 'Ana'}]

    with (
        patch(
            'app_sgbh.views.personal_view.PersonalService.search',
            return_value='queryset',
        ) as search,
        patch('app_sgbh.views.personal_view.PersonalSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = PersonalBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        personal_id=None,
        es_evaluador_edan=True,
        es_encargado_almacen=None,
        esta_activo=True,
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_evaluadores_buscar_forces_evaluador_and_keeps_other_filters():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/personal/buscar/evaluadores/',
        {'personal_id': '3', 'esta_activo': '1', 'es_encargado_almacen': '0'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.personal_view.PersonalService.search',
            return_value='queryset',
        ) as search,
        patch('app_sgbh.views.personal_view.PersonalSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = PersonalEvaluadoresBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        personal_id=3,
        es_encargado_almacen=False,
        esta_activo=True,
        es_evaluador_edan=True,
    )


def test_get_evaluadores_buscar_returns_every_evaluator_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/personal/buscar/evaluadores/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.personal_view.PersonalService.search',
            return_value='queryset',
        ) as search,
        patch('app_sgbh.views.personal_view.PersonalSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = PersonalEvaluadoresBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        personal_id=None,
        es_encargado_almacen=None,
        esta_activo=None,
        es_evaluador_edan=True,
    )


def test_get_encargados_almacen_buscar_forces_encargado_and_keeps_other_filters():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/personal/buscar/encargados-almacen/',
        {'es_evaluador_edan': 'true', 'esta_activo': 'false'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.personal_view.PersonalService.search',
            return_value='queryset',
        ) as search,
        patch('app_sgbh.views.personal_view.PersonalSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = PersonalEncargadosAlmacenBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        personal_id=None,
        es_evaluador_edan=True,
        esta_activo=False,
        es_encargado_almacen=True,
    )


def test_get_encargados_almacen_buscar_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/personal/buscar/encargados-almacen/',
        {'personal_id': 'x'},
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = PersonalEncargadosAlmacenBuscarView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El filtro personal_id debe ser un número entero'


def test_get_personal_buscar_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/personal/buscar/', {'personal_id': 'x'})
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = PersonalBuscarView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El filtro personal_id debe ser un número entero'
