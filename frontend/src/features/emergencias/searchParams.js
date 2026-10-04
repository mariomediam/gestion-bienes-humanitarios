const NUMERIC_SEARCH = /^\d+$/

export function buildEmergenciaSearchParams(consulta, filtros) {
  const params = {}
  const texto = consulta.trim()

  if (texto) {
    if (NUMERIC_SEARCH.test(texto)) {
      params.codigo_sinpad = texto
    } else {
      params.barrio_sector_urbanizacion = texto
    }
  }

  const numeroEvaluacion = filtros.numero_evaluacion.trim()
  if (numeroEvaluacion) {
    params.numero_evaluacion = numeroEvaluacion
  }

  if (filtros.fecha_desde) {
    params.fecha_desde = filtros.fecha_desde
  }

  if (filtros.fecha_hasta) {
    params.fecha_hasta = filtros.fecha_hasta
  }

  if (filtros.tipoPeligro) {
    params.tipo_peligro_id = filtros.tipoPeligro.value
  }

  const localidad = filtros.localidad.trim()
  if (localidad) {
    params.localidad = localidad
  }

  const distritoNombre = filtros.distrito_nombre.trim()
  if (distritoNombre) {
    params.distrito_nombre = distritoNombre
  }

  return params
}
