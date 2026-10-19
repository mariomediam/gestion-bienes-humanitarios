import { format } from '@formkit/tempo'

export function textoVisible(value) {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  return String(value)
}

export function textoPlano(value) {
  if (value === null || value === undefined) {
    return ''
  }

  return String(value)
}

export function formatFechaEntrega(value) {
  if (!value) {
    return '—'
  }

  return format(String(value).slice(0, 10), 'DD/MM/YYYY', 'es')
}

export function textoNumeroAnio(planilla) {
  const numero = planilla.numero_planilla
  const anio = planilla.anio_planilla
  const tieneNumero = numero !== null && numero !== undefined && numero !== ''
  const tieneAnio = anio !== null && anio !== undefined && anio !== ''

  if (!tieneNumero && !tieneAnio) {
    return '—'
  }

  if (!tieneNumero) {
    return String(anio)
  }

  if (!tieneAnio) {
    return String(numero)
  }

  return `${numero}-${anio}`
}

export function textoUbicacion(planilla) {
  const partes = [planilla.distrito_nombre, planilla.barrio_sector_urbanizacion].filter(
    (parte) => parte !== null && parte !== undefined && String(parte).trim() !== '',
  )

  if (planilla.numero_lote) {
    partes.push(`Lote: ${planilla.numero_lote}`)
  }

  if (partes.length === 0) {
    return '—'
  }

  return partes.join(' - ')
}

export function textoCantidad(detalle) {
  if (detalle.cantidad_texto) {
    return String(detalle.cantidad_texto)
  }

  if (detalle.cantidad === null || detalle.cantidad === undefined || detalle.cantidad === '') {
    return '—'
  }

  return String(detalle.cantidad)
}
