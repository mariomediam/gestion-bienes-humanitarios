import { Link } from 'react-router-dom'
import ExcelIcon from '@components/icons/ExcelIcon'
import PlusIcon from '@components/icons/PlusIcon'
import MovimientosBusquedaForm from '@features/movimientos/components/MovimientosBusquedaForm'
import MovimientosResultados from '@features/movimientos/components/MovimientosResultados'
import { exportMovimientosExcel } from '@features/movimientos/exportMovimientosExcel'
import useMovimientosBusqueda from '@features/movimientos/hooks/useMovimientosBusqueda'

export default function MovimientosPage() {
  const {
    loading,
    searched,
    movimientos,
    bienNombre,
    filtros,
    avanzadaAbierta,
    setBienNombre,
    setFiltro,
    toggleAvanzada,
    buscar,
    limpiar,
    solicitarActualizacion,
    quitarMovimiento,
  } = useMovimientosBusqueda()

  const hayResultados = searched && movimientos.length > 0

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1e3064]">Movimientos de almacén</h1>
          <p className="mt-1 text-sm text-gray-600">Gestión de movimientos de almacén</p>
          <p className="mt-3 rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-[#1e3064]" role="note">
            En esta opción no se visualizan las planillas de BAH. Las planillas deben verse en el menú{' '}
            <Link
              to="/alm-planilla-bah"
              className="font-semibold underline hover:text-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 rounded-sm"
            >
              Planilla BAH
            </Link>
            .
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <Link
            to="/alm-movimientos/nuevo"
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            <PlusIcon className="w-4 h-4" />
            Agregar movimiento
          </Link>
          {hayResultados && (
            <button
              type="button"
              onClick={() => exportMovimientosExcel(movimientos)}
              className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
            >
              <ExcelIcon className="w-4 h-4" />
              Exportar a Excel
            </button>
          )}
        </div>
      </div>

      <MovimientosBusquedaForm
        bienNombre={bienNombre}
        onBienNombreChange={setBienNombre}
        filtros={filtros}
        onFiltroChange={setFiltro}
        avanzadaAbierta={avanzadaAbierta}
        onToggleAvanzada={toggleAvanzada}
        onSubmit={buscar}
        onLimpiar={limpiar}
        loading={loading}
      />

      {searched && (
        <MovimientosResultados
          movimientos={movimientos}
          onModificar={solicitarActualizacion}
          onEliminado={quitarMovimiento}
        />
      )}
    </div>
  )
}
