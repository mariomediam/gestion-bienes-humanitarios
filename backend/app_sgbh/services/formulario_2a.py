from django.db import transaction
from django.db.models import CharField, Count, OuterRef, Prefetch, Subquery

from ..db_router import DB_ALIAS
from ..models import (
    Distrito,
    Emergencia,
    EstadoRegistro,
    Formulario2A,
    Formulario2AVivienda,
    Personal,
)
from ..text_search import filter_text_like

_USUARIO_LOGIN_MAX_LENGTH = 20


class Formulario2AServiceError(Exception):
    """Business rule violation for a Formulario 2A operation."""

    def __init__(self, message, *, conflict=False, not_found=False):
        super().__init__(message)
        self.message = message
        self.conflict = conflict
        self.not_found = not_found


class Formulario2AService:
    @staticmethod
    def search(
        codigo_sinpad=None,
        tipo_peligro_id=None,
        departamento_id=None,
        provincia_id=None,
        distrito_id=None,
        fecha_desde=None,
        fecha_hasta=None,
        barrio_sector_urbanizacion=None,
        localidad=None,
        estado_registro_id=None,
    ):
        """Return Formulario 2A rows using optional filters combined with AND.

        fecha_desde and fecha_hasta restrict fecha_empadronamiento.
        barrio_sector_urbanizacion and localidad use a case-insensitive
        partial match. The other filters are exact.
        Ordered by fecha_empadronamiento and hora_empadronamiento descending.
        Each row includes the emergency, the hazard name, distrito_nombre,
        the evaluator name and its viviendas. With no filters, every row
        is returned. The queryset is ready for Formulario2ABusquedaSerializer.
        """
        queryset = _formularios_busqueda()
        if codigo_sinpad is not None:
            queryset = queryset.filter(emergencia__codigo_sinpad=codigo_sinpad)
        if tipo_peligro_id is not None:
            queryset = queryset.filter(emergencia__tipo_peligro_id=tipo_peligro_id)
        if departamento_id is not None:
            queryset = queryset.filter(departamento_id=departamento_id)
        if provincia_id is not None:
            queryset = queryset.filter(provincia_id=provincia_id)
        if distrito_id is not None:
            queryset = queryset.filter(distrito_id=distrito_id)
        if fecha_desde is not None:
            queryset = queryset.filter(fecha_empadronamiento__gte=fecha_desde)
        if fecha_hasta is not None:
            queryset = queryset.filter(fecha_empadronamiento__lte=fecha_hasta)
        if barrio_sector_urbanizacion is not None:
            queryset = filter_text_like(
                queryset,
                'barrio_sector_urbanizacion',
                barrio_sector_urbanizacion,
            )
        if localidad is not None:
            queryset = filter_text_like(queryset, 'localidad', localidad)
        if estado_registro_id is not None:
            queryset = queryset.filter(estado_registro_id=estado_registro_id)

        return queryset.order_by('-fecha_empadronamiento', '-hora_empadronamiento')

    @staticmethod
    def count(estado_registro_id=None):
        """Count rows in S43edan_formulario_2a.

        Optional filter on estado_registro_id. When omitted, every row is counted.
        """
        queryset = Formulario2A.objects.all()
        if estado_registro_id is not None:
            queryset = queryset.filter(estado_registro_id=estado_registro_id)
        result = queryset.aggregate(total=Count('*'))
        return result['total']

    @staticmethod
    def create(
        *,
        emergencia_id,
        departamento_id,
        provincia_id,
        distrito_id,
        fecha_empadronamiento,
        evaluador_id,
        estado_registro_id,
        c_usuari_login,
        hora_empadronamiento=None,
        localidad=None,
        barrio_sector_urbanizacion=None,
        centro_poblado=None,
        caserio=None,
        anexo=None,
        calle_manzana=None,
        edificio_piso_dpto=None,
        otros_ubicacion=None,
        numero_hoja=1,
        total_hojas=None,
        institucion=None,
    ):
        """Insert one row in S43edan_formulario_2a.

        The emergency, district, EDAN evaluator and registration state must
        exist. The evaluator must have es_evaluador_edan enabled.
        c_usuari_login comes from the authenticated user.
        fecha_creacion uses the model default. fecha_modificacion stays null.
        """
        login = str(c_usuari_login or '').strip()
        if login == '' or len(login) > _USUARIO_LOGIN_MAX_LENGTH:
            raise Formulario2AServiceError('No se pudo identificar al usuario')

        _require_hojas(numero_hoja, total_hojas)

        with transaction.atomic(using=DB_ALIAS):
            _require_emergencia(emergencia_id)
            _require_distrito(departamento_id, provincia_id, distrito_id)
            _require_evaluador(evaluador_id)
            _require_estado_registro(estado_registro_id)

            formulario = Formulario2A(
                emergencia_id=emergencia_id,
                departamento_id=departamento_id,
                provincia_id=provincia_id,
                distrito_id=distrito_id,
                fecha_empadronamiento=fecha_empadronamiento,
                hora_empadronamiento=hora_empadronamiento,
                localidad=localidad,
                barrio_sector_urbanizacion=barrio_sector_urbanizacion,
                centro_poblado=centro_poblado,
                caserio=caserio,
                anexo=anexo,
                calle_manzana=calle_manzana,
                edificio_piso_dpto=edificio_piso_dpto,
                otros_ubicacion=otros_ubicacion,
                numero_hoja=numero_hoja,
                total_hojas=total_hojas,
                institucion=institucion,
                evaluador_id=evaluador_id,
                estado_registro_id=estado_registro_id,
                c_usuari_login=login,
            )
            formulario.save()
            stored = _formularios_busqueda().get(pk=formulario.pk)
        return stored


def _require_hojas(numero_hoja, total_hojas):
    if numero_hoja is None or numero_hoja < 1:
        raise Formulario2AServiceError(
            'El campo numero_hoja debe ser un número entero mayor que cero'
        )
    if total_hojas is not None and total_hojas < numero_hoja:
        raise Formulario2AServiceError(
            'El campo total_hojas debe ser mayor o igual que numero_hoja'
        )


def _require_emergencia(emergencia_id):
    if not Emergencia.objects.filter(pk=emergencia_id).exists():
        raise Formulario2AServiceError('La emergencia indicada no existe')


def _require_distrito(departamento_id, provincia_id, distrito_id):
    exists = Distrito.objects.filter(
        departamento_id=departamento_id,
        provincia_id=provincia_id,
        distrito_id=distrito_id,
    ).exists()
    if not exists:
        raise Formulario2AServiceError('El distrito indicado no existe')


def _require_evaluador(evaluador_id):
    personal = Personal.objects.filter(pk=evaluador_id).first()
    if personal is None:
        raise Formulario2AServiceError('El evaluador indicado no existe')
    if not personal.es_evaluador_edan:
        raise Formulario2AServiceError(
            'El personal indicado no puede registrarse como evaluador EDAN'
        )


def _require_estado_registro(estado_registro_id):
    if not EstadoRegistro.objects.filter(pk=estado_registro_id).exists():
        raise Formulario2AServiceError('El estado de registro indicado no existe')


def _formularios_busqueda():
    """Formulario 2A rows with distrito_nombre and nested viviendas.

    distrito_nombre comes from DISTRITO matched by the three ubigeo codes.
    Viviendas stay on the parent row instead of duplicating the formulario.
    """
    distrito_nombre = Distrito.objects.filter(
        departamento_id=OuterRef('departamento_id'),
        provincia_id=OuterRef('provincia_id'),
        distrito_id=OuterRef('distrito_id'),
    ).values('distrito_nombre')[:1]
    viviendas = Formulario2AVivienda.objects.order_by('numero_orden', 'vivienda_id')
    return (
        Formulario2A.objects.annotate(
            distrito_nombre=Subquery(distrito_nombre, output_field=CharField())
        )
        .select_related('emergencia', 'emergencia__tipo_peligro', 'evaluador')
        .prefetch_related(Prefetch('viviendas', queryset=viviendas))
    )
