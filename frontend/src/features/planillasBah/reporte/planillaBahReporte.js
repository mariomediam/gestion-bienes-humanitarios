import { format } from '@formkit/tempo'

export const FILAS_PLANILLA = 5
export const GUION_FILA_VACIA = '------'
const SUFIJO_NUMERO_PLANILLA = 'SGGRD-MPP'

const CLASE_CATEGORIA = {
  techo: 'bah-cat-techo',
  abrigo: 'bah-cat-abrigo',
  alimentos: 'bah-cat-alimentos',
  enseres: 'bah-cat-enseres',
  'otros bah': 'bah-cat-otros',
}

export function textoNumeroPlanilla(numero, anio) {
  const tieneNumero = numero !== null && numero !== undefined && numero !== ''
  const tieneAnio = anio !== null && anio !== undefined && anio !== ''

  if (!tieneNumero && !tieneAnio) return ''
  if (!tieneNumero) return `${anio}-${SUFIJO_NUMERO_PLANILLA}`
  if (!tieneAnio) return `${numero}-${SUFIJO_NUMERO_PLANILLA}`
  return `${numero}-${anio}-${SUFIJO_NUMERO_PLANILLA}`
}

export function formatFechaEntregaReporte(value) {
  if (!value) return ''
  return format(String(value).slice(0, 10), 'DD/MM/YYYY', 'es')
}

export function textoReporte(valor) {
  if (valor === null || valor === undefined || valor === '') return ''
  return String(valor)
}

export function gruposPorCategoria(bienes) {
  const grupos = []
  const lista = Array.isArray(bienes) ? bienes : []

  lista.forEach((bien, indice) => {
    const nombre = bien?.categoria_bien_nombre ?? null
    const ultimo = grupos[grupos.length - 1]
    if (ultimo && ultimo.nombre === nombre) {
      ultimo.bienes.push({ bien, indice })
    } else {
      grupos.push({
        nombre,
        bienes: [{ bien, indice }],
      })
    }
  })

  return grupos
}

export function claseCategoria(nombre) {
  if (nombre === null || nombre === undefined || String(nombre).trim() === '') {
    return 'bah-cat-otros'
  }

  const clave = String(nombre).trim().toLowerCase().replace(/\s+/g, ' ')
  return CLASE_CATEGORIA[clave] || 'bah-cat-otros'
}

export function textoCantidadImpresa(bien) {
  const escrito = bien?.cantidad_texto
  if (escrito !== null && escrito !== undefined && String(escrito).trim() !== '') {
    return String(escrito).trim()
  }

  return magnitudCantidad(bien?.cantidad)
}

function magnitudCantidad(cantidad) {
  if (cantidad === null || cantidad === undefined || cantidad === '') return ''

  const limpio = String(cantidad).trim()
  if (!/^-?\d+(\.\d+)?$/.test(limpio)) return ''

  const unsigned = limpio.startsWith('-') ? limpio.slice(1) : limpio
  const [enteraRaw, fracRaw = ''] = unsigned.split('.')
  let entero = BigInt(enteraRaw || '0')
  const digitos = `${fracRaw}000`.slice(0, 3)
  let centesimas = Number(digitos.slice(0, 2))
  if (Number(digitos[2]) >= 5) centesimas += 1
  if (centesimas >= 100) {
    entero += 1n
    centesimas = 0
  }

  if (centesimas === 0) return entero.toString()
  return `${entero}.${String(centesimas).padStart(2, '0')}`
}

export function anchosColumnas(totalBienes) {
  const pesos = [5, 18, 20, 11, 10, ...Array(totalBienes).fill(6), 8]
  const suma = pesos.reduce((total, peso) => total + peso, 0)
  return pesos.map((peso) => `${(peso / suma) * 100}%`)
}
