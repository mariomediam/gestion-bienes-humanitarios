export const FILTROS_MOVIMIENTO_ORIGEN = {
  fecha_desde: '',
  fecha_hasta: '',
  documento_referencia: '',
  numero_planilla: '',
  tipo_movimiento_id: '',
}

export function buildMovimientoOrigenSearchParams(filtros) {
  const params = {}

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

  if (filtros.tipo_movimiento_id) {
    params.tipo_movimiento_id = filtros.tipo_movimiento_id
  }

  params.naturaleza = 'S'

  return params
}
