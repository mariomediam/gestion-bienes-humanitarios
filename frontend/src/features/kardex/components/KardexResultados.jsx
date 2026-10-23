import { filasPresentacion } from '@features/kardex/columnasKardex'
import { formatFechaMovimiento } from '@utils/dates'

function texto(value) {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  return String(value)
}

export default function KardexResultados({ filas, loading, fechaDesde, fechaHasta }) {
  const presentacion = filasPresentacion(filas, { fechaDesde, fechaHasta })

  return (
    <section className="bg-white rounded-lg border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200">
        <h2 className="text-base font-semibold text-[#1e3064]">Resultados de la búsqueda</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-500">
            <tr>
              <th scope="col" className="px-5 py-3 font-medium">Fecha de movimiento</th>
              <th scope="col" className="px-5 py-3 font-medium">Tipo de movimiento</th>
              <th scope="col" className="px-5 py-3 font-medium">Documento de referencia</th>
              <th scope="col" className="px-5 py-3 font-medium">Entrada</th>
              <th scope="col" className="px-5 py-3 font-medium">Salida</th>
              <th scope="col" className="px-5 py-3 font-medium">Saldo</th>
            </tr>
          </thead>
          <tbody>
            {loading && filas.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-6 text-center text-gray-500">
                  Buscando...
                </td>
              </tr>
            ) : presentacion.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-6 text-center text-gray-500">
                  No se encontraron movimientos de almacén
                </td>
              </tr>
            ) : (
              presentacion.map((fila) => (
                <tr key={fila.movimiento_detalle_id} className="border-t border-gray-100">
                  <td className="px-5 py-3 text-gray-800 whitespace-nowrap">
                    {formatFechaMovimiento(fila.fecha_movimiento)}
                  </td>
                  <td className="px-5 py-3 text-gray-800">{texto(fila.tipo_movimiento)}</td>
                  <td className="px-5 py-3 text-gray-800">{texto(fila.documento_referencia)}</td>
                  <td className="px-5 py-3 text-gray-800 whitespace-nowrap">{texto(fila.entrada)}</td>
                  <td className="px-5 py-3 text-gray-800 whitespace-nowrap">{texto(fila.salida)}</td>
                  <td className="px-5 py-3 text-gray-800 whitespace-nowrap">{texto(fila.saldo)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
