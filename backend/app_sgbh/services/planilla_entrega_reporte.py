from django.db.models import CharField, OuterRef, Prefetch, Subquery

from ..models import Distrito, MovimientoDetalle, PlanillaEntrega
from .formulario_2a_integrante import contar_integrantes_familia
from .planilla_entrega import PlanillaEntregaServiceError

# The printed planilla always shows these names. The stored ubigeo codes
# stay on the formulario and are not repeated as region or province text.
REGION_REPORTE = 'PIURA'
PROVINCIA_REPORTE = 'PIURA'
ENTREGADO_POR_GORE = ''
MUNICIP_DIST = ''


def encabezado_reporte(planilla, nro_integrantes):
    """Header of one printable planilla BAH.

    Region and province are always PIURA. entregado_por_gore and
    municip_dist stay empty. municip_prov repeats distrito_nombre.
    distrito_nombre comes from the DISTRITO annotation. The address and
    the person names follow the SQL Server + expressions of the print query.
    """
    formulario = _formulario(planilla)
    vivienda = _vivienda(planilla)
    emergencia = _emergencia(planilla)
    persona = _persona(planilla)
    encargado = _encargado(planilla)
    movimiento = planilla.movimiento_almacen
    distrito_nombre = getattr(planilla, 'distrito_nombre', None)
    return {
        'movimiento_id': None if movimiento is None else movimiento.movimiento_id,
        'planilla_entrega_id': planilla.planilla_entrega_id,
        'numero_planilla': planilla.numero_planilla,
        'anio_planilla': planilla.anio_planilla,
        'region_nombre': REGION_REPORTE,
        'provincia_nombre': PROVINCIA_REPORTE,
        'distrito_nombre': distrito_nombre,
        'localidad': None if formulario is None else formulario.localidad,
        'barrio_sector_urbanizacion': (
            None if formulario is None else formulario.barrio_sector_urbanizacion
        ),
        'codigo_sinpad': None if emergencia is None else emergencia.codigo_sinpad,
        'entregado_por_gore': ENTREGADO_POR_GORE,
        'municip_prov': distrito_nombre,
        'municip_dist': MUNICIP_DIST,
        'tipo_peligro_nombre': _tipo_peligro_nombre(emergencia),
        'planilla_fecha_entrega': planilla.fecha_entrega,
        'direccion': direccion_reporte(
            None if formulario is None else formulario.localidad,
            None if formulario is None else formulario.barrio_sector_urbanizacion,
            None if formulario is None else formulario.calle_manzana,
            None if vivienda is None else vivienda.numero_lote,
        ),
        'integrante_receptor_nombre': nombre_completo(
            None if persona is None else persona.apellido_paterno,
            None if persona is None else persona.apellido_materno,
            None if persona is None else persona.nombres,
        ),
        'integrante_receptor_doc_ident': (
            None if persona is None else persona.numero_documento
        ),
        'nro_integrantes_familia': nro_integrantes,
        'encargado_almacen_nombre': nombre_completo(
            None if encargado is None else encargado.apellido_paterno,
            None if encargado is None else encargado.apellido_materno,
            None if encargado is None else encargado.nombres,
        ),
    }


def bienes_reporte(detalles):
    """One printed line per movement detail, in the given order."""
    return [_bien(detalle) for detalle in detalles]


def direccion_reporte(localidad, barrio, calle_manzana, numero_lote):
    """isnull(localidad, '') + ' ' + isnull(barrio, '') + ' ' + isnull('CALLE/MZNA ' + calle, '') + ' LOTE ' + lote.

    SQL Server + yields NULL when numero_lote is NULL, so the whole
    address is NULL. A NULL calle_manzana becomes an empty fragment.
    """
    if numero_lote is None:
        return None
    localidad = '' if localidad is None else localidad
    barrio = '' if barrio is None else barrio
    calle = '' if calle_manzana is None else f'CALLE/MZNA {calle_manzana}'
    return f'{localidad} {barrio} {calle} LOTE {numero_lote}'


def nombre_completo(apellido_paterno, apellido_materno, nombres):
    """apellido_paterno + ' ' + apellido_materno + ' ' + nombres.

    SQL Server + yields NULL when any part is NULL.
    """
    if apellido_paterno is None or apellido_materno is None or nombres is None:
        return None
    return f'{apellido_paterno} {apellido_materno} {nombres}'


def bien_nombre_reporte(nombre, abreviatura):
    """nombre + ' (' + abreviatura + ')'.

    SQL Server + yields NULL when nombre or abreviatura is NULL.
    """
    if nombre is None or abreviatura is None:
        return None
    return f'{nombre} ({abreviatura})'


def armar_reporte(planilla, nro_integrantes):
    """Header plus goods lines for the printable planilla BAH."""
    reporte = encabezado_reporte(planilla, nro_integrantes)
    reporte['bienes'] = bienes_reporte(_detalles_planilla(planilla))
    return reporte


class PlanillaEntregaReporteService:
    @staticmethod
    def get(planilla_entrega_id):
        """Return the printable payload of one planilla BAH.

        Raises PlanillaEntregaServiceError when the planilla does not exist.
        nro_integrantes_familia is the count of the receptor's familia.
        Goods lines are the movement details ordered by categoria orden.
        A planilla without a movement still returns the header and no lines.
        """
        planilla = _planilla_reporte(planilla_entrega_id)
        if planilla is None:
            raise PlanillaEntregaServiceError(
                'La planilla BAH indicada no existe',
                not_found=True,
            )
        receptor = planilla.integrante_receptor
        familia_id = None if receptor is None else receptor.familia_id
        nro_integrantes = contar_integrantes_familia(familia_id)
        return armar_reporte(planilla, nro_integrantes)


def _planilla_reporte(planilla_entrega_id):
    """One planilla with the print-query relations and distrito_nombre.

    Left joins in the print query that are not selected (almacén, tipo de
    movimiento and estado de movimiento) are omitted: they do not add
    columns and do not multiply rows. Distrito has no foreign key, so its
    name is a subquery on the three ubigeo codes, same as the other
    lookups of DISTRITO. Detail lines stay on the movement, ordered by
    S43cat_bah_categorias_bienes.orden.
    """
    distrito_nombre = Distrito.objects.filter(
        departamento_id=OuterRef(
            'integrante_receptor__familia__vivienda__formulario_2a__departamento_id'
        ),
        provincia_id=OuterRef(
            'integrante_receptor__familia__vivienda__formulario_2a__provincia_id'
        ),
        distrito_id=OuterRef(
            'integrante_receptor__familia__vivienda__formulario_2a__distrito_id'
        ),
    ).values('distrito_nombre')[:1]
    return (
        PlanillaEntrega.objects.filter(planilla_entrega_id=planilla_entrega_id)
        .select_related(
            'movimiento_almacen',
            'movimiento_almacen__encargado_almacen',
            'integrante_receptor',
            'integrante_receptor__persona',
            'integrante_receptor__familia',
            'integrante_receptor__familia__vivienda',
            'integrante_receptor__familia__vivienda__formulario_2a',
            'integrante_receptor__familia__vivienda__formulario_2a__emergencia',
            'integrante_receptor__familia__vivienda__formulario_2a__emergencia__tipo_peligro',
        )
        .annotate(distrito_nombre=Subquery(distrito_nombre, output_field=CharField()))
        .prefetch_related(
            Prefetch(
                'movimiento_almacen__detalles',
                queryset=_detalles_reporte(),
            )
        )
        .first()
    )


def _detalles_reporte():
    """Detail rows with bien, unit and category, ordered by category orden."""
    return MovimientoDetalle.objects.select_related(
        'bien',
        'bien__unidad_medida',
        'bien__categoria_bien',
    ).order_by('bien__categoria_bien__orden')


def _detalles_planilla(planilla):
    movimiento = planilla.movimiento_almacen
    if movimiento is None:
        return []
    detalles = movimiento.detalles
    if hasattr(detalles, 'all'):
        return list(detalles.all())
    return list(detalles)


def _bien(detalle):
    bien = detalle.bien
    categoria = None if bien is None else bien.categoria_bien
    unidad = None if bien is None else bien.unidad_medida
    return {
        'categoria_bien_nombre': None if categoria is None else categoria.nombre,
        'bien_nombre': bien_nombre_reporte(
            None if bien is None else bien.nombre,
            None if unidad is None else unidad.abreviatura,
        ),
        'cantidad': detalle.cantidad,
        'cantidad_texto': detalle.cantidad_texto,
    }


def _receptor(planilla):
    return planilla.integrante_receptor


def _familia(planilla):
    receptor = _receptor(planilla)
    if receptor is None:
        return None
    return receptor.familia


def _vivienda(planilla):
    familia = _familia(planilla)
    if familia is None:
        return None
    return familia.vivienda


def _formulario(planilla):
    vivienda = _vivienda(planilla)
    if vivienda is None:
        return None
    return vivienda.formulario_2a


def _emergencia(planilla):
    formulario = _formulario(planilla)
    if formulario is None:
        return None
    return formulario.emergencia


def _persona(planilla):
    receptor = _receptor(planilla)
    if receptor is None:
        return None
    return receptor.persona


def _encargado(planilla):
    movimiento = planilla.movimiento_almacen
    if movimiento is None:
        return None
    return movimiento.encargado_almacen


def _tipo_peligro_nombre(emergencia):
    if emergencia is None or emergencia.tipo_peligro is None:
        return None
    return emergencia.tipo_peligro.nombre
