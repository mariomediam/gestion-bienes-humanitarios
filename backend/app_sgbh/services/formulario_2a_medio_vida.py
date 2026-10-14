from django.db import transaction

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


def _require_tipo_unico(familia_id, tipo_medio_vida_id):
    """Apply UQ_f2a_medio_vida_familia_tipo before the insert."""
    exists = Formulario2AMedioVida.objects.filter(
        familia_id=familia_id,
        tipo_medio_vida_id=tipo_medio_vida_id,
    ).exists()
    if exists:
        raise Formulario2AMedioVidaServiceError(
            'La familia ya tiene registrado este tipo de medio de vida',
            conflict=True,
        )


def _medio_vida_guardado(medio_vida_id):
    return Formulario2AMedioVida.objects.select_related(
        'tipo_medio_vida',
        'tipo_medio_vida__categoria_medio_vida',
    ).get(pk=medio_vida_id)
