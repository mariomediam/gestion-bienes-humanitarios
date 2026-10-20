import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import EyeIcon from '@components/icons/EyeIcon'
import PencilIcon from '@components/icons/PencilIcon'
import TrashIcon from '@components/icons/TrashIcon'
import PlanillaBahEliminarModal from '@features/planillasBah/components/PlanillaBahEliminarModal'
import {
  formatFechaEntrega,
  textoCantidad,
  textoNumeroAnio,
  textoUbicacion,
  textoVisible,
} from '@features/planillasBah/formato'

const actionButtonClassName =
  'group relative inline-flex items-center justify-center w-8 h-8 text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors'

const deleteButtonClassName =
  'group relative inline-flex items-center justify-center w-8 h-8 text-red-600 bg-white border border-gray-300 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 transition-colors'

const actionTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-[#1e3064] px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

const deleteTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-red-600 px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

function BienesCell({ detalles }) {
  if (!detalles || detalles.length === 0) {
    return <span className="text-gray-400">—</span>
  }

  return (
    <table className="min-w-full text-xs text-left">
      <thead className="text-gray-500">
        <tr>
          <th scope="col" className="pr-3 py-1 font-medium">Bien</th>
          <th scope="col" className="pr-3 py-1 font-medium">Unidad</th>
          <th scope="col" className="py-1 font-medium">Cantidad</th>
        </tr>
      </thead>
      <tbody>
        {detalles.map((detalle) => (
          <tr key={detalle.movimiento_detalle_id}>
            <td className="pr-3 py-1 text-gray-800">{textoVisible(detalle.bien_nombre)}</td>
            <td className="pr-3 py-1 text-gray-800">{textoVisible(detalle.unidad_medida_abreviatura)}</td>
            <td className="py-1 text-gray-800 whitespace-nowrap">{textoCantidad(detalle)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function PlanillasBahResultados({ planillas, onEliminada }) {
  const navigate = useNavigate()
  const [planillaAEliminar, setPlanillaAEliminar] = useState(null)

  return (
    <section className="bg-white rounded-lg border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200">
        <h2 className="text-base font-semibold text-[#1e3064]">Resultados de la búsqueda</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-500">
            <tr>
              <th scope="col" className="px-5 py-3 font-medium">Número y año</th>
              <th scope="col" className="px-5 py-3 font-medium">Fecha de entrega</th>
              <th scope="col" className="px-5 py-3 font-medium">Código SINPAD</th>
              <th scope="col" className="px-5 py-3 font-medium">Ubicación</th>
              <th scope="col" className="px-5 py-3 font-medium">Receptor</th>
              <th scope="col" className="px-5 py-3 font-medium">Bienes</th>
              <th scope="col" className="px-5 py-3 font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {planillas.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-5 py-6 text-center text-gray-500">
                  No se encontraron planillas BAH
                </td>
              </tr>
            ) : (
              planillas.map((planilla) => (
                <tr key={planilla.planilla_entrega_id} className="border-t border-gray-100 align-top">
                  <td className="px-5 py-3 text-gray-800 whitespace-nowrap">
                    {textoNumeroAnio(planilla)}
                  </td>
                  <td className="px-5 py-3 text-gray-800 whitespace-nowrap">
                    {formatFechaEntrega(planilla.planilla_fecha_entrega)}
                  </td>
                  <td className="px-5 py-3 text-gray-800">{textoVisible(planilla.codigo_sinpad)}</td>
                  <td className="px-5 py-3 text-gray-800">{textoUbicacion(planilla)}</td>
                  <td className="px-5 py-3 text-gray-800">
                    {textoVisible(planilla.integrante_receptor_nombre)}
                  </td>
                  <td className="px-5 py-3 text-gray-800">
                    <BienesCell detalles={planilla.detalles} />
                  </td>
                  <td className="relative z-10 px-5 py-3 whitespace-nowrap">
                    <div className="flex gap-2">
                      <button
                        type="button"
                        aria-label="Ver"
                        className={actionButtonClassName}
                        onClick={() => navigate(`/alm-planilla-bah/${planilla.planilla_entrega_id}/reporte`)}
                      >
                        <EyeIcon className="w-4 h-4" />
                        <span className={actionTooltipClassName} aria-hidden="true">
                          Ver
                        </span>
                      </button>
                      <Link
                        to={`/alm-planilla-bah/${planilla.movimiento_id}/editar`}
                        aria-label="Modificar"
                        className={actionButtonClassName}
                      >
                        <PencilIcon className="w-4 h-4" />
                        <span className={actionTooltipClassName} aria-hidden="true">
                          Modificar
                        </span>
                      </Link>
                      <button
                        type="button"
                        aria-label="Eliminar"
                        onClick={() => setPlanillaAEliminar(planilla)}
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

      <PlanillaBahEliminarModal
        isOpen={planillaAEliminar !== null}
        planilla={planillaAEliminar}
        onClose={() => setPlanillaAEliminar(null)}
        onEliminada={onEliminada}
      />
    </section>
  )
}
