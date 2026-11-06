export function buildDevolucionSearchParams(bienNombre, filtros) {
  const params = {}
  const nombre = bienNombre.trim()

  if (nombre) {
    params.bien_nombre = nombre
  }

  if (filtros.fecha_desde) {
    params.fecha_desde = filtros.fecha_desde
  }

  if (filtros.fecha_hasta) {
    params.fecha_hasta = filtros.fecha_hasta
  }

  const documentoReferencia = filtros.documento_referencia.trim()
  if (documentoReferencia) {
    params.documento_referencia = documentoReferencia
  }

  const numeroPlanilla = filtros.numero_planilla.trim()
  if (numeroPlanilla) {
    params.numero_planilla = numeroPlanilla
  }

  return params
}
