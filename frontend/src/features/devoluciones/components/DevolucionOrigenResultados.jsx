import { textoNumeroAnio } from '@features/planillasBah/formato'
import { formatFechaMovimiento } from '@utils/dates'

const CODIGO_ENTREGA_BAH = 'ENTREGA_BAH'

function texto(value) {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  return String(value)
}

function referenciaMovimiento(movimiento) {
  if (movimiento.tipo_movimiento_codigo === CODIGO_ENTREGA_BAH) {
    return textoNumeroAnio(movimiento)
  }

  return texto(movimiento.documento_referencia)
}

export default function DevolucionOrigenResultados({
  movimientos,
  movimientoSeleccionadoId,
  onSeleccionar,
}) {
  return (
    <div className="overflow-x-auto border border-gray-200 rounded-lg">
      <table className="min-w-full text-sm text-left">
        <thead className="bg-gray-50 text-gray-500">
          <tr>
            <th scope="col" className="px-4 py-3 font-medium">Tipo de movimiento</th>
            <th scope="col" className="px-4 py-3 font-medium">Documento de referencia</th>
            <th scope="col" className="px-4 py-3 font-medium">Fecha de movimiento</th>
            <th scope="col" className="px-4 py-3 font-medium">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {movimientos.length === 0 ? (
            <tr>
              <td colSpan={4} className="px-4 py-6 text-center text-gray-500">
                No se encontraron movimientos
              </td>
            </tr>
          ) : (
            movimientos.map((movimiento) => {
              const seleccionado = movimiento.movimiento_id === movimientoSeleccionadoId

              return (
                <tr
                  key={movimiento.movimiento_id}
                  className={`border-t border-gray-100 ${seleccionado ? 'bg-gray-50' : ''}`}
                >
                  <td className="px-4 py-3 text-gray-800">
                    {texto(movimiento.tipo_movimiento_nombre)}
                  </td>
                  <td className="px-4 py-3 text-gray-800">
                    {referenciaMovimiento(movimiento)}
                  </td>
                  <td className="px-4 py-3 text-gray-800 whitespace-nowrap">
                    {formatFechaMovimiento(movimiento.fecha_movimiento)}
                  </td>
                  <td className="px-4 py-3 whitespace-nowrap">
                    <button
                      type="button"
                      onClick={() => onSeleccionar(movimiento)}
                      aria-pressed={seleccionado}
                      className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
                    >
                      Seleccionar
                    </button>
                  </td>
                </tr>
              )
            })
          )}
        </tbody>
      </table>
    </div>
  )
}
