import { useState } from 'react'
import ExcelIcon from '@components/icons/ExcelIcon'
import PlusIcon from '@components/icons/PlusIcon'
import BienesBusquedaForm from '@features/bienes/components/BienesBusquedaForm'
import BienesResultados from '@features/bienes/components/BienesResultados'
import { exportBienesExcel } from '@features/bienes/exportBienesExcel'
import useBienesBusqueda from '@features/bienes/hooks/useBienesBusqueda'

export default function BienesPage() {
  const [nombre, setNombre] = useState('')
  const { loading, searched, bienes, buscar, limpiarResultados } = useBienesBusqueda()

  function handleBuscar(event) {
    event.preventDefault()
    const valor = nombre.trim()
    buscar(valor ? { nombre: valor } : {})
  }

  function handleLimpiar() {
    setNombre('')
    limpiarResultados()
  }

  const hayResultados = searched && bienes.length > 0

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1e3064]">Bienes de almacén</h1>
          <p className="mt-1 text-sm text-gray-600">Gestión de bienes de almacén</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            <PlusIcon className="w-4 h-4" />
            Agregar nuevo bien
          </button>
          {hayResultados && (
            <button
              type="button"
              onClick={() => exportBienesExcel(bienes)}
              className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
            >
              <ExcelIcon className="w-4 h-4" />
              Exportar a Excel
            </button>
          )}
        </div>
      </div>

      <BienesBusquedaForm
        nombre={nombre}
        onNombreChange={setNombre}
        onSubmit={handleBuscar}
        onLimpiar={handleLimpiar}
        loading={loading}
      />

      {searched && <BienesResultados bienes={bienes} />}
    </div>
  )
}
