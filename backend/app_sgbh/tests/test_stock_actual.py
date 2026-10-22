from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.serializers import StockActualSerializer
from app_sgbh.services.stock_actual import StockActualService
from app_sgbh.views.stock_actual_view import StockActualListView


def _stock_row():
    return SimpleNamespace(
        bien_id=4,
        stock_actual=Decimal('12.500000'),
        bien=SimpleNamespace(
            categoria_bien_id=2,
            unidad_medida_id=3,
            codigo='CLAV-01',
            nombre='Clavos de madera',
            descripcion='Clavos para madera',
            orden_impresion=1,
            esta_activo=True,
            visible_planilla=True,
            categoria_bien=SimpleNamespace(nombre='Herramientas'),
            unidad_medida=SimpleNamespace(nombre='Kilogramo'),
        ),
    )


def test_list_returns_every_row_when_no_filter_is_sent():
    with patch('app_sgbh.services.stock_actual.StockActual') as model:
        queryset = model.objects.select_related.return_value
        queryset.order_by.return_value = 'rows'

        result = StockActualService.list()

    assert result == 'rows'
    model.objects.select_related.assert_called_once_with(
        'bien',
        'bien__categoria_bien',
        'bien__unidad_medida',
    )
    queryset.filter.assert_not_called()
    queryset.order_by.assert_called_once_with('bien_id')


def test_list_filters_by_bien_id():
    with patch('app_sgbh.services.stock_actual.StockActual') as model:
        queryset = model.objects.select_related.return_value
        queryset.filter.return_value = queryset
        queryset.order_by.return_value = 'rows'

        result = StockActualService.list(bien_id=4)

    assert result == 'rows'
    queryset.filter.assert_called_once_with(bien_id=4)
    queryset.order_by.assert_called_once_with('bien_id')


def test_serializer_returns_good_category_and_unit_columns():
    data = StockActualSerializer(_stock_row()).data

    assert data == {
        'bien_id': 4,
        'categoria_bien_id': 2,
        'unidad_medida_id': 3,
        'codigo': 'CLAV-01',
        'nombre': 'Clavos de madera',
        'descripcion': 'Clavos para madera',
        'orden_impresion': 1,
        'esta_activo': True,
        'visible_planilla': True,
        'stock_actual': '12.500000',
        'categoria_bien_nombre': 'Herramientas',
        'unidad_medida_nombre': 'Kilogramo',
    }


def test_serializer_returns_null_optional_good_fields():
    row = _stock_row()
    row.bien.descripcion = None
    row.bien.orden_impresion = None

    data = StockActualSerializer(row).data

    assert data['descripcion'] is None
    assert data['orden_impresion'] is None


def test_get_returns_rows_when_bien_id_is_sent():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/stock-actual/', {'bien_id': '4'})
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'bien_id': 4, 'stock_actual': '12.500000'}]

    with (
        patch(
            'app_sgbh.views.stock_actual_view.StockActualService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.stock_actual_view.StockActualSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = StockActualListView.as_view()(request)

    assert response.status_code == 200
    assert response.data == rows
    list_rows.assert_called_once_with(bien_id=4)
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_returns_every_row_without_params():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/stock-actual/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with (
        patch(
            'app_sgbh.views.stock_actual_view.StockActualService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.stock_actual_view.StockActualSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = []
        response = StockActualListView.as_view()(request)

    assert response.status_code == 200
    assert response.data == []
    list_rows.assert_called_once_with(bien_id=None)


def test_get_rejects_invalid_filter():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/stock-actual/', {'bien_id': 'x'})
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = StockActualListView.as_view()(request)

    assert response.status_code == 400
    assert response.data['error'] == 'El filtro bien_id debe ser un número entero'


def test_get_returns_500_when_the_query_fails():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/stock-actual/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.stock_actual_view.StockActualService.list',
        side_effect=Exception('db'),
    ):
        response = StockActualListView.as_view()(request)

    assert response.status_code == 500
    assert response.data['error'] == 'No se pudo obtener el stock actual'
