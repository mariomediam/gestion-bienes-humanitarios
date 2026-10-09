import { useState } from 'react'
import PlusIcon from '@components/icons/PlusIcon'
import TrashIcon from '@components/icons/TrashIcon'
import Formulario2AFamiliaEliminarModal from '@features/formularios2a/components/Formulario2AFamiliaEliminarModal'

const buttonIconClassName = 'w-4 h-4'

const secondaryButtonClassName =
  'inline-flex max-w-full items-center gap-2 px-4 py-2 text-left text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors'

const deleteButtonClassName =
  'inline-flex max-w-full items-center gap-2 px-4 py-2 text-left text-sm font-medium text-red-600 bg-white border border-gray-300 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 transition-colors'

export default function Formulario2AFamiliaCard({ familia, onEliminada }) {
  const [confirmandoEliminacion, setConfirmandoEliminacion] = useState(false)

  return (
    <section className="min-w-0 rounded-lg border border-gray-200 bg-white">
      <div className="flex min-w-0 flex-wrap items-center gap-2 px-5 py-4">
        <h3 className="min-w-0 text-sm font-semibold text-[#1e3064] wrap-break-word">
          Familia {familia.numero_orden}
        </h3>
        <button
          type="button"
          className={deleteButtonClassName}
          onClick={() => setConfirmandoEliminacion(true)}
        >
          <TrashIcon className={buttonIconClassName} />
          Eliminar familia
        </button>
        <button type="button" className={secondaryButtonClassName}>
          <PlusIcon className={buttonIconClassName} />
          Agregar medio de vida
        </button>
        <button type="button" className={secondaryButtonClassName}>
          <PlusIcon className={buttonIconClassName} />
          Agregar integrante
        </button>
      </div>

      <Formulario2AFamiliaEliminarModal
        isOpen={confirmandoEliminacion}
        familia={familia}
        onClose={() => setConfirmandoEliminacion(false)}
        onEliminada={onEliminada}
      />
    </section>
  )
}
