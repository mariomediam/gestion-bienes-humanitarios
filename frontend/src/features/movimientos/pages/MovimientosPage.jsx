import { useState } from 'react'
import ExcelIcon from '@components/icons/ExcelIcon'
import PlusIcon from '@components/icons/PlusIcon'
import MovimientosBusquedaForm from '@features/movimientos/components/MovimientosBusquedaForm'
import MovimientosResultados from '@features/movimientos/components/MovimientosResultados'
import { exportMovimientosExcel } from '@features/movimientos/exportMovimientosExcel'
import useMovimientosBusqueda from '@features/movimientos/hooks/useMovimientosBusqueda'
import { buildMovimientoSearchParams } from '@features/movimientos/searchParams'

const EMPTY_FILTROS = {
  fecha_desde: '',
  fecha_hasta: '',
  tipo_movimiento_id: '',
  documento_referencia: '',
  destinatario: '',
}

export default function MovimientosPage() {
  const [bienNombre, setBienNombre] = useState('')
  const [filtros, setFiltros] = useState(EMPTY_FILTROS)
  const [avanzadaAbierta, setAvanzadaAbierta] = useState(false)
  const { loading, searched, movimientos, buscar, limpiarResultados } = useMovimientosBusqueda()

  function handleFiltroChange(name, value) {
    setFiltros((current) => ({ ...current, [name]: value }))
  }

  function handleBuscar(event) {
    event.preventDefault()
    buscar(buildMovimientoSearchParams(bienNombre, filtros))
  }

  function handleLimpiar() {
    setBienNombre('')
    setFiltros(EMPTY_FILTROS)
    setAvanzadaAbierta(false)
    limpiarResultados()
  }

  const hayResultados = searched && movimientos.length > 0

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1e3064]">Movimientos de almacén</h1>
          <p className="mt-1 text-sm text-gray-600">Gestión de movimientos de almacén</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            <PlusIcon className="w-4 h-4" />
            Agregar movimiento
          </button>
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
        onFiltroChange={handleFiltroChange}
        avanzadaAbierta={avanzadaAbierta}
        onToggleAvanzada={() => setAvanzadaAbierta((open) => !open)}
        onSubmit={handleBuscar}
        onLimpiar={handleLimpiar}
        loading={loading}
      />

      {searched && <MovimientosResultados movimientos={movimientos} />}
    </div>
  )
}
