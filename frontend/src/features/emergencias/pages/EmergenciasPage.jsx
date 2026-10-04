import { useState } from 'react'
import EmergenciasBusquedaForm from '@features/emergencias/components/EmergenciasBusquedaForm'
import EmergenciasResultados from '@features/emergencias/components/EmergenciasResultados'
import useEmergenciasBusqueda from '@features/emergencias/hooks/useEmergenciasBusqueda'
import { buildEmergenciaSearchParams } from '@features/emergencias/searchParams'

const EMPTY_FILTROS = {
  numero_evaluacion: '',
  fecha_desde: '',
  fecha_hasta: '',
  tipoPeligro: null,
  localidad: '',
  distrito_nombre: '',
}

export default function EmergenciasPage() {
  const [consulta, setConsulta] = useState('')
  const [filtros, setFiltros] = useState(EMPTY_FILTROS)
  const [avanzadaAbierta, setAvanzadaAbierta] = useState(false)
  const { loading, searched, emergencias, buscar, limpiarResultados } = useEmergenciasBusqueda()

  function handleFiltroChange(name, value) {
    setFiltros((current) => ({ ...current, [name]: value }))
  }

  function handleBuscar(event) {
    event.preventDefault()
    buscar(buildEmergenciaSearchParams(consulta, filtros))
  }

  function handleLimpiar() {
    setConsulta('')
    setFiltros(EMPTY_FILTROS)
    setAvanzadaAbierta(false)
    limpiarResultados()
  }

  const hayResultados = searched && emergencias.length > 0

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1e3064]">Emergencias</h1>
          <p className="mt-1 text-sm text-gray-600">Gestión de emergencias</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            Agregar nueva emergencia
          </button>
          {hayResultados && (
            <button
              type="button"
              className="px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
            >
              Exportar a Excel
            </button>
          )}
        </div>
      </div>

      <EmergenciasBusquedaForm
        consulta={consulta}
        onConsultaChange={setConsulta}
        filtros={filtros}
        onFiltroChange={handleFiltroChange}
        avanzadaAbierta={avanzadaAbierta}
        onToggleAvanzada={() => setAvanzadaAbierta((open) => !open)}
        onSubmit={handleBuscar}
        onLimpiar={handleLimpiar}
        loading={loading}
      />

      {searched && <EmergenciasResultados emergencias={emergencias} />}
    </div>
  )
}
