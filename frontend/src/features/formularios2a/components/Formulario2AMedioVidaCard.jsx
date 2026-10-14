import { useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import PencilIcon from '@components/icons/PencilIcon'
import TrashIcon from '@components/icons/TrashIcon'
import Formulario2AMedioVidaEliminarModal from '@features/formularios2a/components/Formulario2AMedioVidaEliminarModal'
import Formulario2AMedioVidaFormModal from '@features/formularios2a/components/Formulario2AMedioVidaFormModal'

const buttonIconClassName = 'w-4 h-4'

const secondaryButtonClassName =
  'inline-flex max-w-full items-center gap-2 px-4 py-2 text-left text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors'

const deleteButtonClassName =
  'inline-flex max-w-full items-center gap-2 px-4 py-2 text-left text-sm font-medium text-red-600 bg-white border border-gray-300 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 transition-colors'

function texto(value) {
  if (value === null || value === undefined || value === '') return '—'
  return value
}

function Campo({ label, value }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs font-medium text-gray-800">{label}</dt>
      <dd className="mt-0 mb-1 text-sm text-[#1e3064] wrap-break-word">{value}</dd>
    </div>
  )
}

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function tituloMedioVida(medioVida) {
  const nombre = medioVida.tipo_medio_vida_nombre
  if (nombre === null || nombre === undefined || nombre === '') return 'Medio de vida'
  return `Medio de vida (${nombre})`
}

export default function Formulario2AMedioVidaCard({ medioVida, onModificado }) {
  const [cargandoEdicion, setCargandoEdicion] = useState(false)
  const [medioVidaEdicion, setMedioVidaEdicion] = useState(null)
  const [confirmandoEliminacion, setConfirmandoEliminacion] = useState(false)

  async function handleModificar() {
    setCargandoEdicion(true)
    try {
      const rows = await sgbhApi.buscarMediosVida({ medio_vida_id: medioVida.medio_vida_id })
      const encontrado = Array.isArray(rows) ? rows[0] : null
      if (!encontrado) {
        toast.error('El medio de vida indicado no existe')
        return
      }
      setMedioVidaEdicion(encontrado)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de medios de vida'))
    } finally {
      setCargandoEdicion(false)
    }
  }

  function handleMedioVidaGuardado() {
    setMedioVidaEdicion(null)
    onModificado?.()
  }

  return (
    <section className="min-w-0 rounded-lg border border-gray-200 bg-white">
      <div className="flex min-w-0 flex-wrap items-center gap-2 border-b border-gray-200 px-5 py-4">
        <h4 className="min-w-0 text-sm font-semibold text-[#1e3064] wrap-break-word">
          {tituloMedioVida(medioVida)}
        </h4>
        <button
          type="button"
          className={`${secondaryButtonClassName} disabled:opacity-50`}
          onClick={handleModificar}
          disabled={cargandoEdicion}
        >
          <PencilIcon className={buttonIconClassName} />
          Modificar medio de vida
        </button>
        <button
          type="button"
          className={deleteButtonClassName}
          onClick={() => setConfirmandoEliminacion(true)}
        >
          <TrashIcon className={buttonIconClassName} />
          Eliminar medio de vida
        </button>
      </div>

      <div className="px-5 py-4">
        <h5 className="text-sm font-semibold text-[#1e3064]">Datos del medio de vida</h5>
        <dl className="mt-3 grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
          <Campo label="Categoría de medio de vida" value={texto(medioVida.categoria_medio_vida_nombre)} />
          <Campo label="Tipo de medio de vida" value={texto(medioVida.tipo_medio_vida_nombre)} />
          <Campo label="Cantidad" value={texto(medioVida.cantidad)} />
          <Campo label="Observación" value={texto(medioVida.observacion)} />
        </dl>
      </div>

      {medioVidaEdicion && (
        <Formulario2AMedioVidaFormModal
          key={medioVidaEdicion.medio_vida_id}
          isOpen
          medioVida={medioVidaEdicion}
          onClose={() => setMedioVidaEdicion(null)}
          onSaved={handleMedioVidaGuardado}
        />
      )}

      <Formulario2AMedioVidaEliminarModal
        isOpen={confirmandoEliminacion}
        medioVida={medioVida}
        onClose={() => setConfirmandoEliminacion(false)}
        onEliminado={onModificado}
      />
    </section>
  )
}
