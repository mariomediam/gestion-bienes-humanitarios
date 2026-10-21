import { useEffect, useRef } from 'react'
import PlusIcon from '@components/icons/PlusIcon'
import TrashIcon from '@components/icons/TrashIcon'
import BienMovimientoSelect, {
  etiquetaUnidadMedida,
} from '@features/movimientos/components/BienMovimientoSelect'

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

function mensajeSignoCantidad(naturaleza) {
  if (naturaleza === 'E' || naturaleza === 'S') {
    return 'Ingrese la cantidad en positivo'
  }
  return ''
}

export default function MovimientoDetalleFilas({
  lineas,
  errores,
  naturaleza,
  disabled,
  soloLectura = false,
  onAgregar,
  onQuitar,
  onCambiar,
}) {
  const avisoSigno = soloLectura ? '' : mensajeSignoCantidad(naturaleza)
  const camposBloqueados = disabled || soloLectura
  const irAlFinalRef = useRef(false)

  useEffect(() => {
    if (!irAlFinalRef.current) return
    irAlFinalRef.current = false
    const desplazables = [document.scrollingElement, document.querySelector('main')].filter(Boolean)
    desplazables.forEach((elemento) => {
      elemento.scrollTo({ top: elemento.scrollHeight, behavior: 'smooth' })
    })
  }, [lineas])

  useEffect(() => {
    if (soloLectura || disabled) return undefined

    function handleKeyDown(event) {
      if (event.repeat || (event.key !== 'Insert' && event.code !== 'Insert')) return
      if (event.target instanceof Element && event.target.closest('[role="dialog"]')) return
      event.preventDefault()
      irAlFinalRef.current = true
      onAgregar()
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [soloLectura, disabled, onAgregar])

  return (
    <section className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-[#1e3064]">Bienes</h2>
          {avisoSigno && <p className="mt-1 text-xs text-gray-600">{avisoSigno}</p>}
          {!soloLectura && (
            <p className="mt-1 text-xs text-gray-600">
              También se pueden agregar bienes presionando la tecla Insert
            </p>
          )}
        </div>
        {!soloLectura && (
          <button
            type="button"
            onClick={onAgregar}
            disabled={disabled}
            title="Insert"
            aria-keyshortcuts="Insert"
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PlusIcon className="w-4 h-4" />
            Agregar bien
          </button>
        )}
      </div>

      {errores.detalles && <p className="text-xs text-red-600">{errores.detalles}</p>}

      {lineas.length === 0 && (
        <p className="text-sm text-gray-600">No hay bienes agregados</p>
      )}

      <div className="space-y-4">
        {lineas.map((linea, index) => {
          const errorLinea = errores[linea.key] || {}
          const unidad = etiquetaUnidadMedida(linea.bien)

          return (
            <div
              key={linea.key}
              className="grid grid-cols-1 gap-3 border border-gray-100 rounded-md p-3 lg:grid-cols-12 lg:items-start"
            >
              <div className={soloLectura ? 'lg:col-span-6' : 'lg:col-span-5'}>
                <label htmlFor={`bien-movimiento-${linea.key}`} className={labelClassName}>
                  Bien
                </label>
                <BienMovimientoSelect
                  inputId={`bien-movimiento-${linea.key}`}
                  value={linea.bien}
                  onChange={(bien) => onCambiar(linea.key, 'bien', bien)}
                  disabled={camposBloqueados}
                />
                {errorLinea.bien && (
                  <p className="mt-1 text-xs text-red-600">{errorLinea.bien}</p>
                )}
              </div>

              <div className="lg:col-span-2">
                <span id={`unidad-bien-${linea.key}`} className={labelClassName}>
                  Unidad de medida
                </span>
                <div
                  aria-labelledby={`unidad-bien-${linea.key}`}
                  className="min-h-[38px] px-3 py-2 border border-gray-200 rounded-md text-sm bg-gray-50 text-gray-700"
                >
                  {unidad || '—'}
                </div>
              </div>

              <div className="lg:col-span-2">
                <label htmlFor={`cantidad-bien-${linea.key}`} className={labelClassName}>
                  Cantidad
                </label>
                <input
                  id={`cantidad-bien-${linea.key}`}
                  type="text"
                  inputMode="decimal"
                  value={linea.cantidad}
                  onChange={(event) => onCambiar(linea.key, 'cantidad', event.target.value)}
                  readOnly={soloLectura}
                  disabled={camposBloqueados}
                  aria-describedby={avisoSigno ? 'aviso-signo-cantidad' : undefined}
                  className={inputClassName}
                />
                {errorLinea.cantidad && (
                  <p className="mt-1 text-xs text-red-600">{errorLinea.cantidad}</p>
                )}
              </div>

              <div className="lg:col-span-2">
                <label htmlFor={`cantidad-texto-bien-${linea.key}`} className={labelClassName}>
                  Cantidad textual
                </label>
                <input
                  id={`cantidad-texto-bien-${linea.key}`}
                  type="text"
                  value={linea.cantidad_texto}
                  onChange={(event) => onCambiar(linea.key, 'cantidad_texto', event.target.value)}
                  maxLength={30}
                  readOnly={soloLectura}
                  disabled={camposBloqueados}
                  className={inputClassName}
                />
                {errorLinea.cantidad_texto && (
                  <p className="mt-1 text-xs text-red-600">{errorLinea.cantidad_texto}</p>
                )}
              </div>

              {!soloLectura && (
                <div className="lg:col-span-1 lg:pt-5">
                  <button
                    type="button"
                    onClick={() => onQuitar(linea.key)}
                    disabled={disabled}
                    aria-label={`Quitar bien ${index + 1}`}
                    className="inline-flex items-center justify-center w-full h-[38px] text-red-600 border border-gray-300 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          )
        })}
      </div>
      {avisoSigno && (
        <p id="aviso-signo-cantidad" className="sr-only">
          {avisoSigno}
        </p>
      )}
    </section>
  )
}
