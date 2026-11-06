const ESCALA = 6

export function normalizarCantidad(raw) {
  return String(raw ?? '').trim().replace(',', '.')
}

export function textoSaldo(saldo) {
  if (saldo == null) return '—'
  return unidadesATexto(saldo)
}

export function saldoDevolucion(cantidadOrigen, cantidadEntrada) {
  const origen = aUnidades(cantidadOrigen)
  const entrada = aUnidades(cantidadEntrada) ?? 0n
  if (origen == null) return null
  return origen - entrada
}

export function cantidadSuperaSaldo(cantidad, saldo) {
  const valor = aUnidades(normalizarCantidad(cantidad))
  if (valor == null || saldo == null) return false
  return valor > saldo
}

function aUnidades(value) {
  let texto = normalizarCantidad(value)
  if (!texto) return null

  let negativo = false
  if (texto.startsWith('-')) {
    negativo = true
    texto = texto.slice(1)
  }
  if (!/^\d+(\.\d+)?$/.test(texto)) return null

  const [entera, decimal = ''] = texto.split('.')
  const digitos = `${entera}${decimal.padEnd(ESCALA, '0').slice(0, ESCALA)}`
  const unidades = BigInt(digitos)
  return negativo ? -unidades : unidades
}

function unidadesATexto(unidades) {
  const negativo = unidades < 0n
  const digitos = (negativo ? -unidades : unidades).toString().padStart(ESCALA + 1, '0')
  const entera = digitos.slice(0, -ESCALA).replace(/^0+(?=\d)/, '')
  const decimal = digitos.slice(-ESCALA).replace(/0+$/, '')
  const texto = decimal ? `${entera}.${decimal}` : entera
  return negativo && texto !== '0' ? `-${texto}` : texto
}
