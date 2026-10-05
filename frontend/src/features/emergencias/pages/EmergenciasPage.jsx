import { useState } from 'react'
import ExcelIcon from '@components/icons/ExcelIcon'
import PlusIcon from '@components/icons/PlusIcon'
import EmergenciaFormModal from '@features/emergencias/components/EmergenciaFormModal'
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
  const [formularioAbierto, setFormularioAbierto] = useState(false)
  const [emergenciaEdicion, setEmergenciaEdicion] = useState(null)
  const {
    loading,
    searched,
    emergencias,
    buscar,
    limpiarResultados,
    reemplazarEmergencia,
    quitarEmergencia,
  } = useEmergenciasBusqueda()

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

  function handleAbrirCrear() {
    setEmergenciaEdicion(null)
    setFormularioAbierto(true)
  }

  function handleAbrirModificar(emergencia) {
    setEmergenciaEdicion(emergencia)
    setFormularioAbierto(true)
  }

  function handleCerrarFormulario() {
    setFormularioAbierto(false)
    setEmergenciaEdicion(null)
  }

  function handleEmergenciaGuardada(emergencia) {
    const eraEdicion = emergenciaEdicion !== null
    setFormularioAbierto(false)
    setEmergenciaEdicion(null)
    if (eraEdicion) {
      reemplazarEmergencia(emergencia)
      return
    }
    buscar({ emergencia_id: emergencia.emergencia_id })
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
            onClick={handleAbrirCrear}
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            <PlusIcon className="w-4 h-4" />
            Agregar nueva emergencia
          </button>
          {hayResultados && (
            <button
              type="button"
              className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
            >
              <ExcelIcon className="w-4 h-4" />
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

      {searched && (
        <EmergenciasResultados
          emergencias={emergencias}
          onModificar={handleAbrirModificar}
          onEliminada={quitarEmergencia}
        />
      )}

      <EmergenciaFormModal
        key={emergenciaEdicion ? emergenciaEdicion.emergencia_id : 'nueva'}
        isOpen={formularioAbierto}
        emergencia={emergenciaEdicion}
        onClose={handleCerrarFormulario}
        onSaved={handleEmergenciaGuardada}
      />
    </div>
  )
}
