import { useState } from 'react'
import ExcelIcon from '@components/icons/ExcelIcon'
import PlusIcon from '@components/icons/PlusIcon'
import PersonaFormModal from '@features/formularios2a/components/PersonaFormModal'
import PersonasBusquedaForm from '@features/personas/components/PersonasBusquedaForm'
import PersonasResultados from '@features/personas/components/PersonasResultados'
import { exportPersonasExcel } from '@features/personas/exportPersonasExcel'
import usePersonasBusqueda from '@features/personas/hooks/usePersonasBusqueda'
import { buildPersonaSearchParams } from '@features/personas/searchParams'

export default function PersonasPage() {
  const [consulta, setConsulta] = useState('')
  const [formularioAbierto, setFormularioAbierto] = useState(false)
  const [personaEdicion, setPersonaEdicion] = useState(null)
  const {
    loading,
    searched,
    personas,
    buscar,
    limpiarResultados,
    reemplazarPersona,
    quitarPersona,
  } = usePersonasBusqueda()

  function handleBuscar(event) {
    event.preventDefault()
    buscar(buildPersonaSearchParams(consulta))
  }

  function handleLimpiar() {
    setConsulta('')
    limpiarResultados()
  }

  function handleAbrirCrear() {
    setPersonaEdicion(null)
    setFormularioAbierto(true)
  }

  function handleAbrirModificar(persona) {
    setPersonaEdicion(persona)
    setFormularioAbierto(true)
  }

  function handleCerrarFormulario() {
    setFormularioAbierto(false)
    setPersonaEdicion(null)
  }

  function handlePersonaGuardada(persona) {
    const eraEdicion = personaEdicion !== null
    setFormularioAbierto(false)
    setPersonaEdicion(null)
    if (eraEdicion) {
      reemplazarPersona(persona)
      return
    }
    buscar({ persona_id: persona.persona_id })
  }

  const hayResultados = searched && personas.length > 0

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1e3064]">Personas</h1>
          <p className="mt-1 text-sm text-gray-600">Gestión de personas</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={handleAbrirCrear}
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            <PlusIcon className="w-4 h-4" />
            Agregar nueva persona
          </button>
          {hayResultados && (
            <button
              type="button"
              onClick={() => exportPersonasExcel(personas)}
              className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
            >
              <ExcelIcon className="w-4 h-4" />
              Exportar a Excel
            </button>
          )}
        </div>
      </div>

      <PersonasBusquedaForm
        consulta={consulta}
        onConsultaChange={setConsulta}
        onSubmit={handleBuscar}
        onLimpiar={handleLimpiar}
        loading={loading}
      />

      {searched && (
        <PersonasResultados
          personas={personas}
          onModificar={handleAbrirModificar}
          onEliminado={quitarPersona}
        />
      )}

      <PersonaFormModal
        key={personaEdicion ? personaEdicion.persona_id : 'nuevo'}
        isOpen={formularioAbierto}
        personaId={personaEdicion ? personaEdicion.persona_id : null}
        onClose={handleCerrarFormulario}
        onSaved={handlePersonaGuardada}
      />
    </div>
  )
}
