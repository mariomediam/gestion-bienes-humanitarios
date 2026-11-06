from decimal import Decimal
from unittest.mock import patch

from django.db.models import Sum, Value
from django.db.models.functions import Abs, Coalesce
from django.urls import resolve
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.models import MovimientoDetalle
from app_sgbh.serializers.movimiento_cantidades_salida import (
    MovimientoCantidadesSalidaSerializer,
)
from app_sgbh.services.movimiento_cantidades_salida import (
    MovimientoCantidadesSalidaService,
)
from app_sgbh.views.movimiento_cantidades_salida_view import (
    MovimientoCantidadesPorDevolverView,
)


def _lookup_pairs(node):
    pairs = []
    for child in getattr(node, 'children', ()):
        if hasattr(child, 'lhs') and hasattr(child, 'rhs'):
            pairs.append((child.lhs.target.column, child.rhs))
        else:
            pairs.extend(_lookup_pairs(child))
    return pairs


def test_list_keeps_each_salida_line_and_sums_entradas_by_bien():
    queryset = MovimientoCantidadesSalidaService.list(159)
    query = queryset.query

    assert ('movimiento_id', 159) in _lookup_pairs(query.where)
    assert ('naturaleza', 'S') in _lookup_pairs(query.where)
    assert isinstance(query.annotations['cantidad_origen'], Abs)
    assert (
        query.annotations['cantidad_origen'].source_expressions[0].target.column
        == 'cantidad'
    )

    entrada = query.annotations['cantidad_entrada']
    assert isinstance(entrada, Coalesce)
    inner, cero = entrada.get_source_expressions()
    assert isinstance(cero, Value)
    assert cero.value == Decimal('0')
    assert isinstance(inner.annotations['total'], Sum)
    assert isinstance(inner.annotations['total'].source_expressions[0], Abs)
    inner_filters = _lookup_pairs(inner.where)
    assert ('movimiento_origen_id', 159) in inner_filters
    assert ('naturaleza', 'E') in inner_filters
    bien_refs = [rhs for column, rhs in inner_filters if column == 'bien_id']
    assert len(bien_refs) == 1
    assert bien_refs[0].alias == MovimientoDetalle._meta.db_table
    assert queryset._fields == (
        'bien_id',
        'bien_nombre',
        'abreviatura_nombre',
        'cantidad_origen',
        'cantidad_entrada',
    )


def test_serializer_returns_salida_and_entrada_columns():
    data = MovimientoCantidadesSalidaSerializer(
        {
            'bien_id': 7,
            'bien_nombre': 'Motobomba',
            'abreviatura_nombre': 'UND',
            'cantidad_origen': Decimal('2.000000'),
            'cantidad_entrada': Decimal('1.000000'),
        }
    ).data

    assert data == {
        'bien_id': 7,
        'bien_nombre': 'Motobomba',
        'abreviatura_nombre': 'UND',
        'cantidad_origen': '2.000000',
        'cantidad_entrada': '1.000000',
    }


def test_serializer_returns_null_abreviatura_and_zero_entrada():
    data = MovimientoCantidadesSalidaSerializer(
        {
            'bien_id': 7,
            'bien_nombre': 'Motobomba',
            'abreviatura_nombre': None,
            'cantidad_origen': Decimal('2.000000'),
            'cantidad_entrada': Decimal('0'),
        }
    ).data

    assert data['abreviatura_nombre'] is None
    assert data['cantidad_entrada'] == '0.000000'


def test_url_resolves_cantidades_salida():
    match = resolve('/api/sgbh/movimientos/159/cantidades-salida/')

    assert match.func.view_class is MovimientoCantidadesPorDevolverView
    assert match.kwargs == {'movimiento_id': 159}


def test_get_returns_rows():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/movimientos/159/cantidades-salida/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    rows = [{'bien_id': 7}]

    with (
        patch(
            'app_sgbh.views.movimiento_cantidades_salida_view.MovimientoCantidadesSalidaService.list',
            return_value='queryset',
        ) as list_rows,
        patch(
            'app_sgbh.views.movimiento_cantidades_salida_view.MovimientoCantidadesSalidaSerializer'
        ) as serializer_cls,
    ):
        serializer_cls.return_value.data = rows
        response = MovimientoCantidadesPorDevolverView.as_view()(request, movimiento_id=159)

    assert response.status_code == 200
    assert response.data == rows
    list_rows.assert_called_once_with(159)
    serializer_cls.assert_called_once_with('queryset', many=True)


def test_get_rejects_movimiento_id_out_of_range():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/movimientos/0/cantidades-salida/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = MovimientoCantidadesPorDevolverView.as_view()(request, movimiento_id=0)

    assert response.status_code == 400
    assert response.data['error'] == 'El campo movimiento_id debe ser un número entero'


def test_get_returns_500_when_the_query_fails():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/movimientos/159/cantidades-salida/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.movimiento_cantidades_salida_view.MovimientoCantidadesSalidaService.list',
        side_effect=Exception('db'),
    ):
        response = MovimientoCantidadesPorDevolverView.as_view()(request, movimiento_id=159)

    assert response.status_code == 500
    assert (
        response.data['error']
        == 'No se pudieron obtener las cantidades de salida del movimiento'
    )
