from django.db import transaction
from django.db.models import Count, Max, ProtectedError

from ..db_router import DB_ALIAS
from ..models import (
    CondicionPersona,
    EnfermedadCronica,
    Formulario2A,
    Formulario2AFamilia,
    Formulario2AIntegrante,
    Formulario2AVivienda,
    GradoLesion,
    Persona,
    PlanillaEntrega,
    RolFamiliar,
    TipoDanioPersonal,
    TipoDiscapacidad,
)
from .formulario_2a import Formulario2AService, Formulario2AServiceError

_SMALLINT_MAX = 32767
_EDAD_MIN = 0
_EDAD_MAX = 130
_GESTANTE_MIN = 1
_GESTANTE_MAX = 45
# DDL check CK_f2a_integrante_grado compares tipo_danio_personal_id to 1.
_TIPO_DANIO_PERMITE_GRADO = 1


class Formulario2AIntegranteServiceError(Exception):
    """Business rule violation for an integrante operation."""

    def __init__(self, message, *, conflict=False, not_found=False):
        super().__init__(message)
        self.message = message
        self.conflict = conflict
        self.not_found = not_found


class Formulario2AIntegranteService:
    @staticmethod
    def search(
        integrante_id=None,
        familia_id=None,
        persona_id=None,
        formulario_2a_id=None,
        codigo_sinpad=None,
    ):
        """Return integrante rows using optional filters combined with AND.

        Filters are exact. formulario_2a_id and codigo_sinpad come from
        the familia chain (vivienda, formulario and emergency). With no
        filters, every row is returned. Ordered by integrante_id. Person
        columns, catalog names and the familia chain come from the related
        rows. The queryset is ready for IntegranteBusquedaSerializer.
        """
        queryset = Formulario2AIntegrante.objects.select_related(
            'persona',
            'persona__tipo_documento',
            'rol_familiar',
            'condicion_persona',
            'tipo_danio_personal',
            'grado_lesion',
            'tipo_discapacidad',
            'enfermedad_cronica',
            'familia',
            'familia__vivienda',
            'familia__vivienda__formulario_2a',
            'familia__vivienda__formulario_2a__emergencia',
        )
        if integrante_id is not None:
            queryset = queryset.filter(integrante_id=integrante_id)
        if familia_id is not None:
            queryset = queryset.filter(familia_id=familia_id)
        if persona_id is not None:
            queryset = queryset.filter(persona_id=persona_id)
        if formulario_2a_id is not None:
            queryset = queryset.filter(
                familia__vivienda__formulario_2a_id=formulario_2a_id,
            )
        if codigo_sinpad is not None:
            queryset = queryset.filter(
                familia__vivienda__formulario_2a__emergencia__codigo_sinpad=(
                    codigo_sinpad
                ),
            )

        return queryset.order_by('integrante_id')

    @staticmethod
    def count(condicion_persona_id=None):
        """Count rows in S43edan_formulario_2a_integrantes.

        Optional filter on condicion_persona_id. When omitted, every row is counted.
        """
        queryset = Formulario2AIntegrante.objects.all()
        if condicion_persona_id is not None:
            queryset = queryset.filter(condicion_persona_id=condicion_persona_id)
        result = queryset.aggregate(total=Count('*'))
        return result['total']

    @staticmethod
    def create(
        *,
        familia_id,
        persona_id,
        rol_familiar_id,
        edad,
        condicion_persona_id,
        tipo_danio_personal_id=None,
        grado_lesion_id=None,
        gestante_semanas=None,
        tipo_discapacidad_id=None,
        enfermedad_cronica_id=None,
    ):
        """Insert one row in S43edan_formulario_2a_integrantes.

        The parent familia must exist and its Formulario 2A must still
        accept changes. numero_orden is the next order of that familia:
        one more than its current maximum, or 1 when it has no integrantes.
        A persona cannot be repeated in the same familia. Catalog foreign
        keys and the persona must exist when they are sent. fecha_creacion
        uses the model default.
        """
        _require_edad(edad)
        _require_gestante(gestante_semanas)
        _require_grado(tipo_danio_personal_id, grado_lesion_id)

        with transaction.atomic(using=DB_ALIAS):
            familia = _require_familia(familia_id)
            vivienda = _require_vivienda(familia.vivienda_id)
            formulario = _require_formulario(vivienda.formulario_2a_id)
            _require_formulario_modificable(formulario)
            _require_persona(persona_id)
            _require_persona_unica(familia_id, persona_id)
            _require_catalogos(
                rol_familiar_id=rol_familiar_id,
                condicion_persona_id=condicion_persona_id,
                tipo_danio_personal_id=tipo_danio_personal_id,
                grado_lesion_id=grado_lesion_id,
                tipo_discapacidad_id=tipo_discapacidad_id,
                enfermedad_cronica_id=enfermedad_cronica_id,
            )
            numero_orden = _siguiente_numero_orden(familia_id)

            integrante = Formulario2AIntegrante(
                familia_id=familia_id,
                persona_id=persona_id,
                rol_familiar_id=rol_familiar_id,
                numero_orden=numero_orden,
                edad=edad,
                condicion_persona_id=condicion_persona_id,
                tipo_danio_personal_id=tipo_danio_personal_id,
                grado_lesion_id=grado_lesion_id,
                gestante_semanas=gestante_semanas,
                tipo_discapacidad_id=tipo_discapacidad_id,
                enfermedad_cronica_id=enfermedad_cronica_id,
            )
            integrante.save()
            stored = _integrante_guardado(integrante.pk)
        return stored

    @staticmethod
    def update(
        integrante_id,
        *,
        persona_id,
        rol_familiar_id,
        edad,
        condicion_persona_id,
        tipo_danio_personal_id=None,
        grado_lesion_id=None,
        gestante_semanas=None,
        tipo_discapacidad_id=None,
        enfermedad_cronica_id=None,
    ):
        """Update the editable columns of one S43edan_formulario_2a_integrantes row.

        The body matches create except familia_id. That column, numero_orden
        and fecha_creacion stay as stored. Rejected when the parent form is
        inactive, a related Planilla BAH is in state EMITIDA, or the persona
        is already an integrante of the same familia.
        """
        _require_edad(edad)
        _require_gestante(gestante_semanas)
        _require_grado(tipo_danio_personal_id, grado_lesion_id)

        with transaction.atomic(using=DB_ALIAS):
            integrante = _require_integrante(integrante_id)
            familia = _require_familia(integrante.familia_id)
            vivienda = _require_vivienda(familia.vivienda_id)
            formulario = _require_formulario(vivienda.formulario_2a_id)
            _require_formulario_modificable(formulario)
            _require_persona(persona_id)
            _require_persona_unica(
                integrante.familia_id,
                persona_id,
                exclude_integrante_id=integrante.pk,
            )
            _require_catalogos(
                rol_familiar_id=rol_familiar_id,
                condicion_persona_id=condicion_persona_id,
                tipo_danio_personal_id=tipo_danio_personal_id,
                grado_lesion_id=grado_lesion_id,
                tipo_discapacidad_id=tipo_discapacidad_id,
                enfermedad_cronica_id=enfermedad_cronica_id,
            )

            integrante.persona_id = persona_id
            integrante.rol_familiar_id = rol_familiar_id
            integrante.edad = edad
            integrante.condicion_persona_id = condicion_persona_id
            integrante.tipo_danio_personal_id = tipo_danio_personal_id
            integrante.grado_lesion_id = grado_lesion_id
            integrante.gestante_semanas = gestante_semanas
            integrante.tipo_discapacidad_id = tipo_discapacidad_id
            integrante.enfermedad_cronica_id = enfermedad_cronica_id
            integrante.save()
            stored = _integrante_guardado(integrante.pk)
        return stored

    @staticmethod
    def delete(integrante_id):
        """Delete one S43edan_formulario_2a_integrantes row.

        Uses the same guards as update: the integrante, its familia, the
        vivienda and the parent Formulario 2A must exist, and the form must
        still accept changes. Also rejected when a Planilla BAH references
        this integrante.
        """
        with transaction.atomic(using=DB_ALIAS):
            integrante = _require_integrante(integrante_id)
            familia = _require_familia(integrante.familia_id)
            vivienda = _require_vivienda(familia.vivienda_id)
            formulario = _require_formulario(vivienda.formulario_2a_id)
            _require_formulario_modificable(formulario)
            if _tiene_planilla(integrante_id):
                raise Formulario2AIntegranteServiceError(
                    'No se puede eliminar el integrante porque tiene planillas de entrega asociadas',
                    conflict=True,
                )

            try:
                integrante.delete()
            except ProtectedError:
                raise Formulario2AIntegranteServiceError(
                    'No se puede eliminar el integrante porque tiene registros asociados',
                    conflict=True,
                ) from None


def _require_edad(edad):
    if isinstance(edad, bool) or not isinstance(edad, int):
        raise Formulario2AIntegranteServiceError(
            'El campo edad debe ser un número entero'
        )
    if edad < _EDAD_MIN or edad > _EDAD_MAX:
        raise Formulario2AIntegranteServiceError(
            'El campo edad debe estar entre 0 y 130'
        )


def _require_gestante(gestante_semanas):
    if gestante_semanas is None:
        return
    if isinstance(gestante_semanas, bool) or not isinstance(gestante_semanas, int):
        raise Formulario2AIntegranteServiceError(
            'El campo gestante_semanas debe ser un número entero'
        )
    if gestante_semanas < _GESTANTE_MIN or gestante_semanas > _GESTANTE_MAX:
        raise Formulario2AIntegranteServiceError(
            'El campo gestante_semanas debe estar entre 1 y 45'
        )


def _require_grado(tipo_danio_personal_id, grado_lesion_id):
    """Apply CK_f2a_integrante_grado without naming the catalog value."""
    if grado_lesion_id is None:
        return
    if tipo_danio_personal_id != _TIPO_DANIO_PERMITE_GRADO:
        raise Formulario2AIntegranteServiceError(
            'El campo grado_lesion_id solo puede enviarse cuando tipo_danio_personal_id es 1'
        )


def _require_integrante(integrante_id):
    try:
        return Formulario2AIntegrante.objects.select_for_update().get(pk=integrante_id)
    except Formulario2AIntegrante.DoesNotExist:
        raise Formulario2AIntegranteServiceError(
            'El integrante indicado no existe',
            not_found=True,
        ) from None


def _require_familia(familia_id):
    try:
        return Formulario2AFamilia.objects.select_for_update().get(pk=familia_id)
    except Formulario2AFamilia.DoesNotExist:
        raise Formulario2AIntegranteServiceError(
            'La familia indicada no existe',
            not_found=True,
        ) from None


def _require_vivienda(vivienda_id):
    try:
        return Formulario2AVivienda.objects.select_for_update().get(pk=vivienda_id)
    except Formulario2AVivienda.DoesNotExist:
        raise Formulario2AIntegranteServiceError(
            'La vivienda indicada no existe',
            not_found=True,
        ) from None


def _require_formulario(formulario_2a_id):
    try:
        return Formulario2A.objects.select_for_update().get(pk=formulario_2a_id)
    except Formulario2A.DoesNotExist:
        raise Formulario2AIntegranteServiceError(
            'El formulario EDAN 2A indicado no existe',
            not_found=True,
        ) from None


def _require_formulario_modificable(formulario):
    try:
        Formulario2AService.require_modificable(formulario)
    except Formulario2AServiceError as exc:
        raise Formulario2AIntegranteServiceError(
            exc.message,
            conflict=exc.conflict,
            not_found=exc.not_found,
        ) from exc


def _tiene_planilla(integrante_id):
    """True when any Planilla BAH uses this integrante as receptor."""
    return PlanillaEntrega.objects.filter(
        integrante_receptor_id=integrante_id,
    ).exists()


def _require_persona(persona_id):
    if not Persona.objects.filter(pk=persona_id).exists():
        raise Formulario2AIntegranteServiceError('La persona indicada no existe')


def _require_persona_unica(familia_id, persona_id, *, exclude_integrante_id=None):
    queryset = Formulario2AIntegrante.objects.filter(
        familia_id=familia_id,
        persona_id=persona_id,
    )
    if exclude_integrante_id is not None:
        queryset = queryset.exclude(pk=exclude_integrante_id)
    if queryset.exists():
        raise Formulario2AIntegranteServiceError(
            'La persona ya está registrada como integrante de esta familia',
            conflict=True,
        )


def _require_catalogos(
    *,
    rol_familiar_id,
    condicion_persona_id,
    tipo_danio_personal_id,
    grado_lesion_id,
    tipo_discapacidad_id,
    enfermedad_cronica_id,
):
    _require_catalogo(
        RolFamiliar,
        rol_familiar_id,
        'El rol familiar indicado no existe',
    )
    _require_catalogo(
        CondicionPersona,
        condicion_persona_id,
        'La condición de persona indicada no existe',
    )
    _require_catalogo_opcional(
        TipoDanioPersonal,
        tipo_danio_personal_id,
        'El tipo de daño personal indicado no existe',
    )
    _require_catalogo_opcional(
        GradoLesion,
        grado_lesion_id,
        'El grado de lesión indicado no existe',
    )
    _require_catalogo_opcional(
        TipoDiscapacidad,
        tipo_discapacidad_id,
        'El tipo de discapacidad indicado no existe',
    )
    _require_catalogo_opcional(
        EnfermedadCronica,
        enfermedad_cronica_id,
        'La enfermedad crónica indicada no existe',
    )


def contar_integrantes_familia(familia_id):
    """Count integrantes that share one familia_id.

    Same count the planilla print query stores in @nro_integrantes: every
    row of S43edan_formulario_2a_integrantes whose familia_id is the
    receptor's. A missing familia returns 0, as the inner joins do when
    the planilla or the receptor is absent.
    """
    if familia_id is None:
        return 0
    result = Formulario2AIntegrante.objects.filter(
        familia_id=familia_id,
    ).aggregate(total=Count('*'))
    return result['total']


def _integrante_guardado(integrante_id):
    return Formulario2AIntegrante.objects.select_related(
        'rol_familiar',
        'condicion_persona',
        'tipo_danio_personal',
        'grado_lesion',
        'tipo_discapacidad',
        'enfermedad_cronica',
    ).get(pk=integrante_id)


def _require_catalogo(model, catalog_id, message):
    if not model.objects.filter(pk=catalog_id).exists():
        raise Formulario2AIntegranteServiceError(message)


def _require_catalogo_opcional(model, catalog_id, message):
    if catalog_id is None:
        return
    _require_catalogo(model, catalog_id, message)


def _siguiente_numero_orden(familia_id):
    """Return the next numero_orden of one familia.

    The caller must already hold the parent familia row lock so two inserts
    of the same familia cannot take the same value.
    """
    max_orden = Formulario2AIntegrante.objects.filter(
        familia_id=familia_id,
    ).aggregate(maximo=Max('numero_orden'))['maximo']
    numero_orden = 1 if max_orden is None else max_orden + 1
    if numero_orden > _SMALLINT_MAX:
        raise Formulario2AIntegranteServiceError(
            'No se puede asignar otro número de orden en la familia',
            conflict=True,
        )
    return numero_orden
