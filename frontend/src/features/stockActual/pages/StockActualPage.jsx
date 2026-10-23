import { useState } from 'react'
import ExcelIcon from '@components/icons/ExcelIcon'
import StockActualBusquedaForm from '@features/stockActual/components/StockActualBusquedaForm'
import StockActualResultados from '@features/stockActual/components/StockActualResultados'
import { exportStockActualExcel } from '@features/stockActual/exportStockActualExcel'
import useStockActualBusqueda from '@features/stockActual/hooks/useStockActualBusqueda'

export default function StockActualPage() {
  const [bien, setBien] = useState(null)
  const {
    loading,
    searched,
    filas,
    buscar,
    limpiarResultados,
  } = useStockActualBusqueda()

  function handleBuscar(event) {
    event.preventDefault()
    const params = {}
    if (bien?.value) {
      params.bien_id = bien.value
    }
    buscar(params)
  }

  function handleLimpiar() {
    setBien(null)
    limpiarResultados()
  }

  const hayResultados = searched && filas.length > 0

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1e3064]">Stock actual</h1>
          <p className="mt-1 text-sm text-gray-600">Consulta de stock de bienes</p>
        </div>

        {hayResultados && (
          <button
            type="button"
            onClick={() => exportStockActualExcel(filas)}
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            <ExcelIcon className="w-4 h-4" />
            Exportar a Excel
          </button>
        )}
      </div>

      <StockActualBusquedaForm
        bien={bien}
        onBienChange={setBien}
        onSubmit={handleBuscar}
        onLimpiar={handleLimpiar}
        loading={loading}
      />

      {searched && <StockActualResultados filas={filas} />}
    </div>
  )
}
