from django.db import transaction
from django.db.models import CharField, Count, F, OuterRef, Prefetch, Subquery
from django.utils import timezone

from ..db_router import DB_ALIAS
from ..models import Distrito, Emergencia, Formulario2A, TipoPeligro
from ..text_search import filter_text_like

_USUARIO_LOGIN_MAX_LENGTH = 20


class EmergenciaServiceError(Exception):
    """Business rule violation for an emergency operation."""

    def __init__(self, message, *, conflict=False, not_found=False):
        super().__init__(message)
        self.message = message
        self.conflict = conflict
        self.not_found = not_found


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
        """Return emergencies with fecha_emergencia >= fecha_desde.

        The queryset is ready for EmergenciaSerializer.
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
        """Return emergencies using optional filters combined with AND.

        Ordered by fecha_emergencia and hora_ocurrencia_estimada descending.
        Related formularios include location fields and distrito_nombre.
        When a formulario or distrito filter is sent, only matching
        formularios are included. The queryset is ready for EmergenciaSerializer.
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
        return emergencias

    @staticmethod
    def create(
        *,
        numero_evaluacion,
        codigo_sinpad,
        tipo_peligro_id,
        fecha_emergencia,
        c_usuari_login,
        hora_ocurrencia_estimada=None,
        esta_activo=True,
    ):
        """Insert one row in S43edan_emergencias.

        codigo_sinpad is required. The insert is rejected when that code
        already exists, compared without case sensitivity.
        c_usuari_login comes from the authenticated user.
        """
        login = str(c_usuari_login or '').strip()
        if login == '' or len(login) > _USUARIO_LOGIN_MAX_LENGTH:
            raise EmergenciaServiceError('No se pudo identificar al usuario')

        codigo_sinpad = _require_codigo_sinpad(codigo_sinpad)

        with transaction.atomic(using=DB_ALIAS):
            _require_tipo_peligro(tipo_peligro_id)
            _require_codigo_sinpad_disponible(codigo_sinpad)

            emergencia = Emergencia(
                numero_evaluacion=numero_evaluacion,
                codigo_sinpad=codigo_sinpad,
                tipo_peligro_id=tipo_peligro_id,
                fecha_emergencia=fecha_emergencia,
                hora_ocurrencia_estimada=hora_ocurrencia_estimada,
                esta_activo=esta_activo,
                c_usuari_login=login,
            )
            emergencia.save()

            stored = (
                Emergencia.objects.select_related('tipo_peligro')
                .prefetch_related(
                    Prefetch('formularios_2a', queryset=_formularios_con_distrito())
                )
                .get(pk=emergencia.pk)
            )
        return stored

    @staticmethod
    def update(
        emergencia_id,
        *,
        numero_evaluacion,
        codigo_sinpad,
        tipo_peligro_id,
        fecha_emergencia,
        hora_ocurrencia_estimada=None,
        esta_activo=True,
    ):
        """Update the editable columns of one S43edan_emergencias row.

        The body matches create. codigo_sinpad must not belong to another
        emergency. c_usuari_login and fecha_creacion stay as stored.
        fecha_modificacion is set to the current time.
        """
        codigo_sinpad = _require_codigo_sinpad(codigo_sinpad)

        with transaction.atomic(using=DB_ALIAS):
            try:
                emergencia = Emergencia.objects.get(pk=emergencia_id)
            except Emergencia.DoesNotExist:
                raise EmergenciaServiceError(
                    'La emergencia indicada no existe',
                    not_found=True,
                )

            _require_tipo_peligro(tipo_peligro_id)
            _require_codigo_sinpad_disponible(
                codigo_sinpad,
                exclude_id=emergencia_id,
            )

            emergencia.numero_evaluacion = numero_evaluacion
            emergencia.codigo_sinpad = codigo_sinpad
            emergencia.tipo_peligro_id = tipo_peligro_id
            emergencia.fecha_emergencia = fecha_emergencia
            emergencia.hora_ocurrencia_estimada = hora_ocurrencia_estimada
            emergencia.esta_activo = esta_activo
            emergencia.fecha_modificacion = timezone.now()
            emergencia.save()

            stored = (
                Emergencia.objects.select_related('tipo_peligro')
                .prefetch_related(
                    Prefetch('formularios_2a', queryset=_formularios_con_distrito())
                )
                .get(pk=emergencia.pk)
            )
        return stored


def _require_codigo_sinpad(codigo_sinpad):
    codigo_sinpad = str(codigo_sinpad or '').strip()
    if codigo_sinpad == '':
        raise EmergenciaServiceError('El campo codigo_sinpad es obligatorio')
    return codigo_sinpad


def _require_tipo_peligro(tipo_peligro_id):
    if not TipoPeligro.objects.filter(pk=tipo_peligro_id).exists():
        raise EmergenciaServiceError('El tipo de peligro indicado no existe')


def _require_codigo_sinpad_disponible(codigo_sinpad, exclude_id=None):
    """Reject codigo_sinpad when another emergency already uses it."""
    queryset = Emergencia.objects.filter(codigo_sinpad__iexact=codigo_sinpad)
    if exclude_id is not None:
        queryset = queryset.exclude(pk=exclude_id)
    if queryset.exists():
        raise EmergenciaServiceError(
            'Ya existe una emergencia con el código SINPAD indicado',
            conflict=True,
        )


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
