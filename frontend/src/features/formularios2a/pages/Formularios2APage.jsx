import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ExcelIcon from '@components/icons/ExcelIcon'
import PlusIcon from '@components/icons/PlusIcon'
import Formulario2ACodigoSinpadModal from '@features/formularios2a/components/Formulario2ACodigoSinpadModal'
import Formulario2AFormModal from '@features/formularios2a/components/Formulario2AFormModal'
import Formularios2ABusquedaForm from '@features/formularios2a/components/Formularios2ABusquedaForm'
import Formularios2AResultados from '@features/formularios2a/components/Formularios2AResultados'
import { exportFormularios2AExcel } from '@features/formularios2a/exportFormularios2AExcel'
import useFormularios2ABusqueda from '@features/formularios2a/hooks/useFormularios2ABusqueda'
import { buildFormulario2ASearchParams } from '@features/formularios2a/searchParams'

const EMPTY_FILTROS = {
  tipoPeligro: null,
  distrito: null,
  fecha_desde: '',
  fecha_hasta: '',
  localidad: '',
}

export default function Formularios2APage() {
  const navigate = useNavigate()
  const [consulta, setConsulta] = useState('')
  const [filtros, setFiltros] = useState(EMPTY_FILTROS)
  const [avanzadaAbierta, setAvanzadaAbierta] = useState(false)
  const [codigoModalAbierto, setCodigoModalAbierto] = useState(false)
  const [emergenciaSeleccionada, setEmergenciaSeleccionada] = useState(null)
  const { loading, searched, formularios, buscar, limpiarResultados } = useFormularios2ABusqueda()

  function handleFiltroChange(name, value) {
    setFiltros((current) => ({ ...current, [name]: value }))
  }

  function handleBuscar(event) {
    event.preventDefault()
    buscar(buildFormulario2ASearchParams(consulta, filtros))
  }

  function handleLimpiar() {
    setConsulta('')
    setFiltros(EMPTY_FILTROS)
    setAvanzadaAbierta(false)
    limpiarResultados()
  }

  function handleEmergenciaEncontrada(emergencia) {
    setCodigoModalAbierto(false)
    setEmergenciaSeleccionada(emergencia)
  }

  function handleCerrarFormulario() {
    setEmergenciaSeleccionada(null)
  }

  function handleFormularioGuardado(formulario) {
    setEmergenciaSeleccionada(null)
    navigate(`/formularios-2A/${formulario.formulario_2a_id}`)
  }

  const hayResultados = searched && formularios.length > 0

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1e3064]">Formularios EDAN 2A</h1>
          <p className="mt-1 text-sm text-gray-600">Gestión de formularios EDAN 2A</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setCodigoModalAbierto(true)}
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            <PlusIcon className="w-4 h-4" />
            Agregar formulario 2A
          </button>
          {hayResultados && (
            <button
              type="button"
              onClick={() => exportFormularios2AExcel(formularios)}
              className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
            >
              <ExcelIcon className="w-4 h-4" />
              Exportar a Excel
            </button>
          )}
        </div>
      </div>

      <Formularios2ABusquedaForm
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

      {searched && <Formularios2AResultados formularios={formularios} />}

      <Formulario2ACodigoSinpadModal
        isOpen={codigoModalAbierto}
        onClose={() => setCodigoModalAbierto(false)}
        onEncontrada={handleEmergenciaEncontrada}
      />
      <Formulario2AFormModal
        key={emergenciaSeleccionada ? emergenciaSeleccionada.emergencia_id : 'nuevo'}
        isOpen={emergenciaSeleccionada !== null}
        emergenciaId={emergenciaSeleccionada?.emergencia_id ?? null}
        codigoSinpad={emergenciaSeleccionada?.codigo_sinpad ?? ''}
        onClose={handleCerrarFormulario}
        onSaved={handleFormularioGuardado}
      />
    </div>
  )
}
