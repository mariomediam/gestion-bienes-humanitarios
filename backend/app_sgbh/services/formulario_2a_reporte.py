from django.db.models import Prefetch

from ..models import (
    Formulario2AFamilia,
    Formulario2AIntegrante,
    Formulario2AMedioVida,
    Formulario2AVivienda,
)
from .formulario_2a import Formulario2AService

# The printed form always shows these names. The stored ubigeo codes stay
# on the formulario and are not repeated as text on the sheet.
DEPARTAMENTO_REPORTE = 'PIURA'
PROVINCIA_REPORTE = 'PIURA'

_USO_VIVIENDA = 'VIVIENDA'
_USO_MEDIO_VIDA = 'MEDIO_VIDA'
_CONDICION_AFECTADA = 'AFECTADA'
_CONDICION_INHABITABLE = 'INHABITABLE'
_CONDICION_DESTRUIDA = 'DESTRUIDA'
_DANIO_FALLECIDO = 'FALLECIDO'
_DANIO_LESIONADO = 'LESIONADO'
_DANIO_DESAPARECIDO = 'DESAPARECIDO'
_CATEGORIA_COMERCIO = 'COMERCIO'
_CATEGORIA_TURISMO = 'TURISMO'
_CATEGORIA_OTROS = 'OTROS'
_SEXO_MASCULINO = 'M'
_SEXO_FEMENINO = 'F'
_MARCA_NUMERO = 1

# Age bands printed on the official form, in years.
_GRUPOS_ETARIOS = (
    ('menor_1', 0, 0),
    ('01_04', 1, 4),
    ('05_09', 5, 9),
    ('10_14', 10, 14),
    ('15_17', 15, 17),
    ('18_49', 18, 49),
    ('50_59', 50, 59),
    ('60_mas', 60, 130),
)


def encabezado_reporte(formulario):
    """Header fields of one Formulario 2A sheet.

    Departamento and provincia are always PIURA. Distrito comes from the
    DISTRITO view already annotated on the formulario.
    """
    emergencia = formulario.emergencia
    return {
        'numero_evaluacion': _texto(emergencia.numero_evaluacion),
        'codigo_sinpad': _texto(emergencia.codigo_sinpad),
        'tipo_peligro': _texto(emergencia.tipo_peligro.nombre),
        'fecha_emergencia': emergencia.fecha_emergencia,
        'hora_ocurrencia_estimada': emergencia.hora_ocurrencia_estimada,
        'fecha_empadronamiento': formulario.fecha_empadronamiento,
        'hora_empadronamiento': formulario.hora_empadronamiento,
        'departamento': DEPARTAMENTO_REPORTE,
        'provincia': PROVINCIA_REPORTE,
        'distrito': _texto(formulario.distrito_nombre),
        'localidad': _texto(formulario.localidad),
        'barrio_sector_urbanizacion': _texto(formulario.barrio_sector_urbanizacion),
        'calle_manzana': _texto(formulario.calle_manzana),
        'edificio_piso_dpto': _texto(formulario.edificio_piso_dpto),
        'numero_hoja': formulario.numero_hoja,
        'centro_poblado': _texto(formulario.centro_poblado),
        'caserio': _texto(formulario.caserio),
        'anexo': _texto(formulario.anexo),
        'otros_ubicacion': _texto(formulario.otros_ubicacion),
        'institucion': _texto(formulario.institucion),
        'evaluador_nombre': _nombre_partes(
            formulario.evaluador.apellido_paterno,
            formulario.evaluador.apellido_materno,
            formulario.evaluador.nombres,
        ),
    }


def filas_reporte(viviendas):
    """One printed row per integrante, in vivienda, familia and integrante order.

    Housing marks are printed only on the first row of each vivienda, as on
    the filled field sheets. Medios de vida are printed on the first
    integrante of each familia.
    """
    filas = []
    for vivienda in viviendas:
        familias = _secuencia(vivienda.familias)
        if not familias:
            filas.append(_fila(**_vivienda_campos(vivienda)))
            continue
        primera_de_vivienda = True
        for familia in familias:
            integrantes = _secuencia(familia.integrantes)
            medios = _medios_campos(_secuencia(familia.medios_vida))
            if not integrantes:
                vivienda_campos = _vivienda_campos(vivienda) if primera_de_vivienda else {}
                filas.append(_fila(**vivienda_campos, **medios))
                primera_de_vivienda = False
                continue
            for indice, integrante in enumerate(integrantes):
                vivienda_campos = _vivienda_campos(vivienda) if primera_de_vivienda else {}
                medios_campos = medios if indice == 0 else {}
                filas.append(
                    _fila(
                        **vivienda_campos,
                        **_persona_campos(integrante),
                        **medios_campos,
                    )
                )
                primera_de_vivienda = False
    return filas


def armar_reporte(formulario, viviendas):
    """Header plus rows for the printable Formulario 2A."""
    reporte = encabezado_reporte(formulario)
    reporte['filas'] = filas_reporte(viviendas)
    return reporte


class Formulario2AReporteService:
    @staticmethod
    def get(formulario_2a_id):
        """Return the printable payload of one Formulario 2A.

        Raises Formulario2AServiceError when the formulario does not exist.
        """
        formulario = Formulario2AService.get(formulario_2a_id)
        viviendas = _viviendas_reporte(formulario_2a_id)
        return armar_reporte(formulario, viviendas)


def _viviendas_reporte(formulario_2a_id):
    integrantes = Formulario2AIntegrante.objects.select_related(
        'persona',
        'persona__tipo_documento',
        'rol_familiar',
        'condicion_persona',
        'tipo_danio_personal',
        'tipo_discapacidad',
        'enfermedad_cronica',
    ).order_by('numero_orden', 'integrante_id')
    medios = Formulario2AMedioVida.objects.select_related(
        'tipo_medio_vida',
        'tipo_medio_vida__categoria_medio_vida',
    ).order_by('medio_vida_id')
    familias = Formulario2AFamilia.objects.order_by(
        'numero_orden',
        'familia_id',
    ).prefetch_related(
        Prefetch('integrantes', queryset=integrantes),
        Prefetch('medios_vida', queryset=medios),
    )
    return (
        Formulario2AVivienda.objects.filter(formulario_2a_id=formulario_2a_id)
        .select_related(
            'tipo_uso_instalacion',
            'condicion_vivienda',
            'material_techo',
            'material_pared',
            'material_piso',
        )
        .prefetch_related(Prefetch('familias', queryset=familias))
        .order_by('numero_orden', 'vivienda_id')
    )


def _fila(
    *,
    numero_lote=None,
    tenencia_si=False,
    tenencia_no=False,
    uso_vivienda=False,
    uso_medio_vida=False,
    condicion_afectada=False,
    condicion_inhabitable=False,
    condicion_destruida=False,
    material_techo=None,
    material_pared=None,
    material_piso=None,
    apellidos_nombres=None,
    edad=None,
    tipo_documento=None,
    numero_documento=None,
    condicion_persona=None,
    danio_fallecido=None,
    danio_lesionado=None,
    danio_desaparecido=None,
    grupo_etario=None,
    sexo=None,
    gestante_semanas=None,
    discapacidad=None,
    enfermedad_cronica=None,
    comercio_tipo=None,
    comercio_cantidad=None,
    turismo_tipo=None,
    turismo_cantidad=None,
    otros=None,
):
    return {
        'numero_lote': numero_lote,
        'tenencia_si': tenencia_si,
        'tenencia_no': tenencia_no,
        'uso_vivienda': uso_vivienda,
        'uso_medio_vida': uso_medio_vida,
        'condicion_afectada': condicion_afectada,
        'condicion_inhabitable': condicion_inhabitable,
        'condicion_destruida': condicion_destruida,
        'material_techo': material_techo,
        'material_pared': material_pared,
        'material_piso': material_piso,
        'apellidos_nombres': apellidos_nombres,
        'edad': edad,
        'tipo_documento': tipo_documento,
        'numero_documento': numero_documento,
        'condicion_persona': condicion_persona,
        'danio_fallecido': danio_fallecido,
        'danio_lesionado': danio_lesionado,
        'danio_desaparecido': danio_desaparecido,
        'grupo_etario': grupo_etario,
        'sexo': sexo,
        'gestante_semanas': gestante_semanas,
        'discapacidad': discapacidad,
        'enfermedad_cronica': enfermedad_cronica,
        'comercio_tipo': comercio_tipo,
        'comercio_cantidad': comercio_cantidad,
        'turismo_tipo': turismo_tipo,
        'turismo_cantidad': turismo_cantidad,
        'otros': otros,
    }


def _vivienda_campos(vivienda):
    tenencia = vivienda.tenencia_propia
    uso = _codigo(vivienda.tipo_uso_instalacion)
    condicion = _codigo(vivienda.condicion_vivienda)
    return {
        'numero_lote': _texto(vivienda.numero_lote),
        'tenencia_si': tenencia is True,
        'tenencia_no': tenencia is False,
        'uso_vivienda': uso == _USO_VIVIENDA,
        'uso_medio_vida': uso == _USO_MEDIO_VIDA,
        'condicion_afectada': condicion == _CONDICION_AFECTADA,
        'condicion_inhabitable': condicion == _CONDICION_INHABITABLE,
        'condicion_destruida': condicion == _CONDICION_DESTRUIDA,
        'material_techo': _codigo_formulario(vivienda.material_techo),
        'material_pared': _codigo_formulario(vivienda.material_pared),
        'material_piso': _codigo_formulario(vivienda.material_piso),
    }


def _persona_campos(integrante):
    persona = integrante.persona
    sexo = _texto(persona.sexo)
    if sexo not in (_SEXO_MASCULINO, _SEXO_FEMENINO):
        sexo = None
    danios = {
        'danio_fallecido': None,
        'danio_lesionado': None,
        'danio_desaparecido': None,
    }
    campo_danio = {
        _DANIO_FALLECIDO: 'danio_fallecido',
        _DANIO_LESIONADO: 'danio_lesionado',
        _DANIO_DESAPARECIDO: 'danio_desaparecido',
    }.get(_codigo(integrante.tipo_danio_personal))
    if campo_danio:
        danios[campo_danio] = _MARCA_NUMERO
    return {
        'apellidos_nombres': _nombre_partes(
            persona.apellido_paterno,
            persona.apellido_materno,
            persona.nombres,
            _codigo(integrante.rol_familiar),
        ),
        'edad': integrante.edad,
        'tipo_documento': _codigo(persona.tipo_documento),
        'numero_documento': _texto(persona.numero_documento),
        'condicion_persona': _codigo(integrante.condicion_persona),
        'grupo_etario': _grupo_etario(integrante.edad),
        'sexo': sexo,
        'gestante_semanas': integrante.gestante_semanas,
        'discapacidad': _codigo_formulario(integrante.tipo_discapacidad),
        'enfermedad_cronica': _codigo_formulario(integrante.enfermedad_cronica),
        **danios,
    }


def _medios_campos(medios):
    grupos = {
        _CATEGORIA_COMERCIO: [],
        _CATEGORIA_TURISMO: [],
        _CATEGORIA_OTROS: [],
    }
    for medio in medios:
        categoria = _codigo(medio.tipo_medio_vida.categoria_medio_vida)
        if categoria in grupos:
            grupos[categoria].append(medio)
    return {
        'comercio_tipo': _unir_codigos(grupos[_CATEGORIA_COMERCIO]),
        'comercio_cantidad': _unir_cantidades(grupos[_CATEGORIA_COMERCIO]),
        'turismo_tipo': _unir_codigos(grupos[_CATEGORIA_TURISMO]),
        'turismo_cantidad': _unir_cantidades(grupos[_CATEGORIA_TURISMO]),
        'otros': _unir_codigos(grupos[_CATEGORIA_OTROS]),
    }


def _unir_codigos(medios):
    if not medios:
        return None
    return ', '.join(str(medio.tipo_medio_vida.codigo_formulario) for medio in medios)


def _unir_cantidades(medios):
    if not medios:
        return None
    return ', '.join(str(medio.cantidad) for medio in medios)


def _grupo_etario(edad):
    for clave, minimo, maximo in _GRUPOS_ETARIOS:
        if minimo <= edad <= maximo:
            return clave
    return None


def _nombre_partes(apellido_paterno, apellido_materno, nombres, rol_codigo=None):
    partes = (_texto(apellido_paterno), _texto(apellido_materno), _texto(nombres))
    nombre = ' '.join(parte for parte in partes if parte)
    if not nombre:
        return None
    if rol_codigo:
        return f'{nombre} ({rol_codigo})'
    return nombre


def _codigo(catalogo):
    if catalogo is None:
        return None
    return _texto(getattr(catalogo, 'codigo', None))


def _codigo_formulario(catalogo):
    if catalogo is None:
        return None
    return catalogo.codigo_formulario


def _texto(value):
    if value is None:
        return None
    texto = str(value).strip()
    return texto or None


def _secuencia(valor):
    if hasattr(valor, 'all'):
        return list(valor.all())
    return list(valor)
