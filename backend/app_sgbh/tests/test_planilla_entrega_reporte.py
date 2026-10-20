from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.db.models import Count
from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.formulario_2a_integrante import contar_integrantes_familia
from app_sgbh.services.planilla_entrega import PlanillaEntregaServiceError
from app_sgbh.services.planilla_entrega_reporte import (
    PlanillaEntregaReporteService,
    _detalles_reporte,
    armar_reporte,
    bienes_reporte,
    bien_nombre_reporte,
    direccion_reporte,
    encabezado_reporte,
    nombre_completo,
)
from app_sgbh.views.planilla_entrega_reporte_view import PlanillaEntregaReporteView


def _detalle(
    *,
    nombre='AGUA',
    abreviatura='UND',
    categoria='ALIMENTOS',
    cantidad='2.000000',
    cantidad_texto='2',
):
    return SimpleNamespace(
        cantidad=Decimal(cantidad),
        cantidad_texto=cantidad_texto,
        bien=SimpleNamespace(
            nombre=nombre,
            unidad_medida=SimpleNamespace(abreviatura=abreviatura),
            categoria_bien=SimpleNamespace(nombre=categoria, orden=1),
        ),
    )


def _planilla(
    *,
    localidad='LA UNION',
    barrio='SANTA ROSA',
    calle='A-1',
    numero_lote='12',
    codigo_sinpad='SIN-1',
    tipo_peligro='INUNDACION',
    distrito_nombre='PIURA',
    numero_documento='12345678',
    apellido_paterno='PEREZ',
    apellido_materno='LOPEZ',
    nombres='ANA',
    movimiento=None,
    detalles=None,
    receptor=True,
):
    if detalles is None:
        detalles = [_detalle()]
    if movimiento is None and receptor:
        movimiento = SimpleNamespace(
            movimiento_id=15,
            encargado_almacen=SimpleNamespace(
                apellido_paterno='GARCIA',
                apellido_materno='RUIZ',
                nombres='LUIS',
            ),
            detalles=detalles,
        )
    formulario = SimpleNamespace(
        localidad=localidad,
        barrio_sector_urbanizacion=barrio,
        calle_manzana=calle,
        emergencia=SimpleNamespace(
            codigo_sinpad=codigo_sinpad,
            tipo_peligro=None
            if tipo_peligro is None
            else SimpleNamespace(nombre=tipo_peligro),
        ),
    )
    vivienda = SimpleNamespace(numero_lote=numero_lote, formulario_2a=formulario)
    familia = SimpleNamespace(familia_id=7, vivienda=vivienda)
    integrante = None
    if receptor:
        integrante = SimpleNamespace(
            familia_id=7,
            familia=familia,
            persona=SimpleNamespace(
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                nombres=nombres,
                numero_documento=numero_documento,
            ),
        )
    return SimpleNamespace(
        planilla_entrega_id=3,
        numero_planilla=10,
        anio_planilla=2026,
        fecha_entrega=date(2026, 4, 2),
        distrito_nombre=distrito_nombre,
        integrante_receptor=integrante,
        movimiento_almacen=movimiento,
    )


def test_direccion_une_localidad_barrio_calle_y_lote():
    assert (
        direccion_reporte('LA UNION', 'SANTA ROSA', 'A-1', '12')
        == 'LA UNION SANTA ROSA CALLE/MZNA A-1 LOTE 12'
    )


def test_direccion_deja_vacios_los_nulos_excepto_el_lote():
    assert direccion_reporte(None, 'SANTA ROSA', None, '12') == ' SANTA ROSA  LOTE 12'


def test_direccion_es_nula_cuando_el_lote_es_nulo():
    assert direccion_reporte('LA UNION', 'SANTA ROSA', 'A-1', None) is None


def test_nombre_completo_separa_con_espacios():
    assert nombre_completo('PEREZ', 'LOPEZ', 'ANA') == 'PEREZ LOPEZ ANA'


def test_nombre_completo_es_nulo_si_falta_una_parte():
    assert nombre_completo('PEREZ', None, 'ANA') is None


def test_bien_nombre_incluye_la_abreviatura():
    assert bien_nombre_reporte('AGUA', 'UND') == 'AGUA (UND)'


def test_bien_nombre_es_nulo_si_falta_la_abreviatura():
    assert bien_nombre_reporte('AGUA', None) is None


def test_encabezado_reporte_arma_la_planilla():
    data = encabezado_reporte(_planilla(), 4)

    assert data['movimiento_id'] == 15
    assert data['planilla_entrega_id'] == 3
    assert data['numero_planilla'] == 10
    assert data['anio_planilla'] == 2026
    assert data['region_nombre'] == 'PIURA'
    assert data['provincia_nombre'] == 'PIURA'
    assert data['distrito_nombre'] == 'PIURA'
    assert data['localidad'] == 'LA UNION'
    assert data['barrio_sector_urbanizacion'] == 'SANTA ROSA'
    assert data['codigo_sinpad'] == 'SIN-1'
    assert data['entregado_por_gore'] == ''
    assert data['municip_prov'] == 'PIURA'
    assert data['municip_dist'] == ''
    assert data['tipo_peligro_nombre'] == 'INUNDACION'
    assert data['planilla_fecha_entrega'] == date(2026, 4, 2)
    assert data['direccion'] == 'LA UNION SANTA ROSA CALLE/MZNA A-1 LOTE 12'
    assert data['integrante_receptor_nombre'] == 'PEREZ LOPEZ ANA'
    assert data['integrante_receptor_doc_ident'] == '12345678'
    assert data['nro_integrantes_familia'] == 4
    assert data['encargado_almacen_nombre'] == 'GARCIA RUIZ LUIS'


def test_encabezado_sin_movimiento_deja_nulos_el_movimiento_y_el_encargado():
    planilla = _planilla()
    planilla.movimiento_almacen = None

    data = encabezado_reporte(planilla, 0)

    assert data['movimiento_id'] is None
    assert data['encargado_almacen_nombre'] is None
    assert data['region_nombre'] == 'PIURA'


def test_bienes_reporte_conserva_el_orden_y_la_cantidad():
    lineas = bienes_reporte(
        [
            _detalle(nombre='AGUA', categoria='ALIMENTOS', cantidad='2.000000'),
            _detalle(nombre='FRAZADA', categoria='ABRIGO', cantidad='-1.500000'),
        ]
    )

    assert [linea['categoria_bien_nombre'] for linea in lineas] == [
        'ALIMENTOS',
        'ABRIGO',
    ]
    assert lineas[0]['bien_nombre'] == 'AGUA (UND)'
    assert lineas[0]['cantidad'] == Decimal('2.000000')
    assert lineas[0]['cantidad_texto'] == '2'
    assert lineas[1]['bien_nombre'] == 'FRAZADA (UND)'
    assert lineas[1]['cantidad_texto'] == '2'


def test_armar_reporte_lista_los_bienes_del_movimiento():
    data = armar_reporte(_planilla(), 4)

    assert data['nro_integrantes_familia'] == 4
    assert len(data['bienes']) == 1
    assert data['bienes'][0]['bien_nombre'] == 'AGUA (UND)'


def test_armar_reporte_sin_movimiento_no_agrega_lineas():
    planilla = _planilla()
    planilla.movimiento_almacen = None

    data = armar_reporte(planilla, 2)

    assert data['bienes'] == []
    assert data['nro_integrantes_familia'] == 2


def test_detalles_reporte_ordenan_por_la_categoria():
    assert _detalles_reporte().query.order_by == ('bien__categoria_bien__orden',)


def test_get_cuenta_los_integrantes_de_la_familia_del_receptor():
    planilla = _planilla()

    with (
        patch(
            'app_sgbh.services.planilla_entrega_reporte._planilla_reporte',
            return_value=planilla,
        ),
        patch(
            'app_sgbh.services.planilla_entrega_reporte.contar_integrantes_familia',
            return_value=6,
        ) as contar,
    ):
        data = PlanillaEntregaReporteService.get(3)

    contar.assert_called_once_with(7)
    assert data['nro_integrantes_familia'] == 6
    assert data['planilla_entrega_id'] == 3


def test_get_responde_no_existe_cuando_no_hay_planilla():
    with patch(
        'app_sgbh.services.planilla_entrega_reporte._planilla_reporte',
        return_value=None,
    ):
        with pytest.raises(PlanillaEntregaServiceError) as exc:
            PlanillaEntregaReporteService.get(9)

    assert exc.value.not_found is True
    assert exc.value.message == 'La planilla BAH indicada no existe'


def test_contar_integrantes_familia_cuenta_por_familia():
    with patch(
        'app_sgbh.services.formulario_2a_integrante.Formulario2AIntegrante.objects.filter'
    ) as filtrar:
        filtrar.return_value.aggregate.return_value = {'total': 5}
        total = contar_integrantes_familia(8)

    assert total == 5
    filtrar.assert_called_once_with(familia_id=8)
    assert filtrar.return_value.aggregate.call_args.kwargs['total'] == Count('*')


def test_contar_integrantes_familia_sin_familia_es_cero():
    assert contar_integrantes_familia(None) == 0


def test_get_reporte_devuelve_la_planilla():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/planillas-bah/3/reporte/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    payload = encabezado_reporte(_planilla(), 4)
    payload['bienes'] = bienes_reporte([_detalle()])

    with patch(
        'app_sgbh.views.planilla_entrega_reporte_view.PlanillaEntregaReporteService.get',
        return_value=payload,
    ):
        response = PlanillaEntregaReporteView.as_view()(request, planilla_entrega_id=3)

    assert response.status_code == 200
    assert response.data['region_nombre'] == 'PIURA'
    assert response.data['provincia_nombre'] == 'PIURA'
    assert response.data['entregado_por_gore'] == ''
    assert response.data['municip_dist'] == ''
    assert response.data['nro_integrantes_familia'] == 4
    assert response.data['planilla_fecha_entrega'] == '2026-04-02'
    assert response.data['direccion'] == 'LA UNION SANTA ROSA CALLE/MZNA A-1 LOTE 12'
    assert response.data['bienes'] == [
        {
            'categoria_bien_nombre': 'ALIMENTOS',
            'bien_nombre': 'AGUA (UND)',
            'cantidad': '2.000000',
            'cantidad_texto': '2',
        }
    ]


def test_get_reporte_responde_404_cuando_no_existe():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/planillas-bah/9/reporte/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.planilla_entrega_reporte_view.PlanillaEntregaReporteService.get',
        side_effect=PlanillaEntregaServiceError(
            'La planilla BAH indicada no existe',
            not_found=True,
        ),
    ):
        response = PlanillaEntregaReporteView.as_view()(request, planilla_entrega_id=9)

    assert response.status_code == 404
    assert response.data['error'] == 'La planilla BAH indicada no existe'


def test_get_reporte_rechaza_un_id_fuera_de_rango():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/planillas-bah/0/reporte/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    response = PlanillaEntregaReporteView.as_view()(request, planilla_entrega_id=0)

    assert response.status_code == 400
    assert response.data['error'] == (
        'El campo planilla_entrega_id debe ser un número entero'
    )
