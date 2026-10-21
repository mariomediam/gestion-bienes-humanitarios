import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import ExcelIcon from '@components/icons/ExcelIcon'
import PlusIcon from '@components/icons/PlusIcon'
import PlanillaBahSeleccionarFormularioModal from '@features/planillasBah/components/PlanillaBahSeleccionarFormularioModal'
import PlanillasBahBusquedaForm from '@features/planillasBah/components/PlanillasBahBusquedaForm'
import PlanillasBahResultados from '@features/planillasBah/components/PlanillasBahResultados'
import { exportPlanillasBahExcel } from '@features/planillasBah/exportPlanillasBahExcel'
import usePlanillasBahBusqueda from '@features/planillasBah/hooks/usePlanillasBahBusqueda'

export default function PlanillasBahPage() {
  const navigate = useNavigate()
  const [modalAbierto, setModalAbierto] = useState(false)
  const {
    loading,
    searched,
    planillas,
    consulta,
    filtros,
    avanzadaAbierta,
    setConsulta,
    setFiltro,
    toggleAvanzada,
    buscar,
    limpiar,
    solicitarActualizacion,
    quitarPlanilla,
  } = usePlanillasBahBusqueda()

  const hayResultados = searched && planillas.length > 0

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#1e3064]">Planillas BAH</h1>
          <p className="mt-1 text-sm text-gray-600">Gestión de planillas BAH</p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setModalAbierto(true)}
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            <PlusIcon className="w-4 h-4" />
            Agregar planilla
          </button>
          {hayResultados && (
            <button
              type="button"
              onClick={() => exportPlanillasBahExcel(planillas)}
              className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
            >
              <ExcelIcon className="w-4 h-4" />
              Exportar a Excel
            </button>
          )}
        </div>
      </div>

      <PlanillasBahBusquedaForm
        consulta={consulta}
        onConsultaChange={setConsulta}
        filtros={filtros}
        onFiltroChange={setFiltro}
        avanzadaAbierta={avanzadaAbierta}
        onToggleAvanzada={toggleAvanzada}
        onSubmit={buscar}
        onLimpiar={limpiar}
        loading={loading}
      />

      {searched && (
        <PlanillasBahResultados
          planillas={planillas}
          onModificar={solicitarActualizacion}
          onEliminada={quitarPlanilla}
        />
      )}

      <PlanillaBahSeleccionarFormularioModal
        isOpen={modalAbierto}
        onClose={() => setModalAbierto(false)}
        onSeleccionado={(vivienda) => {
          setModalAbierto(false)
          navigate(`/alm-planilla-bah/nuevo/${vivienda.formulario_2a_id}`)
        }}
      />
    </div>
  )
}
