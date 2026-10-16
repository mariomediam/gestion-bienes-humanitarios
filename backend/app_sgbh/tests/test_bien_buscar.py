from types import SimpleNamespace
from unittest.mock import patch

import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.query_params import (
    parse_bien_id,
    parse_categoria_bien_id,
    parse_codigo_bien,
    parse_nombre_bien,
    parse_unidad_medida_id,
)
from app_sgbh.serializers import BienBusquedaSerializer
from app_sgbh.services.bien import BienService
from app_sgbh.text_search import text_like_pattern
from app_sgbh.views.bien_view import BienBuscarView, _parse_busqueda


def test_parse_busqueda_omits_every_filter_when_params_are_empty():
    parsed, error = _parse_busqueda({})

    assert error is None
    assert parsed == {
        'bien_id': None,
        'categoria_bien_id': None,
        'unidad_medida_id': None,
        'codigo': None,
        'nombre': None,
    }


def test_parse_busqueda_accepts_filters_and_trims_text():
    parsed, error = _parse_busqueda(
        {
            'bien_id': '4',
            'categoria_bien_id': '2',
            'unidad_medida_id': '3',
            'codigo': '  CLAV-01  ',
            'nombre': '  clavos madera  ',
        }
    )

    assert error is None
    assert parsed == {
        'bien_id': 4,
        'categoria_bien_id': 2,
        'unidad_medida_id': 3,
        'codigo': 'CLAV-01',
        'nombre': 'clavos madera',
    }


@pytest.mark.parametrize(
    ('parser', 'value', 'message'),
    [
        (parse_bien_id, 'abc', 'bien_id debe ser un número entero'),
        (parse_bien_id, '3000000000', 'bien_id debe ser un número entero'),
        (
            parse_categoria_bien_id,
            '40000',
            'categoria_bien_id debe ser un número entero',
        ),
        (
            parse_unidad_medida_id,
            '2.5',
            'unidad_medida_id debe ser un número entero',
        ),
        (parse_codigo_bien, 'C' * 51, 'codigo no debe superar 50'),
        (parse_nombre_bien, 'N' * 251, 'nombre no debe superar 250'),
    ],
)
def test_parsers_reject_invalid_filters(parser, value, message):
    _parsed, error = parser(value)

    assert error is not None
    assert message in error


def test_search_returns_every_row_when_no_filter_is_sent():
    with patch('app_sgbh.services.bien.Bien') as bien:
        queryset = bien.objects.select_related.return_value
        queryset.order_by.return_value = 'rows'

        result = BienService.search()

    assert result == 'rows'
    bien.objects.select_related.assert_called_once_with(
        'categoria_bien',
        'unidad_medida',
    )
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('nombre')


def test_search_combines_exact_and_name_filters():
    with patch('app_sgbh.services.bien.Bien') as bien:
        queryset = bien.objects.select_related.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = BienService.search(
            bien_id=4,
            categoria_bien_id=2,
            unidad_medida_id=3,
            codigo='CLAV-01',
            nombre='clavos madera',
        )

    assert result == 'rows'
    assert queryset.filter.call_args_list == [
        ((), {'bien_id': 4}),
        ((), {'categoria_bien_id': 2}),
        ((), {'unidad_medida_id': 3}),
        ((), {'codigo': 'CLAV-01'}),
        ((), {'nombre__ilike_pattern': text_like_pattern('clavos madera')}),
    ]
    assert text_like_pattern('clavos madera') == '%clavos%madera%'


def test_bien_busqueda_serializer_includes_category_and_unit():
    bien = SimpleNamespace(
        bien_id=4,
        categoria_bien_id=2,
        unidad_medida_id=3,
        codigo='CLAV-01',
        nombre='Clavos de madera',
        descripcion='Clavos para madera',
        orden_impresion=1,
        esta_activo=True,
        visible_planilla=True,
        categoria_bien=SimpleNamespace(codigo='HERR', nombre='Herramientas'),
        unidad_medida=SimpleNamespace(
            codigo='KG',
            nombre='Kilogramo',
            abreviatura='kg',
        ),
    )

    data = BienBusquedaSerializer(bien).data

    assert data['categoria_bien_codigo'] == 'HERR'
    assert data['categoria_bien_nombre'] == 'Herramientas'
    assert data['unidad_medida_codigo'] == 'KG'
    assert data['unidad_medida_nombre'] == 'Kilogramo'
    assert data['unidad_medida_abreviatura'] == 'kg'


def test_bien_busqueda_serializer_returns_null_optional_fields():
    bien = SimpleNamespace(
        bien_id=4,
        categoria_bien_id=2,
        unidad_medida_id=3,
        codigo='CLAV-01',
        nombre='Clavos de madera',
        descripcion=None,
        orden_impresion=None,
        esta_activo=True,
        visible_planilla=False,
        categoria_bien=SimpleNamespace(codigo='HERR', nombre='Herramientas'),
        unidad_medida=SimpleNamespace(
            codigo='KG',
            nombre='Kilogramo',
            abreviatura=None,
        ),
    )

    data = BienBusquedaSerializer(bien).data

    assert data['descripcion'] is None
    assert data['orden_impresion'] is None
    assert data['unidad_medida_abreviatura'] is None


def test_get_bienes_buscar_returns_rows():
    factory = APIRequestFactory()
    request = factory.get(
        '/api/sgbh/bienes/buscar/',
        {
            'bien_id': '4',
            'categoria_bien_id': '2',
            'unidad_medida_id': '3',
            'codigo': 'CLAV-01',
            'nombre': 'clavos madera',
        },
    )
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'bien_id': 4, 'nombre': 'Clavos de madera'}]

    with (
        patch(
            'app_sgbh.views.bien_view.BienService.search',
            return_value='queryset',
        ) as search,
        patch('app_sgbh.views.bien_view.BienBusquedaSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = BienBuscarView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    search.assert_called_once_with(
        bien_id=4,
        categoria_bien_id=2,
        unidad_medida_id=3,
        codigo='CLAV-01',
        nombre='clavos madera',
    )
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_bienes_buscar_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/bienes/buscar/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.bien_view.BienService.search',
            return_value='queryset',
        ) as search,
        patch('app_sgbh.views.bien_view.BienBusquedaSerializer') as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = BienBuscarView.as_view()(request)

    assert response.status_code == 200
    search.assert_called_once_with(
        bien_id=None,
        categoria_bien_id=None,
        unidad_medida_id=None,
        codigo=None,
        nombre=None,
    )


def test_get_bienes_buscar_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/bienes/buscar/', {'bien_id': 'abc'})
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = BienBuscarView.as_view()(request)

    assert response.status_code == 400
    assert 'bien_id debe ser un número entero' in response.data['error']
