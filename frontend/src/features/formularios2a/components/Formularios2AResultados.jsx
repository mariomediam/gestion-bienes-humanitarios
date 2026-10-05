import PencilIcon from '@components/icons/PencilIcon'
import TrashIcon from '@components/icons/TrashIcon'
import { partesUbicacion } from '@features/formularios2a/ubicacion'
import { formatFechaHora } from '@utils/dates'

const actionButtonClassName =
  'group relative inline-flex items-center justify-center w-8 h-8 text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors'

const deleteButtonClassName =
  'group relative inline-flex items-center justify-center w-8 h-8 text-red-600 bg-white border border-gray-300 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 transition-colors'

const actionTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-[#1e3064] px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

const deleteTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-red-600 px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

function UbicacionCell({ formulario }) {
  const { lugar, lotes } = partesUbicacion(formulario)

  if (!lugar && lotes.length === 0) {
    return <span className="text-gray-400">—</span>
  }

  return (
    <div>
      {lugar && <div>{lugar}</div>}
      {lotes.length > 0 && (
        <ul className="mt-1 list-disc pl-4">
          {formulario.viviendas
            .filter((vivienda) => vivienda.numero_lote)
            .map((vivienda) => (
              <li key={vivienda.vivienda_id}>{vivienda.numero_lote}</li>
            ))}
        </ul>
      )}
    </div>
  )
}

export default function Formularios2AResultados({ formularios }) {
  return (
    <section className="bg-white rounded-lg border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200">
        <h2 className="text-base font-semibold text-[#1e3064]">Resultados de la búsqueda</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-500">
            <tr>
              <th scope="col" className="px-5 py-3 font-medium">Código SINPAD</th>
              <th scope="col" className="px-5 py-3 font-medium">Distrito, barrio y lote</th>
              <th scope="col" className="px-5 py-3 font-medium">Tipo de peligro</th>
              <th scope="col" className="px-5 py-3 font-medium">Fecha y hora de empadronamiento</th>
              <th scope="col" className="px-5 py-3 font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {formularios.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-5 py-6 text-center text-gray-500">
                  No se encontraron formularios EDAN 2A
                </td>
              </tr>
            ) : (
              formularios.map((formulario) => (
                <tr key={formulario.formulario_2a_id} className="border-t border-gray-100">
                  <td className="px-5 py-3 text-gray-800">{formulario.codigo_sinpad || '—'}</td>
                  <td className="px-5 py-3 text-gray-800">
                    <UbicacionCell formulario={formulario} />
                  </td>
                  <td className="px-5 py-3 text-gray-800">{formulario.nombre_tipo_peligro}</td>
                  <td className="px-5 py-3 text-gray-800 whitespace-nowrap">
                    {formatFechaHora(formulario.fecha_empadronamiento, formulario.hora_empadronamiento)}
                  </td>
                  <td className="relative z-10 px-5 py-3 whitespace-nowrap">
                    <div className="flex gap-2">
                      <button
                        type="button"
                        aria-label="Modificar"
                        className={actionButtonClassName}
                      >
                        <PencilIcon className="w-4 h-4" />
                        <span className={actionTooltipClassName} aria-hidden="true">
                          Modificar
                        </span>
                      </button>
                      <button
                        type="button"
                        aria-label="Eliminar"
                        className={deleteButtonClassName}
                      >
                        <TrashIcon className="w-4 h-4" />
                        <span className={deleteTooltipClassName} aria-hidden="true">
                          Eliminar
                        </span>
                      </button>
                    </div>
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
