import { textoSaldo } from '@features/devoluciones/cantidades'

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

function textoBien(bien) {
  const nombre = bien.bien_nombre || '—'
  if (!bien.abreviatura_nombre) return nombre
  return `${nombre} (${bien.abreviatura_nombre})`
}

export default function DevolucionBienes({ bienes, errores, disabled, onCambiarCantidad }) {
  return (
    <section className="bg-white rounded-lg border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-[#1e3064]">Bienes</h2>
        <p className="mt-1 text-xs text-gray-600">Ingrese la cantidad en positivo</p>
      </div>

      {errores.detalles && (
        <p className="px-5 pt-4 text-xs text-red-600">{errores.detalles}</p>
      )}

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-500">
            <tr>
              <th scope="col" className="px-5 py-3 font-medium">Bien</th>
              <th scope="col" className="px-5 py-3 font-medium">Saldo</th>
              <th scope="col" className="px-5 py-3 font-medium">Cantidad</th>
            </tr>
          </thead>
          <tbody>
            {bienes.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-5 py-6 text-center text-gray-500">
                  El movimiento origen no tiene bienes
                </td>
              </tr>
            ) : (
              bienes.map((bien) => {
                const errorLinea = errores[bien.key] || {}

                return (
                  <tr key={bien.key} className="border-t border-gray-100 align-top">
                    <td className="px-5 py-3 text-gray-800">{textoBien(bien)}</td>
                    <td className="px-5 py-3 text-gray-800 whitespace-nowrap">
                      {textoSaldo(bien.saldo)}
                    </td>
                    <td className="px-5 py-3">
                      <label htmlFor={`cantidad-devolucion-${bien.key}`} className="sr-only">
                        Cantidad de {textoBien(bien)}
                      </label>
                      <input
                        id={`cantidad-devolucion-${bien.key}`}
                        type="text"
                        inputMode="decimal"
                        value={bien.cantidad}
                        onChange={(event) => onCambiarCantidad(bien.key, event.target.value)}
                        disabled={disabled}
                        className={inputClassName}
                      />
                      {errorLinea.cantidad && (
                        <p className="mt-1 text-xs text-red-600">{errorLinea.cantidad}</p>
                      )}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
