from django.db.models import CharField, Count, F, OuterRef, Prefetch, Subquery

from ..models import Distrito, Emergencia, Formulario2A
from ..text_search import filter_text_like

_FORMULARIO_UBICACION_FIELDS = (
    'localidad',
    'barrio_sector_urbanizacion',
    'centro_poblado',
    'caserio',
    'anexo',
    'calle_manzana',
    'edificio_piso_dpto',
    'otros_ubicacion',
)


class EmergenciaService:
    @staticmethod
    def count(esta_activo=None):
        """Count rows in S43edan_emergencias.

        Optional filter on esta_activo. When omitted, every row is counted.
        """
        queryset = Emergencia.objects.all()
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)
        result = queryset.aggregate(total=Count('*'))
        return result['total']

    @staticmethod
    def count_by_tipo_peligro(esta_activo=None):
        """Count emergencies grouped by tipo_peligro_id.

        Joins S43cat_tipos_peligro to include nombre as nombre_peligro.
        Optional filter on S43edan_emergencias.esta_activo.
        """
        queryset = Emergencia.objects.all()
        if esta_activo is not None:
            queryset = queryset.filter(esta_activo=esta_activo)
        rows = queryset.values(
            'tipo_peligro_id',
            nombre_peligro=F('tipo_peligro__nombre'),
        ).annotate(total=Count('*'))
        return list(rows)

    @staticmethod
    def list_from_date(fecha_desde):
        """List emergencies with fecha_emergencia >= fecha_desde.

        One item per emergency. Formulario 2A location fields and
        distrito_nombre are nested in formularios_2a.
        """
        return EmergenciaService.search(fecha_desde=fecha_desde)

    @staticmethod
    def search(
        emergencia_id=None,
        codigo_sinpad=None,
        barrio_sector_urbanizacion=None,
        numero_evaluacion=None,
        fecha_desde=None,
        fecha_hasta=None,
        tipo_peligro_id=None,
        localidad=None,
        distrito_nombre=None,
        esta_activo=None,
    ):
        """List emergencies using optional filters combined with AND.

        One item per emergency, ordered by fecha_emergencia and
        hora_ocurrencia_estimada descending. Formulario 2A location fields
        and distrito_nombre are nested in formularios_2a. When a formulario
        or distrito filter is sent, only matching formularios are included.
        """
        formularios = _formularios_con_distrito()
        formulario_filtrado = False
        if barrio_sector_urbanizacion is not None:
            formularios = filter_text_like(
                formularios,
                'barrio_sector_urbanizacion',
                barrio_sector_urbanizacion,
            )
            formulario_filtrado = True
        if localidad is not None:
            formularios = filter_text_like(formularios, 'localidad', localidad)
            formulario_filtrado = True
        if distrito_nombre is not None:
            formularios = filter_text_like(
                formularios,
                'distrito_nombre',
                distrito_nombre,
            )
            formulario_filtrado = True

        emergencias = Emergencia.objects.all()
        if emergencia_id is not None:
            emergencias = emergencias.filter(emergencia_id=emergencia_id)
        if codigo_sinpad is not None:
            emergencias = emergencias.filter(codigo_sinpad=codigo_sinpad)
        if numero_evaluacion is not None:
            emergencias = emergencias.filter(numero_evaluacion=numero_evaluacion)
        if fecha_desde is not None:
            emergencias = emergencias.filter(fecha_emergencia__gte=fecha_desde)
        if fecha_hasta is not None:
            emergencias = emergencias.filter(fecha_emergencia__lte=fecha_hasta)
        if tipo_peligro_id is not None:
            emergencias = emergencias.filter(tipo_peligro_id=tipo_peligro_id)
        if esta_activo is not None:
            emergencias = emergencias.filter(esta_activo=esta_activo)
        if formulario_filtrado:
            emergencias = emergencias.filter(
                emergencia_id__in=formularios.values('emergencia_id')
            )

        emergencias = (
            emergencias.select_related('tipo_peligro')
            .prefetch_related(Prefetch('formularios_2a', queryset=formularios))
            .order_by('-fecha_emergencia', '-hora_ocurrencia_estimada')
        )
        return [_emergencia_to_dict(emergencia) for emergencia in emergencias]


def _formularios_con_distrito():
    """Formulario 2A rows annotated with distrito_nombre."""
    distrito_nombre = Distrito.objects.filter(
        departamento_id=OuterRef('departamento_id'),
        provincia_id=OuterRef('provincia_id'),
        distrito_id=OuterRef('distrito_id'),
    ).values('distrito_nombre')[:1]
    return Formulario2A.objects.annotate(
        distrito_nombre=Subquery(distrito_nombre, output_field=CharField())
    )


def _emergencia_to_dict(emergencia):
    """Map an emergency and its prefetched formularios to the list payload."""
    return {
        'emergencia_id': emergencia.emergencia_id,
        'numero_evaluacion': emergencia.numero_evaluacion,
        'codigo_sinpad': emergencia.codigo_sinpad,
        'tipo_peligro_id': emergencia.tipo_peligro_id,
        'fecha_emergencia': emergencia.fecha_emergencia,
        'hora_ocurrencia_estimada': emergencia.hora_ocurrencia_estimada,
        'esta_activo': emergencia.esta_activo,
        'c_usuari_login': emergencia.c_usuari_login,
        'fecha_creacion': emergencia.fecha_creacion,
        'fecha_modificacion': emergencia.fecha_modificacion,
        'nombre_tipo_peligro': emergencia.tipo_peligro.nombre,
        'formularios_2a': [
            {
                'distrito_nombre': formulario.distrito_nombre,
                **{
                    field: getattr(formulario, field)
                    for field in _FORMULARIO_UBICACION_FIELDS
                },
            }
            for formulario in emergencia.formularios_2a.all()
        ],
    }
