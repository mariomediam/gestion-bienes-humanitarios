export function buildMovimientoSearchParams(bienNombre, filtros) {
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

  if (filtros.tipo_movimiento_id) {
    params.tipo_movimiento_id = filtros.tipo_movimiento_id
  }

  const documentoReferencia = filtros.documento_referencia.trim()
  if (documentoReferencia) {
    params.documento_referencia = documentoReferencia
  }

  const destinatario = filtros.destinatario.trim()
  if (destinatario) {
    params.destinatario = destinatario
  }

  return params
}
