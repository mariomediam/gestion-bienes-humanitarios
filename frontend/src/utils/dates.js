import { addMonth, format } from '@formkit/tempo'

export function getFechaUnMesAnterior(from = new Date()) {
  return format(addMonth(from, -1), 'YYYY-MM-DD')
}

export function formatFechaHora(fecha, hora) {
  if (!fecha) return '—'

  const [year, month, day] = String(fecha).slice(0, 10).split('-')
  const fechaTexto = `${day}/${month}/${year}`

  if (!hora) return fechaTexto

  return `${fechaTexto} ${String(hora).slice(0, 5)}`
}
