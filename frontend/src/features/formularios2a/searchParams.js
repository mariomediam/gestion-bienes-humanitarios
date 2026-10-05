const NUMERIC_SEARCH = /^\d+$/

export function buildFormulario2ASearchParams(consulta, filtros) {
  const params = {}
  const texto = consulta.trim()

  if (texto) {
    if (NUMERIC_SEARCH.test(texto)) {
      params.codigo_sinpad = texto
    } else {
      params.barrio_sector_urbanizacion = texto
    }
  }

  if (filtros.tipoPeligro) {
    params.tipo_peligro_id = filtros.tipoPeligro.value
  }

  if (filtros.distrito) {
    params.departamento_id = filtros.distrito.departamento_id
    params.provincia_id = filtros.distrito.provincia_id
    params.distrito_id = filtros.distrito.distrito_id
  }

  if (filtros.fecha_desde) {
    params.fecha_desde = filtros.fecha_desde
  }

  if (filtros.fecha_hasta) {
    params.fecha_hasta = filtros.fecha_hasta
  }

  const localidad = filtros.localidad.trim()
  if (localidad) {
    params.localidad = localidad
  }

  return params
}
