"""Shared parsers for query parameters."""

from datetime import date

_TRUE_VALUES = {'1', 'true'}
_FALSE_VALUES = {'0', 'false'}


def parse_optional_bool(raw_value, field_name):
    """Parse an optional boolean query param.

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

    return None, f'El filtro {field_name} debe ser 1, 0, true o false'


def parse_esta_activo(raw_value):
    """Parse the optional esta_activo query param."""
    return parse_optional_bool(raw_value, 'esta_activo')


def parse_f_activo(raw_value):
    """Parse the optional f_activo query param."""
    return parse_optional_bool(raw_value, 'f_activo')


def parse_es_evaluador_edan(raw_value):
    """Parse the optional es_evaluador_edan query param."""
    return parse_optional_bool(raw_value, 'es_evaluador_edan')


def parse_es_encargado_almacen(raw_value):
    """Parse the optional es_encargado_almacen query param."""
    return parse_optional_bool(raw_value, 'es_encargado_almacen')


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


def parse_tipo_uso_instalacion_id(raw_value):
    """Parse the optional tipo_uso_instalacion_id query param."""
    return _parse_optional_smallint(raw_value, 'tipo_uso_instalacion_id')


def parse_condicion_vivienda_id(raw_value):
    """Parse the optional condicion_vivienda_id query param."""
    return _parse_optional_smallint(raw_value, 'condicion_vivienda_id')


def parse_material_techo_id(raw_value):
    """Parse the optional material_techo_id query param."""
    return _parse_optional_smallint(raw_value, 'material_techo_id')


def parse_codigo_formulario_material_techo(raw_value):
    """Parse the optional codigo_formulario query param for S43cat_materiales_techo."""
    return _parse_optional_smallint(raw_value, 'codigo_formulario')


def parse_material_pared_id(raw_value):
    """Parse the optional material_pared_id query param."""
    return _parse_optional_smallint(raw_value, 'material_pared_id')


def parse_codigo_formulario_material_pared(raw_value):
    """Parse the optional codigo_formulario query param for S43cat_materiales_pared."""
    return _parse_optional_smallint(raw_value, 'codigo_formulario')


def parse_material_piso_id(raw_value):
    """Parse the optional material_piso_id query param."""
    return _parse_optional_smallint(raw_value, 'material_piso_id')


def parse_codigo_formulario_material_piso(raw_value):
    """Parse the optional codigo_formulario query param for S43cat_materiales_piso."""
    return _parse_optional_smallint(raw_value, 'codigo_formulario')


def parse_estado_registro_id(raw_value):
    """Parse the optional estado_registro_id query param."""
    return _parse_optional_smallint(raw_value, 'estado_registro_id')


def parse_estado_planilla_id(raw_value):
    """Parse the optional estado_planilla_id query param."""
    return _parse_optional_smallint(raw_value, 'estado_planilla_id')


def parse_condicion_persona_id(raw_value):
    """Parse the optional condicion_persona_id query param."""
    return _parse_optional_smallint(raw_value, 'condicion_persona_id')


def parse_personal_id(raw_value):
    """Parse the optional personal_id query param."""
    return _parse_optional_smallint(raw_value, 'personal_id')


def parse_fecha_desde(raw_value):
    """Parse the required fecha_desde query param as a date.

    Returns (value, error_message).
    """
    if raw_value is None or str(raw_value).strip() == '':
        return None, 'El filtro fecha_desde es obligatorio'

    return _parse_date(raw_value, 'fecha_desde')


def parse_optional_date(raw_value, field_name):
    """Parse an optional date query param.

    Returns (value, error_message). value is a date or None.
    None means the filter was omitted.
    """
    if raw_value is None or str(raw_value).strip() == '':
        return None, None

    return _parse_date(raw_value, field_name)


def _parse_date(raw_value, field_name):
    """Parse a non-empty date query param. Returns (value, error_message)."""
    normalized = str(raw_value).strip()
    try:
        value = date.fromisoformat(normalized)
    except ValueError:
        return None, f'El filtro {field_name} debe tener el formato AAAA-MM-DD'

    return value, None


_INT_MIN = -2147483648
_INT_MAX = 2147483647


def _parse_optional_int(raw_value, field_name):
    """Parse an optional int query param.

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

    if value < _INT_MIN or value > _INT_MAX:
        return None, f'El filtro {field_name} debe ser un número entero'

    return value, None


def parse_tipo_peligro_id(raw_value):
    """Parse the optional tipo_peligro_id query param."""
    return _parse_optional_int(raw_value, 'tipo_peligro_id')


def parse_emergencia_id(raw_value):
    """Parse the optional emergencia_id query param."""
    return _parse_optional_int(raw_value, 'emergencia_id')


def parse_formulario_2a_id(raw_value):
    """Parse the optional formulario_2a_id query param."""
    return _parse_optional_int(raw_value, 'formulario_2a_id')


def parse_vivienda_id(raw_value):
    """Parse the optional vivienda_id query param."""
    return _parse_optional_int(raw_value, 'vivienda_id')


def _parse_optional_text(raw_value, field_name, max_length):
    """Parse an optional text query param.

    Returns (value, error_message). value is a stripped string or None.
    None means the filter was omitted.
    """
    if raw_value is None:
        return None, None

    normalized = str(raw_value).strip()
    if normalized == '':
        return None, None

    if len(normalized) > max_length:
        return None, (
            f'El filtro {field_name} no debe superar {max_length} caracteres'
        )

    return normalized, None


def parse_codigo_tipo_peligro(raw_value):
    """Parse the optional codigo query param for S43cat_tipos_peligro."""
    return _parse_optional_text(raw_value, 'codigo', 10)


def parse_nombre_tipo_peligro(raw_value):
    """Parse the optional nombre query param for S43cat_tipos_peligro."""
    return _parse_optional_text(raw_value, 'nombre', 200)


def parse_codigo_tipo_uso_instalacion(raw_value):
    """Parse the optional codigo query param for S43cat_tipos_uso_instalacion."""
    return _parse_optional_text(raw_value, 'codigo', 30)


def parse_nombre_tipo_uso_instalacion(raw_value):
    """Parse the optional nombre query param for S43cat_tipos_uso_instalacion."""
    return _parse_optional_text(raw_value, 'nombre', 100)


def parse_codigo_condicion_vivienda(raw_value):
    """Parse the optional codigo query param for S43cat_condiciones_vivienda."""
    return _parse_optional_text(raw_value, 'codigo', 30)


def parse_nombre_condicion_vivienda(raw_value):
    """Parse the optional nombre query param for S43cat_condiciones_vivienda."""
    return _parse_optional_text(raw_value, 'nombre', 100)


def parse_nombre_material_techo(raw_value):
    """Parse the optional nombre query param for S43cat_materiales_techo."""
    return _parse_optional_text(raw_value, 'nombre', 200)


def parse_nombre_material_pared(raw_value):
    """Parse the optional nombre query param for S43cat_materiales_pared."""
    return _parse_optional_text(raw_value, 'nombre', 200)


def parse_nombre_material_piso(raw_value):
    """Parse the optional nombre query param for S43cat_materiales_piso."""
    return _parse_optional_text(raw_value, 'nombre', 200)


def parse_codigo_sinpad(raw_value):
    """Parse the optional codigo_sinpad query param."""
    return _parse_optional_text(raw_value, 'codigo_sinpad', 30)


def parse_numero_evaluacion(raw_value):
    """Parse the optional numero_evaluacion query param."""
    return _parse_optional_text(raw_value, 'numero_evaluacion', 50)


def parse_barrio_sector_urbanizacion(raw_value):
    """Parse the optional barrio_sector_urbanizacion query param."""
    return _parse_optional_text(raw_value, 'barrio_sector_urbanizacion', 250)


def parse_localidad(raw_value):
    """Parse the optional localidad query param."""
    return _parse_optional_text(raw_value, 'localidad', 200)


def parse_distrito_nombre(raw_value):
    """Parse the optional distrito_nombre query param."""
    return _parse_optional_text(raw_value, 'distrito_nombre', 50)


def parse_departamento_id(raw_value):
    """Parse the optional departamento_id query param (CHAR(2))."""
    return _parse_optional_text(raw_value, 'departamento_id', 2)


def parse_provincia_id(raw_value):
    """Parse the optional provincia_id query param (CHAR(2))."""
    return _parse_optional_text(raw_value, 'provincia_id', 2)


def parse_distrito_id(raw_value):
    """Parse the optional distrito_id query param (CHAR(2))."""
    return _parse_optional_text(raw_value, 'distrito_id', 2)
