from django.db import transaction
from django.db.models import ProtectedError

from ..db_router import DB_ALIAS
from ..models import (
    Formulario2A,
    Formulario2AFamilia,
    Formulario2AMedioVida,
    Formulario2AVivienda,
    TipoMedioVida,
)
from .formulario_2a import Formulario2AService, Formulario2AServiceError

_INT_MAX = 2147483647
_OBSERVACION_MAX_LENGTH = 500


class Formulario2AMedioVidaServiceError(Exception):
    """Business rule violation for a medio de vida operation."""

    def __init__(self, message, *, conflict=False, not_found=False):
        super().__init__(message)
        self.message = message
        self.conflict = conflict
        self.not_found = not_found


class Formulario2AMedioVidaService:
    @staticmethod
    def search(medio_vida_id=None, familia_id=None, tipo_medio_vida_id=None):
        """Return medio de vida rows using optional filters combined with AND.

        Filters are exact. With no filters, every row is returned.
        Ordered by medio_vida_id. Catalog names and the familia chain
        come from the related rows. The queryset is ready for
        MedioVidaBusquedaSerializer.
        """
        queryset = Formulario2AMedioVida.objects.select_related(
            'tipo_medio_vida',
            'tipo_medio_vida__categoria_medio_vida',
            'familia',
            'familia__vivienda',
            'familia__vivienda__formulario_2a',
            'familia__vivienda__formulario_2a__emergencia',
        )
        if medio_vida_id is not None:
            queryset = queryset.filter(medio_vida_id=medio_vida_id)
        if familia_id is not None:
            queryset = queryset.filter(familia_id=familia_id)
        if tipo_medio_vida_id is not None:
            queryset = queryset.filter(tipo_medio_vida_id=tipo_medio_vida_id)

        return queryset.order_by('medio_vida_id')

    @staticmethod
    def create(
        *,
        familia_id,
        tipo_medio_vida_id,
        cantidad,
        observacion=None,
    ):
        """Insert one row in S43edan_formulario_2a_medios_vida.

        The parent familia must exist and its Formulario 2A must still
        accept changes. The tipo must exist and cannot repeat in the same
        familia. cantidad must be greater than zero. fecha_creacion uses
        the model default.
        """
        cantidad = _require_cantidad(cantidad)
        observacion = _optional_observacion(observacion)

        with transaction.atomic(using=DB_ALIAS):
            familia = _require_familia(familia_id)
            vivienda = _require_vivienda(familia.vivienda_id)
            formulario = _require_formulario(vivienda.formulario_2a_id)
            _require_formulario_modificable(formulario)
            _require_tipo(tipo_medio_vida_id)
            _require_tipo_unico(familia_id, tipo_medio_vida_id)

            medio_vida = Formulario2AMedioVida(
                familia_id=familia_id,
                tipo_medio_vida_id=tipo_medio_vida_id,
                cantidad=cantidad,
                observacion=observacion,
            )
            medio_vida.save()
            stored = _medio_vida_guardado(medio_vida.pk)
        return stored

    @staticmethod
    def update(
        medio_vida_id,
        *,
        tipo_medio_vida_id,
        cantidad,
        observacion=None,
    ):
        """Update the editable columns of one S43edan_formulario_2a_medios_vida row.

        The body matches create except familia_id. That column and
        fecha_creacion stay as stored. Rejected when the parent form is
        inactive, a related Planilla BAH is in state EMITIDA, or the tipo
        is already registered for the same familia.
        """
        cantidad = _require_cantidad(cantidad)
        observacion = _optional_observacion(observacion)

        with transaction.atomic(using=DB_ALIAS):
            medio_vida = _require_medio_vida(medio_vida_id)
            familia = _require_familia(medio_vida.familia_id)
            vivienda = _require_vivienda(familia.vivienda_id)
            formulario = _require_formulario(vivienda.formulario_2a_id)
            _require_formulario_modificable(formulario)
            _require_tipo(tipo_medio_vida_id)
            _require_tipo_unico(
                medio_vida.familia_id,
                tipo_medio_vida_id,
                exclude_medio_vida_id=medio_vida.pk,
            )

            medio_vida.tipo_medio_vida_id = tipo_medio_vida_id
            medio_vida.cantidad = cantidad
            medio_vida.observacion = observacion
            medio_vida.save()
            stored = _medio_vida_guardado(medio_vida.pk)
        return stored

    @staticmethod
    def delete(medio_vida_id):
        """Delete one S43edan_formulario_2a_medios_vida row.

        Uses the same guards as update: the medio de vida, its familia, the
        vivienda and the parent Formulario 2A must exist, and the form must
        still accept changes.
        """
        with transaction.atomic(using=DB_ALIAS):
            medio_vida = _require_medio_vida(medio_vida_id)
            familia = _require_familia(medio_vida.familia_id)
            vivienda = _require_vivienda(familia.vivienda_id)
            formulario = _require_formulario(vivienda.formulario_2a_id)
            _require_formulario_modificable(formulario)

            try:
                medio_vida.delete()
            except ProtectedError:
                raise Formulario2AMedioVidaServiceError(
                    'No se puede eliminar el medio de vida porque tiene registros asociados',
                    conflict=True,
                ) from None


def _require_cantidad(cantidad):
    if isinstance(cantidad, bool) or not isinstance(cantidad, int):
        raise Formulario2AMedioVidaServiceError(
            'El campo cantidad debe ser un número entero'
        )
    if cantidad < 1:
        raise Formulario2AMedioVidaServiceError(
            'El campo cantidad debe ser mayor que cero'
        )
    if cantidad > _INT_MAX:
        raise Formulario2AMedioVidaServiceError(
            'El campo cantidad debe ser un número entero'
        )
    return cantidad


def _optional_observacion(observacion):
    """Return a trimmed observation. Blank and null become null."""
    if observacion is None:
        return None
    if not isinstance(observacion, str):
        raise Formulario2AMedioVidaServiceError(
            'El campo observacion debe ser texto'
        )
    text = observacion.strip()
    if text == '':
        return None
    if len(text) > _OBSERVACION_MAX_LENGTH:
        raise Formulario2AMedioVidaServiceError(
            'El campo observacion no debe superar 500 caracteres'
        )
    return text


def _require_medio_vida(medio_vida_id):
    try:
        return Formulario2AMedioVida.objects.select_for_update().get(pk=medio_vida_id)
    except Formulario2AMedioVida.DoesNotExist:
        raise Formulario2AMedioVidaServiceError(
            'El medio de vida indicado no existe',
            not_found=True,
        ) from None


def _require_familia(familia_id):
    try:
        return Formulario2AFamilia.objects.select_for_update().get(pk=familia_id)
    except Formulario2AFamilia.DoesNotExist:
        raise Formulario2AMedioVidaServiceError(
            'La familia indicada no existe',
            not_found=True,
        ) from None


def _require_vivienda(vivienda_id):
    try:
        return Formulario2AVivienda.objects.select_for_update().get(pk=vivienda_id)
    except Formulario2AVivienda.DoesNotExist:
        raise Formulario2AMedioVidaServiceError(
            'La vivienda indicada no existe',
            not_found=True,
        ) from None


def _require_formulario(formulario_2a_id):
    try:
        return Formulario2A.objects.select_for_update().get(pk=formulario_2a_id)
    except Formulario2A.DoesNotExist:
        raise Formulario2AMedioVidaServiceError(
            'El formulario EDAN 2A indicado no existe',
            not_found=True,
        ) from None


def _require_formulario_modificable(formulario):
    try:
        Formulario2AService.require_modificable(formulario)
    except Formulario2AServiceError as exc:
        raise Formulario2AMedioVidaServiceError(
            exc.message,
            conflict=exc.conflict,
            not_found=exc.not_found,
        ) from exc


def _require_tipo(tipo_medio_vida_id):
    if not TipoMedioVida.objects.filter(pk=tipo_medio_vida_id).exists():
        raise Formulario2AMedioVidaServiceError(
            'El tipo de medio de vida indicado no existe'
        )


def _require_tipo_unico(
    familia_id,
    tipo_medio_vida_id,
    *,
    exclude_medio_vida_id=None,
):
    """Apply UQ_f2a_medio_vida_familia_tipo before insert or update."""
    queryset = Formulario2AMedioVida.objects.filter(
        familia_id=familia_id,
        tipo_medio_vida_id=tipo_medio_vida_id,
    )
    if exclude_medio_vida_id is not None:
        queryset = queryset.exclude(pk=exclude_medio_vida_id)
    if queryset.exists():
        raise Formulario2AMedioVidaServiceError(
            'La familia ya tiene registrado este tipo de medio de vida',
            conflict=True,
        )


def _medio_vida_guardado(medio_vida_id):
    return Formulario2AMedioVida.objects.select_related(
        'tipo_medio_vida',
        'tipo_medio_vida__categoria_medio_vida',
    ).get(pk=medio_vida_id)
