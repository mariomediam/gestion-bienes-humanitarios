const ESCALA = 1000000n

function aEntero(value) {
  const texto = String(value ?? '').trim()
  if (!texto) return 0n

  const negativo = texto.startsWith('-')
  const [entero, fraccion = ''] = texto.replace('-', '').split('.')
  const escala = `${fraccion}000000`.slice(0, 6)
  const numero = BigInt(entero || '0') * ESCALA + BigInt(escala)
  return negativo ? -numero : numero
}

function desdeEntero(value) {
  const negativo = value < 0n
  const absoluto = negativo ? -value : value
  const entero = absoluto / ESCALA
  const fraccion = (absoluto % ESCALA).toString().padStart(6, '0')
  return `${negativo ? '-' : ''}${entero}.${fraccion}`
}

function magnitud(value) {
  return desdeEntero(value < 0n ? -value : value)
}

function fechaDia(value) {
  if (!value) return ''
  return String(value).slice(0, 10)
}

function esAnterior(fecha, fechaDesde) {
  return Boolean(fechaDesde) && Boolean(fecha) && fecha < fechaDesde
}

function estaEnPeriodo(fecha, fechaDesde, fechaHasta) {
  if (!fecha) return !fechaDesde && !fechaHasta
  if (fechaDesde && fecha < fechaDesde) return false
  if (fechaHasta && fecha > fechaHasta) return false
  return true
}

export function filasPresentacion(filas, filtros = {}) {
  const fechaDesde = filtros.fechaDesde || ''
  const fechaHasta = filtros.fechaHasta || ''
  let saldo = 0n
  const visibles = []

  filas.forEach((fila) => {
    const fecha = fechaDia(fila.fecha_movimiento)
    const cantidad = aEntero(fila.cantidad)

    if (esAnterior(fecha, fechaDesde)) {
      saldo += cantidad
      return
    }

    if (!estaEnPeriodo(fecha, fechaDesde, fechaHasta)) return

    saldo += cantidad
    const naturaleza = String(fila.naturaleza || '').trim().toUpperCase()
    const entrada = naturaleza === 'E' || (naturaleza === 'M' && cantidad > 0n)
    const salida = naturaleza === 'S' || (naturaleza === 'M' && cantidad < 0n)

    visibles.push({
      ...fila,
      entrada: entrada ? magnitud(cantidad) : null,
      salida: salida ? magnitud(cantidad) : null,
      saldo: desdeEntero(saldo),
    })
  })

  return visibles
}
