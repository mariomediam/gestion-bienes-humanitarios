const NUMERIC_SEARCH = /^\d+$/

export function buildPlanillaBahSearchParams(consulta, filtros) {
  const params = {}
  const texto = consulta.trim()

  if (texto) {
    if (NUMERIC_SEARCH.test(texto)) {
      params.numero_planilla = texto
    } else {
      params.bien_nombre = texto
    }
  }

  const anioPlanilla = filtros.anio_planilla.trim()
  if (anioPlanilla) {
    params.anio_planilla = anioPlanilla
  }

  const codigoSinpad = filtros.codigo_sinpad.trim()
  if (codigoSinpad) {
    params.codigo_sinpad = codigoSinpad
  }

  const barrio = filtros.barrio_sector_urbanizacion.trim()
  if (barrio) {
    params.barrio_sector_urbanizacion = barrio
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

  const receptor = filtros.integrante_receptor_nombre.trim()
  if (receptor) {
    params.integrante_receptor_nombre = receptor
  }

  return params
}
