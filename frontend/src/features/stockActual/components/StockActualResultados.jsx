import { Link } from 'react-router-dom'

function texto(value) {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  return String(value)
}

export default function StockActualResultados({ filas }) {
  return (
    <section className="bg-white rounded-lg border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200">
        <h2 className="text-base font-semibold text-[#1e3064]">Resultados de la búsqueda</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-500">
            <tr>
              <th scope="col" className="px-5 py-3 font-medium">Nombre</th>
              <th scope="col" className="px-5 py-3 font-medium">Categoría</th>
              <th scope="col" className="px-5 py-3 font-medium">Unidad de medida</th>
              <th scope="col" className="px-5 py-3 font-medium">Stock actual</th>
              <th scope="col" className="px-5 py-3 font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filas.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-5 py-6 text-center text-gray-500">
                  No se encontraron bienes
                </td>
              </tr>
            ) : (
              filas.map((fila) => (
                <tr key={fila.bien_id} className="border-t border-gray-100">
                  <td className="px-5 py-3 text-gray-800">{texto(fila.nombre)}</td>
                  <td className="px-5 py-3 text-gray-800">{texto(fila.categoria_bien_nombre)}</td>
                  <td className="px-5 py-3 text-gray-800">{texto(fila.unidad_medida_nombre)}</td>
                  <td className="px-5 py-3 text-gray-800 whitespace-nowrap">{texto(fila.stock_actual)}</td>
                  <td className="px-5 py-3 whitespace-nowrap">
                    <Link
                      to={`/alm-stock-actual/${fila.bien_id}/kardex`}
                      className="inline-flex items-center whitespace-nowrap px-3 py-1.5 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
                    >
                      Ver Kardex
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
