import { Link } from 'react-router-dom'
import ExcelIcon from '@components/icons/ExcelIcon'
import PlusIcon from '@components/icons/PlusIcon'
import DevolucionesBusquedaForm from '@features/devoluciones/components/DevolucionesBusquedaForm'
import DevolucionesResultados from '@features/devoluciones/components/DevolucionesResultados'
import { exportDevolucionesExcel } from '@features/devoluciones/exportDevolucionesExcel'
import useDevolucionesBusqueda from '@features/devoluciones/hooks/useDevolucionesBusqueda'

export default function DevolucionesPage() {
  const {
    loading,
    searched,
    devoluciones,
    bienNombre,
    filtros,
    avanzadaAbierta,
    setBienNombre,
    setFiltro,
    toggleAvanzada,
    buscar,
    limpiar,
    solicitarActualizacion,
    quitarDevolucion,
  } = useDevolucionesBusqueda()

  const hayResultados = searched && devoluciones.length > 0

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1e3064]">Devoluciones</h1>
          <p className="mt-1 text-sm text-gray-600">Gestión de devoluciones</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <Link
            to="/alm-devolucion/nuevo"
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            <PlusIcon className="w-4 h-4" />
            Agregar Devolución
          </Link>
          {hayResultados && (
            <button
              type="button"
              onClick={() => exportDevolucionesExcel(devoluciones)}
              className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
            >
              <ExcelIcon className="w-4 h-4" />
              Exportar a Excel
            </button>
          )}
        </div>
      </div>

      <DevolucionesBusquedaForm
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
        <DevolucionesResultados
          devoluciones={devoluciones}
          onModificar={solicitarActualizacion}
          onEliminado={quitarDevolucion}
        />
      )}
    </div>
  )
}
