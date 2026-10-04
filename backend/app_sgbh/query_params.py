"""Shared parsers for query parameters."""

from datetime import date

_TRUE_VALUES = {'1', 'true'}
_FALSE_VALUES = {'0', 'false'}


def parse_esta_activo(raw_value):
    """Parse the optional esta_activo query param.

    Returns (value, error_message). value is True, False or None.
    None means the filter was omitted.
    """
    if raw_value is None or raw_value == '':
        return None, None

    normalized = str(raw_value).strip().lower()
    if normalized in _TRUE_VALUES:
        return True, None
    if normalized in _FALSE_VALUES:
        return False, None

    return None, 'El filtro esta_activo debe ser 1, 0, true o false'


_SMALLINT_MIN = -32768
_SMALLINT_MAX = 32767


def _parse_optional_smallint(raw_value, field_name):
    """Parse an optional smallint query param.

    Returns (value, error_message). value is an int or None.
    None means the filter was omitted.
    """
    if raw_value is None or str(raw_value).strip() == '':
        return None, None

    normalized = str(raw_value).strip()
    try:
        value = int(normalized)
    except (TypeError, ValueError):
        return None, f'El filtro {field_name} debe ser un número entero'

    if value < _SMALLINT_MIN or value > _SMALLINT_MAX:
        return None, f'El filtro {field_name} debe ser un número entero'

    return value, None


def parse_estado_registro_id(raw_value):
    """Parse the optional estado_registro_id query param."""
    return _parse_optional_smallint(raw_value, 'estado_registro_id')


def parse_estado_planilla_id(raw_value):
    """Parse the optional estado_planilla_id query param."""
    return _parse_optional_smallint(raw_value, 'estado_planilla_id')


def parse_condicion_persona_id(raw_value):
    """Parse the optional condicion_persona_id query param."""
    return _parse_optional_smallint(raw_value, 'condicion_persona_id')


def parse_fecha_desde(raw_value):
    """Parse the required fecha_desde query param as a date.

    Returns (value, error_message).
    """
    if raw_value is None or str(raw_value).strip() == '':
        return None, 'El filtro fecha_desde es obligatorio'

    normalized = str(raw_value).strip()
    try:
        value = date.fromisoformat(normalized)
    except ValueError:
        return None, 'El filtro fecha_desde debe tener el formato AAAA-MM-DD'

    return value, None
