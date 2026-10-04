from django.db.models import Count, F, OuterRef, Prefetch, Subquery

from ..models import Distrito, Emergencia, Formulario2A

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
        distrito_nombre = Distrito.objects.filter(
            departamento_id=OuterRef('departamento_id'),
            provincia_id=OuterRef('provincia_id'),
            distrito_id=OuterRef('distrito_id'),
        ).values('distrito_nombre')[:1]
        formularios = Formulario2A.objects.annotate(
            distrito_nombre=Subquery(distrito_nombre)
        )
        emergencias = (
            Emergencia.objects.filter(fecha_emergencia__gte=fecha_desde)
            .select_related('tipo_peligro')
            .prefetch_related(Prefetch('formularios_2a', queryset=formularios))
            .order_by('-fecha_emergencia', '-hora_ocurrencia_estimada')
        )

        result = []
        for emergencia in emergencias:
            result.append({
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
            })
        return result
