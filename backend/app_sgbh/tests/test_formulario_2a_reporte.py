from datetime import date, time
from types import SimpleNamespace
from unittest.mock import patch

from rest_framework.test import APIRequestFactory, force_authenticate

from app_auth.authentication import ExternalUser
from app_sgbh.services.formulario_2a import Formulario2AServiceError
from app_sgbh.services.formulario_2a_reporte import (
    encabezado_reporte,
    filas_reporte,
)
from app_sgbh.views.formulario_2a_reporte_view import Formulario2AReporteView


def _catalogo(codigo):
    return SimpleNamespace(codigo=codigo)


def _material(codigo_formulario):
    if codigo_formulario is None:
        return None
    return SimpleNamespace(codigo_formulario=codigo_formulario)


def _persona(
    *,
    sexo='F',
    tipo_documento='DNI',
    numero_documento='44854559',
    apellido_paterno='JACINTO',
    apellido_materno='CHUNGA',
    nombres='CRUZ SIXTA',
):
    return SimpleNamespace(
        sexo=sexo,
        numero_documento=numero_documento,
        apellido_paterno=apellido_paterno,
        apellido_materno=apellido_materno,
        nombres=nombres,
        tipo_documento=None if tipo_documento is None else _catalogo(tipo_documento),
    )


def _integrante(
    *,
    edad,
    sexo='F',
    rol='J',
    condicion='AFECTADO',
    danio=None,
    gestante_semanas=None,
    discapacidad=None,
    enfermedad=None,
    tipo_documento='DNI',
    numero_documento='44854559',
    apellido_paterno='JACINTO',
    apellido_materno='CHUNGA',
    nombres='CRUZ SIXTA',
):
    return SimpleNamespace(
        edad=edad,
        gestante_semanas=gestante_semanas,
        persona=_persona(
            sexo=sexo,
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            nombres=nombres,
        ),
        rol_familiar=_catalogo(rol),
        condicion_persona=_catalogo(condicion),
        tipo_danio_personal=None if danio is None else _catalogo(danio),
        tipo_discapacidad=_material(discapacidad),
        enfermedad_cronica=_material(enfermedad),
    )


def _medio(categoria, codigo_formulario, cantidad):
    return SimpleNamespace(
        cantidad=cantidad,
        tipo_medio_vida=SimpleNamespace(
            codigo_formulario=codigo_formulario,
            categoria_medio_vida=_catalogo(categoria),
        ),
    )


def _familia(integrantes, medios=()):
    return SimpleNamespace(integrantes=list(integrantes), medios_vida=list(medios))


def _vivienda(
    *,
    numero_lote='30',
    tenencia_propia=True,
    uso='VIVIENDA',
    condicion='AFECTADA',
    techo=4,
    pared=6,
    piso=6,
    familias=(),
):
    return SimpleNamespace(
        numero_lote=numero_lote,
        tenencia_propia=tenencia_propia,
        tipo_uso_instalacion=_catalogo(uso),
        condicion_vivienda=None if condicion is None else _catalogo(condicion),
        material_techo=_material(techo),
        material_pared=_material(pared),
        material_piso=_material(piso),
        familias=list(familias),
    )


def _formulario():
    return SimpleNamespace(
        emergencia=SimpleNamespace(
            numero_evaluacion='E-1',
            codigo_sinpad='261404',
            fecha_emergencia=date(2026, 3, 30),
            hora_ocurrencia_estimada=time(12, 0),
            tipo_peligro=SimpleNamespace(nombre='INCENDIO URBANO'),
        ),
        fecha_empadronamiento=date(2026, 3, 31),
        hora_empadronamiento=time(8, 45),
        distrito_nombre=' PIURA ',
        localidad=None,
        barrio_sector_urbanizacion='A.H 01 DE AGOSTO',
        calle_manzana='A',
        edificio_piso_dpto=None,
        numero_hoja=1,
        centro_poblado=None,
        caserio=None,
        anexo=None,
        otros_ubicacion=None,
        institucion='MUNICIPALIDAD PROVINCIAL DE PIURA',
        evaluador=SimpleNamespace(
            apellido_paterno='YDROGO',
            apellido_materno='GARCIA',
            nombres='JESUS',
        ),
        departamento_id='01',
        provincia_id='02',
    )


def test_encabezado_imprime_departamento_y_provincia_piura():
    data = encabezado_reporte(_formulario())

    assert data['departamento'] == 'PIURA'
    assert data['provincia'] == 'PIURA'
    assert data['distrito'] == 'PIURA'
    assert data['tipo_peligro'] == 'INCENDIO URBANO'
    assert data['codigo_sinpad'] == '261404'
    assert data['numero_hoja'] == 1
    assert data['evaluador_nombre'] == 'YDROGO GARCIA JESUS'
    assert data['institucion'] == 'MUNICIPALIDAD PROVINCIAL DE PIURA'


def test_filas_marcan_la_vivienda_solo_en_la_primera_persona():
    vivienda = _vivienda(
        familias=[
            _familia(
                [
                    _integrante(edad=56, rol='J', sexo='F'),
                    _integrante(
                        edad=13,
                        rol='D',
                        sexo='M',
                        apellido_paterno='LEON',
                        apellido_materno='BECERRA',
                        nombres='ADRIAN',
                        numero_documento='77789822',
                    ),
                ]
            )
        ]
    )

    filas = filas_reporte([vivienda])

    assert filas[0]['numero_lote'] == '30'
    assert filas[0]['tenencia_si'] is True
    assert filas[0]['tenencia_no'] is False
    assert filas[0]['uso_vivienda'] is True
    assert filas[0]['condicion_afectada'] is True
    assert filas[0]['material_techo'] == 4
    assert filas[0]['material_pared'] == 6
    assert filas[0]['material_piso'] == 6
    assert filas[0]['apellidos_nombres'] == 'JACINTO CHUNGA CRUZ SIXTA (J)'
    assert filas[1]['numero_lote'] is None
    assert filas[1]['tenencia_si'] is False
    assert filas[1]['uso_vivienda'] is False
    assert filas[1]['material_techo'] is None
    assert filas[1]['apellidos_nombres'] == 'LEON BECERRA ADRIAN (D)'


def test_filas_tenencia_no_y_medio_de_vida_e_inhabitable():
    vivienda = _vivienda(
        tenencia_propia=False,
        uso='MEDIO_VIDA',
        condicion='INHABITABLE',
        familias=[_familia([_integrante(edad=40, sexo='M')])],
    )

    fila = filas_reporte([vivienda])[0]

    assert fila['tenencia_si'] is False
    assert fila['tenencia_no'] is True
    assert fila['uso_vivienda'] is False
    assert fila['uso_medio_vida'] is True
    assert fila['condicion_inhabitable'] is True
    assert fila['condicion_afectada'] is False


def test_filas_no_marcan_tenencia_cuando_es_nula_ni_codigos_desconocidos():
    vivienda = _vivienda(
        tenencia_propia=None,
        uso='OTRO_USO',
        condicion='OTRA',
        familias=[_familia([_integrante(edad=20, sexo='X', danio='OTRO', condicion='OTRA')])],
    )

    fila = filas_reporte([vivienda])[0]

    assert fila['tenencia_si'] is False
    assert fila['tenencia_no'] is False
    assert fila['uso_vivienda'] is False
    assert fila['uso_medio_vida'] is False
    assert fila['condicion_afectada'] is False
    assert fila['condicion_destruida'] is False
    assert fila['sexo'] is None
    assert fila['condicion_damnificado'] is None
    assert fila['condicion_afectado'] is None
    assert fila['danio_fallecido'] is None
    assert fila['danio_lesionado'] is None
    assert fila['danio_desaparecido'] is None


def test_filas_ubican_edad_sexo_y_danos():
    filas = filas_reporte(
        [
            _vivienda(
                familias=[
                    _familia(
                        [
                            _integrante(edad=0, sexo='M', danio='FALLECIDO'),
                            _integrante(edad=4, sexo='F', danio='LESIONADO'),
                            _integrante(edad=17, sexo='M', danio='DESAPARECIDO'),
                            _integrante(
                                edad=60,
                                sexo='F',
                                gestante_semanas=12,
                                condicion='DAMNIFICADO',
                            ),
                        ]
                    )
                ]
            )
        ]
    )

    assert filas[0]['grupo_etario'] == 'menor_1'
    assert filas[0]['sexo'] == 'M'
    assert filas[0]['condicion_afectado'] == 1
    assert filas[0]['condicion_damnificado'] is None
    assert filas[0]['danio_fallecido'] == 1
    assert filas[1]['grupo_etario'] == '01_04'
    assert filas[1]['condicion_afectado'] == 1
    assert filas[1]['danio_lesionado'] == 1
    assert filas[2]['grupo_etario'] == '15_17'
    assert filas[2]['danio_desaparecido'] == 1
    assert filas[3]['grupo_etario'] == '60_mas'
    assert filas[3]['gestante_semanas'] == 12
    assert filas[3]['condicion_damnificado'] == 1
    assert filas[3]['condicion_afectado'] is None


def test_filas_ponen_medios_de_vida_en_el_primer_integrante():
    vivienda = _vivienda(
        familias=[
            _familia(
                [
                    _integrante(edad=30, rol='J'),
                    _integrante(edad=8, rol='D', sexo='M'),
                ],
                medios=[
                    _medio('COMERCIO', 1, 2),
                    _medio('COMERCIO', 4, 1),
                    _medio('TURISMO', 2, 3),
                    _medio('OTROS', 9, 1),
                    _medio('AGRICULTURA', 1, 5),
                ],
            )
        ]
    )

    filas = filas_reporte([vivienda])

    assert filas[0]['comercio_tipo'] == '1, 4'
    assert filas[0]['comercio_cantidad'] == '2, 1'
    assert filas[0]['turismo_tipo'] == '2'
    assert filas[0]['turismo_cantidad'] == '3'
    assert filas[0]['otros'] == '9'
    assert filas[0]['otros_cantidad'] == '1'
    assert filas[1]['comercio_tipo'] is None
    assert filas[1]['turismo_cantidad'] is None
    assert filas[1]['otros'] is None
    assert filas[1]['otros_cantidad'] is None


def test_filas_conservan_vivienda_sin_integrantes_y_sus_medios():
    vivienda = _vivienda(
        familias=[
            _familia([], medios=[_medio('COMERCIO', 3, 1)]),
        ]
    )

    filas = filas_reporte([vivienda])

    assert len(filas) == 1
    assert filas[0]['numero_lote'] == '30'
    assert filas[0]['apellidos_nombres'] is None
    assert filas[0]['comercio_tipo'] == '3'
    assert filas[0]['comercio_cantidad'] == '1'


def test_get_reporte_devuelve_el_formulario():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/5/reporte/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))
    payload = encabezado_reporte(_formulario())
    payload['filas'] = []

    with patch(
        'app_sgbh.views.formulario_2a_reporte_view.Formulario2AReporteService.get',
        return_value=payload,
    ):
        response = Formulario2AReporteView.as_view()(request, formulario_2a_id=5)

    assert response.status_code == 200
    assert response.data['departamento'] == 'PIURA'
    assert response.data['provincia'] == 'PIURA'
    assert response.data['fecha_emergencia'] == '2026-03-30'
    assert response.data['hora_ocurrencia_estimada'] == '12:00:00'
    assert response.data['filas'] == []


def test_get_reporte_responde_404_cuando_no_existe():
    factory = APIRequestFactory()
    request = factory.get('/api/sgbh/formularios-2a/9/reporte/')
    force_authenticate(request, user=ExternalUser(login='mmedina', nombre='Mario'))

    with patch(
        'app_sgbh.views.formulario_2a_reporte_view.Formulario2AReporteService.get',
        side_effect=Formulario2AServiceError(
            'El formulario EDAN 2A indicado no existe',
            not_found=True,
        ),
    ):
        response = Formulario2AReporteView.as_view()(request, formulario_2a_id=9)

    assert response.status_code == 404
    assert response.data['error'] == 'El formulario EDAN 2A indicado no existe'
