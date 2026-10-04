import { formatFechaHora } from '@utils/dates'

function UbicacionList({ formularios }) {
  if (!formularios?.length) {
    return <span className="text-gray-400">—</span>
  }

  return (
    <ul className="space-y-1">
      {formularios.map((formulario, index) => {
        const partes = [formulario.distrito_nombre, formulario.barrio_sector_urbanizacion].filter(Boolean)
        return <li key={index}>{partes.join(' - ') || '—'}</li>
      })}
    </ul>
  )
}

export default function EmergenciasResultados({ emergencias }) {
  return (
    <section className="bg-white rounded-lg border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200">
        <h2 className="text-base font-semibold text-[#1e3064]">Resultados de la búsqueda</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-500">
            <tr>
              <th scope="col" className="px-5 py-3 font-medium">Número de evaluación</th>
              <th scope="col" className="px-5 py-3 font-medium">Código SINPAD</th>
              <th scope="col" className="px-5 py-3 font-medium">Ubicación</th>
              <th scope="col" className="px-5 py-3 font-medium">Tipo de peligro</th>
              <th scope="col" className="px-5 py-3 font-medium">Fecha y hora estimada</th>
            </tr>
          </thead>
          <tbody>
            {emergencias.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-5 py-6 text-center text-gray-500">
                  No se encontraron emergencias
                </td>
              </tr>
            ) : (
              emergencias.map((emergencia) => (
                <tr key={emergencia.emergencia_id} className="border-t border-gray-100">
                  <td className="px-5 py-3 text-gray-800">{emergencia.numero_evaluacion}</td>
                  <td className="px-5 py-3 text-gray-800">{emergencia.codigo_sinpad || '—'}</td>
                  <td className="px-5 py-3 text-gray-800">
                    <UbicacionList formularios={emergencia.formularios_2a} />
                  </td>
                  <td className="px-5 py-3 text-gray-800">{emergencia.nombre_tipo_peligro}</td>
                  <td className="px-5 py-3 text-gray-800 whitespace-nowrap">
                    {formatFechaHora(emergencia.fecha_emergencia, emergencia.hora_ocurrencia_estimada)}
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
