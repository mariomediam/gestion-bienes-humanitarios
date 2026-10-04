export function getFechaUnMesAnterior(from = new Date()) {
  const year = from.getFullYear()
  const month = from.getMonth()
  const day = from.getDate()
  const lastDayOfPreviousMonth = new Date(year, month, 0).getDate()
  const targetDay = Math.min(day, lastDayOfPreviousMonth)
  const target = new Date(year, month - 1, targetDay)
  const targetYear = target.getFullYear()
  const targetMonth = String(target.getMonth() + 1).padStart(2, '0')
  const targetDayText = String(target.getDate()).padStart(2, '0')

  return `${targetYear}-${targetMonth}-${targetDayText}`
}

export function formatFechaHora(fecha, hora) {
  if (!fecha) return '—'

  const [year, month, day] = String(fecha).slice(0, 10).split('-')
  const fechaTexto = `${day}/${month}/${year}`

  if (!hora) return fechaTexto

  return `${fechaTexto} ${String(hora).slice(0, 5)}`
}
