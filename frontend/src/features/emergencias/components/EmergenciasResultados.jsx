import { useState } from 'react'
import PencilIcon from '@components/icons/PencilIcon'
import TrashIcon from '@components/icons/TrashIcon'
import EmergenciaEliminarModal from '@features/emergencias/components/EmergenciaEliminarModal'
import { formatFechaHora } from '@utils/dates'

const actionButtonClassName =
  'group relative inline-flex items-center justify-center w-8 h-8 text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors'

const deleteButtonClassName =
  'group relative inline-flex items-center justify-center w-8 h-8 text-red-600 bg-white border border-gray-300 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 transition-colors'

const actionTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-[#1e3064] px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

const deleteTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-red-600 px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

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

export default function EmergenciasResultados({ emergencias, onModificar, onEliminada }) {
  const [emergenciaAEliminar, setEmergenciaAEliminar] = useState(null)

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
              <th scope="col" className="px-5 py-3 font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {emergencias.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-6 text-center text-gray-500">
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
                  <td className="relative z-10 px-5 py-3 whitespace-nowrap">
                    <div className="flex gap-2">
                      <button
                        type="button"
                        aria-label="Modificar"
                        onClick={() => onModificar(emergencia)}
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
                        onClick={() => setEmergenciaAEliminar(emergencia)}
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

      <EmergenciaEliminarModal
        isOpen={emergenciaAEliminar !== null}
        emergencia={emergenciaAEliminar}
        onClose={() => setEmergenciaAEliminar(null)}
        onEliminada={onEliminada}
      />
    </section>
  )
}
