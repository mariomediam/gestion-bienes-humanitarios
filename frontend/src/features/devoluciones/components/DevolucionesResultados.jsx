import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import EyeIcon from '@components/icons/EyeIcon'
import PencilIcon from '@components/icons/PencilIcon'
import TrashIcon from '@components/icons/TrashIcon'
import DevolucionEliminarModal from '@features/devoluciones/components/DevolucionEliminarModal'
import { formatFechaMovimiento } from '@utils/dates'

const actionButtonClassName =
  'group relative inline-flex items-center justify-center w-8 h-8 text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors'

const deleteButtonClassName =
  'group relative inline-flex items-center justify-center w-8 h-8 text-red-600 bg-white border border-gray-300 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 transition-colors'

const actionTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-[#1e3064] px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

const deleteTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-red-600 px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

function texto(value) {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  return String(value)
}

function BienesCell({ detalles, es_movimiento_mixto }) {
  if (!detalles || detalles.length === 0) {
    return <span className="text-gray-400">—</span>
  }

  return (
    <table className="min-w-full text-xs text-left">
      <thead className="text-gray-500">
        <tr>
          <th scope="col" className="pr-3 py-1 font-medium">Bien</th>
          <th scope="col" className="pr-3 py-1 font-medium">Cantidad</th>
          <th scope="col" className="py-1 font-medium">Cantidad texto</th>
        </tr>
      </thead>
      <tbody>
        {detalles.map((detalle) => (
          <tr key={detalle.movimiento_detalle_id}>
            <td className="pr-3 py-1 text-gray-800">
              {texto(detalle.bien_nombre)} ({texto(detalle.unidad_medida_abreviatura)})
            </td>
            <td className="pr-3 py-1 text-gray-800 whitespace-nowrap">
              {texto(es_movimiento_mixto ? detalle.cantidad : Math.abs(detalle.cantidad))}
            </td>
            <td className="py-1 text-gray-800">{texto(detalle.cantidad_texto)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function DevolucionesResultados({ devoluciones, onModificar, onEliminado }) {
  const navigate = useNavigate()
  const [devolucionAEliminar, setDevolucionAEliminar] = useState(null)

  return (
    <section className="bg-white rounded-lg border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200">
        <h2 className="text-base font-semibold text-[#1e3064]">Resultados de la búsqueda</h2>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-500">
            <tr>
              <th scope="col" className="px-5 py-3 font-medium">Fecha de devolución</th>
              <th scope="col" className="px-5 py-3 font-medium">Documento de referencia origen</th>
              <th scope="col" className="px-5 py-3 font-medium">Documento de referencia</th>
              <th scope="col" className="px-5 py-3 font-medium">Bienes</th>
              <th scope="col" className="px-5 py-3 font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {devoluciones.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-5 py-6 text-center text-gray-500">
                  No se encontraron devoluciones
                </td>
              </tr>
            ) : (
              devoluciones.map((devolucion) => (
                <tr key={devolucion.movimiento_id} className="border-t border-gray-100 align-top">
                  <td className="px-5 py-3 text-gray-800 whitespace-nowrap">
                    {formatFechaMovimiento(devolucion.fecha_movimiento)}
                  </td>
                  <td className="px-5 py-3 text-gray-800">
                    {texto(`${devolucion.tipo_movimiento_origen_nombre} ${devolucion.documento_origen_referencia}`)}
                  </td>
                  <td className="px-5 py-3 text-gray-800">{texto(devolucion.documento_referencia)}</td>
                  <td className="px-5 py-3 text-gray-800">
                    <BienesCell
                      detalles={devolucion.detalles}
                      es_movimiento_mixto={devolucion.tipo_movimiento_naturaleza === 'M'}
                    />
                  </td>
                  <td className="relative z-10 px-5 py-3 whitespace-nowrap">
                    <div className="flex gap-2">
                      <Link
                        to={`/alm-movimientos/${devolucion.movimiento_id}/ver`}
                        state={{ volverA: '/alm-devolucion' }}
                        aria-label="Ver"
                        className={actionButtonClassName}
                      >
                        <EyeIcon className="w-4 h-4" />
                        <span className={actionTooltipClassName} aria-hidden="true">
                          Ver
                        </span>
                      </Link>
                      <button
                        type="button"
                        aria-label="Modificar"
                        className={actionButtonClassName}
                        onClick={() => {
                          onModificar()
                          navigate(`/alm-devolucion/${devolucion.movimiento_id}/editar`)
                        }}
                      >
                        <PencilIcon className="w-4 h-4" />
                        <span className={actionTooltipClassName} aria-hidden="true">
                          Modificar
                        </span>
                      </button>
                      <button
                        type="button"
                        aria-label="Eliminar"
                        onClick={() => setDevolucionAEliminar(devolucion)}
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

      <DevolucionEliminarModal
        isOpen={devolucionAEliminar !== null}
        devolucion={devolucionAEliminar}
        onClose={() => setDevolucionAEliminar(null)}
        onEliminado={onEliminado}
      />
    </section>
  )
}
