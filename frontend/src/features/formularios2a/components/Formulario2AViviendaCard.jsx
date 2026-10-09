import { useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import PencilIcon from '@components/icons/PencilIcon'
import PlusIcon from '@components/icons/PlusIcon'
import TrashIcon from '@components/icons/TrashIcon'
import Formulario2AViviendaEliminarModal from '@features/formularios2a/components/Formulario2AViviendaEliminarModal'
import Formulario2AViviendaFormModal from '@features/formularios2a/components/Formulario2AViviendaFormModal'

const buttonIconClassName = 'w-4 h-4'

const secondaryButtonClassName =
  'inline-flex max-w-full items-center gap-2 px-4 py-2 text-left text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors'

const deleteButtonClassName =
  'inline-flex max-w-full items-center gap-2 px-4 py-2 text-left text-sm font-medium text-red-600 bg-white border border-gray-300 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 transition-colors'

const toggleButtonClassName =
  'group relative inline-flex items-center justify-center px-2 py-2 text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors'

const toggleTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-[#1e3064] px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

function ChevronIcon({ isOpen }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-90' : ''}`}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <polyline points="9 18 15 12 9 6" />
    </svg>
  )
}

function texto(value) {
  if (value === null || value === undefined || value === '') return '—'
  return value
}

function tenencia(value) {
  if (value === null || value === undefined) return '—'
  return value ? 'Sí' : 'No'
}

function Campo({ label, value }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs font-medium text-gray-800">{label}</dt>
      <dd className="mt-0 mb-1 text-sm text-[#1e3064] wrap-break-word">{value}</dd>
    </div>
  )
}

function tituloVivienda(vivienda) {
  const titulo = `Vivienda ${vivienda.numero_orden}`
  if (!vivienda.numero_lote) return titulo
  return `${titulo} (${vivienda.numero_lote})`
}

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function Formulario2AViviendaCard({
  vivienda,
  onViviendaGuardada,
  onViviendaEliminada,
}) {
  const [abierta, setAbierta] = useState(true)
  const [cargandoEdicion, setCargandoEdicion] = useState(false)
  const [viviendaEdicion, setViviendaEdicion] = useState(null)
  const [confirmandoEliminacion, setConfirmandoEliminacion] = useState(false)
  const datosId = `vivienda-${vivienda.vivienda_id}-datos`
  const accion = abierta ? 'Minimizar' : 'Maximizar'

  async function handleModificar() {
    setCargandoEdicion(true)
    try {
      const rows = await sgbhApi.buscarViviendas({ vivienda_id: vivienda.vivienda_id })
      const encontrada = Array.isArray(rows) ? rows[0] : null
      if (!encontrada) {
        toast.error('La vivienda indicada no existe')
        return
      }
      setViviendaEdicion(encontrada)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de viviendas'))
    } finally {
      setCargandoEdicion(false)
    }
  }

  function handleViviendaGuardada(saved) {
    setViviendaEdicion(null)
    onViviendaGuardada?.(saved)
  }

  return (
    <section className="min-w-0 bg-white rounded-lg border border-gray-200">
      <div className={`flex items-start gap-3 px-5 py-4 ${abierta ? 'border-b border-gray-200' : ''}`}>
        <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2">
          <h2 className="min-w-0 text-base font-semibold text-[#1e3064] wrap-break-word">
            {tituloVivienda(vivienda)}
          </h2>
          <button
            type="button"
            className={`${secondaryButtonClassName} disabled:opacity-50`}
            onClick={handleModificar}
            disabled={cargandoEdicion}
          >
            <PencilIcon className={buttonIconClassName} />
            Modificar vivienda
          </button>
          <button
            type="button"
            className={deleteButtonClassName}
            onClick={() => setConfirmandoEliminacion(true)}
          >
            <TrashIcon className={buttonIconClassName} />
            Eliminar vivienda
          </button>
          <button type="button" className={secondaryButtonClassName}>
            <PlusIcon className={buttonIconClassName} />
            Agregar familia
          </button>
        </div>
        <button
          type="button"
          className={`${toggleButtonClassName} shrink-0`}
          aria-expanded={abierta}
          aria-controls={datosId}
          aria-label={`${accion} datos de la vivienda`}
          onClick={() => setAbierta((actual) => !actual)}
        >
          <ChevronIcon isOpen={abierta} />
          <span className={toggleTooltipClassName} aria-hidden="true">
            {accion}
          </span>
        </button>
      </div>

      {abierta && (
        <div id={datosId} className="p-4">
          <div className="rounded-lg border border-gray-200">
            <h3 className="px-5 py-3 text-sm font-semibold text-[#1e3064] border-b border-gray-200">
              Datos de la vivienda
            </h3>
            <dl className="grid grid-cols-1 gap-x-6 gap-y-2 px-5 py-4 sm:grid-cols-2">
              <Campo label="Número de lote" value={texto(vivienda.numero_lote)} />
              <Campo label="Tenencia propia" value={tenencia(vivienda.tenencia_propia)} />
              <Campo label="Tipo de uso de instalación" value={texto(vivienda.tipo_uso_instalacion_nombre)} />
              <Campo label="Condición de vivienda" value={texto(vivienda.condicion_vivienda_nombre)} />
              <Campo label="Material de techo" value={texto(vivienda.material_techo_nombre)} />
              <Campo label="Material de pared" value={texto(vivienda.material_pared_nombre)} />
              <Campo label="Material de piso" value={texto(vivienda.material_piso_nombre)} />
            </dl>
          </div>
        </div>
      )}

      {viviendaEdicion && (
        <Formulario2AViviendaFormModal
          key={viviendaEdicion.vivienda_id}
          isOpen
          vivienda={viviendaEdicion}
          onClose={() => setViviendaEdicion(null)}
          onSaved={handleViviendaGuardada}
        />
      )}

      <Formulario2AViviendaEliminarModal
        isOpen={confirmandoEliminacion}
        vivienda={vivienda}
        onClose={() => setConfirmandoEliminacion(false)}
        onEliminada={onViviendaEliminada}
      />
    </section>
  )
}
