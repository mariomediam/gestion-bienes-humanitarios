import { useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import PencilIcon from '@components/icons/PencilIcon'
import TrashIcon from '@components/icons/TrashIcon'
import Formulario2AIntegranteEliminarModal from '@features/formularios2a/components/Formulario2AIntegranteEliminarModal'
import Formulario2AIntegranteFormModal from '@features/formularios2a/components/Formulario2AIntegranteFormModal'

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

function tituloIntegrante(integrante) {
  const nombre = [integrante.apellido_paterno, integrante.apellido_materno, integrante.nombres]
    .filter((parte) => parte !== null && parte !== undefined && parte !== '')
    .join(' ')
  const titulo = `Integrante ${integrante.numero_orden}`
  if (!nombre) return titulo
  return `${titulo} (${nombre})`
}

export default function Formulario2AIntegranteCard({ integrante, onModificado }) {
  const [cargandoEdicion, setCargandoEdicion] = useState(false)
  const [integranteEdicion, setIntegranteEdicion] = useState(null)
  const [confirmandoEliminacion, setConfirmandoEliminacion] = useState(false)

  async function handleModificar() {
    setCargandoEdicion(true)
    try {
      const rows = await sgbhApi.buscarIntegrantes({ integrante_id: integrante.integrante_id })
      const encontrado = Array.isArray(rows) ? rows[0] : null
      if (!encontrado) {
        toast.error('El integrante indicado no existe')
        return
      }
      setIntegranteEdicion(encontrado)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de integrantes'))
    } finally {
      setCargandoEdicion(false)
    }
  }

  function handleIntegranteGuardado() {
    setIntegranteEdicion(null)
    onModificado?.()
  }

  return (
    <section className="min-w-0 rounded-lg border border-gray-200 bg-white">
      <div className="flex min-w-0 flex-wrap items-center gap-2 border-b border-gray-200 px-5 py-4">
        <h4 className="min-w-0 text-sm font-semibold text-[#1e3064] wrap-break-word">
          {tituloIntegrante(integrante)}
        </h4>
        <button
          type="button"
          className={`${secondaryButtonClassName} disabled:opacity-50`}
          onClick={handleModificar}
          disabled={cargandoEdicion}
        >
          <PencilIcon className={buttonIconClassName} />
          Modificar integrante
        </button>
        <button
          type="button"
          className={deleteButtonClassName}
          onClick={() => setConfirmandoEliminacion(true)}
        >
          <TrashIcon className={buttonIconClassName} />
          Eliminar integrante
        </button>
      </div>

      <div className="px-5 py-4">
        <h5 className="text-sm font-semibold text-[#1e3064]">Datos del integrante</h5>
        <dl className="mt-3 grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
          <Campo label="Rol familiar" value={texto(integrante.rol_familiar_nombre)} />
          <Campo label="Edad" value={texto(integrante.edad)} />
          <Campo label="Condición de persona" value={texto(integrante.condicion_persona_nombre)} />
          <Campo label="Tipo de daño personal" value={texto(integrante.tipo_danio_personal_nombre)} />
          <Campo label="Grado de lesión" value={texto(integrante.grado_lesion_nombre)} />
          <Campo label="Semanas de gestación" value={texto(integrante.gestante_semanas)} />
          <Campo label="Tipo de discapacidad" value={texto(integrante.tipo_discapacidad_nombre)} />
          <Campo label="Enfermedad crónica" value={texto(integrante.enfermedad_cronica_nombre)} />
        </dl>
      </div>

      {integranteEdicion && (
        <Formulario2AIntegranteFormModal
          key={integranteEdicion.integrante_id}
          isOpen
          integrante={integranteEdicion}
          onClose={() => setIntegranteEdicion(null)}
          onSaved={handleIntegranteGuardado}
        />
      )}

      <Formulario2AIntegranteEliminarModal
        isOpen={confirmandoEliminacion}
        integrante={integrante}
        onClose={() => setConfirmandoEliminacion(false)}
        onEliminado={onModificado}
      />
    </section>
  )
}
