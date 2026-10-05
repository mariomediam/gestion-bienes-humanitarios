from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.models import Distrito
from app_sgbh.query_params import parse_distrito_id, parse_f_activo
from app_sgbh.serializers import DistritoSerializer
from app_sgbh.services.distrito import DistritoService
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.distrito_view import DistritoBuscarView, _parse_busqueda


def test_parse_busqueda_omits_every_filter_when_params_are_empty():
    parsed, error = _parse_busqueda({})

    assert error is None
    assert parsed == {
        'departamento_id': None,
        'provincia_id': None,
        'distrito_id': None,
        'distrito_nombre': None,
        'f_activo': None,
    }


def test_parse_busqueda_accepts_several_filters_together():
    parsed, error = _parse_busqueda(
        {
            'departamento_id': '20',
            'provincia_id': '01',
            'distrito_id': '01',
            'distrito_nombre': 'Piura',
            'f_activo': '1',
        }
    )

    assert error is None
    assert parsed == {
        'departamento_id': '20',
        'provincia_id': '01',
        'distrito_id': '01',
        'distrito_nombre': 'Piura',
        'f_activo': True,
    }


@pytest.mark.parametrize(
    ('parser', 'value', 'message'),
    [
        (parse_distrito_id, '001', 'distrito_id no debe superar 2 caracteres'),
        (parse_f_activo, 'si', 'f_activo debe ser 1, 0, true o false'),
    ],
)
def test_parse_busqueda_rejects_invalid_filters(parser, value, message):
    _parsed, error = parser(value)

    assert error is not None
    assert message in error


def test_search_returns_every_row_when_no_filter_is_sent():
    with patch('app_sgbh.services.distrito.Distrito') as distrito:
        queryset = distrito.objects.all.return_value
        queryset.order_by.return_value = 'rows'

        result = DistritoService.search()

    assert result == 'rows'
    distrito.objects.all.assert_called_once_with()
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('distrito_id')


def test_search_combines_filters_with_and():
    with patch('app_sgbh.services.distrito.Distrito') as distrito:
        queryset = distrito.objects.all.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = DistritoService.search(
            departamento_id='20',
            provincia_id='01',
            distrito_id='01',
            distrito_nombre='Piura',
            f_activo=True,
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'departamento_id': '20'}),
        ((), {'provincia_id': '01'}),
        ((), {'distrito_id': '01'}),
        ((), {'distrito_nombre__ilike_pattern': text_like_pattern('Piura')}),
        ((), {'f_activo': True}),
    ]


def test_serializer_returns_distrito_columns():
    distrito = Distrito(
        departamento_id='20',
        provincia_id='01',
        distrito_id='01',
        distrito_nombre='Piura',
        f_activo=True,
    )

    data = DistritoSerializer(distrito).data

    assert data == {
        'departamento_id': '20',
        'provincia_id': '01',
        'distrito_id': '01',
        'distrito_nombre': 'Piura',
        'f_activo': True,
    }


def test_get_distritos_buscar_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/distritos/buscar/',
        {
            'departamento_id': '20',
            'provincia_id': '01',
            'distrito_nombre': 'Piura',
            'f_activo': 'true',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'distrito_id': '01', 'distrito_nombre': 'Piura'}]

    with (
        patch(
            'app_sgbh.views.distrito_view.DistritoService.search',
            return_value='queryset',
        ) as search,
        patch('app_sgbh.views.distrito_view.DistritoSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = DistritoBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        departamento_id='20',
        provincia_id='01',
        distrito_id=None,
        distrito_nombre='Piura',
        f_activo=True,
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_distritos_buscar_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/distritos/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.distrito_view.DistritoService.search',
            return_value='queryset',
        ) as search,
        patch('app_sgbh.views.distrito_view.DistritoSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = DistritoBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        departamento_id=None,
        provincia_id=None,
        distrito_id=None,
        distrito_nombre=None,
        f_activo=None,
    )


def test_get_distritos_buscar_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/distritos/buscar/', {'f_activo': 'si'})
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = DistritoBuscarView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El filtro f_activo debe ser 1, 0, true o false'
