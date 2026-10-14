import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function descripcionMedioVida(medioVida) {
  const nombre = medioVida.tipo_medio_vida_nombre
  if (nombre === null || nombre === undefined || nombre === '') return 'medio de vida'
  return `medio de vida (${nombre})`
}

export default function Formulario2AMedioVidaEliminarModal({
  isOpen,
  medioVida,
  onClose,
  onEliminado,
}) {
  const [eliminando, setEliminando] = useState(false)

  useEffect(() => {
    if (!isOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !eliminando) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, eliminando, onClose])

  if (!isOpen || !medioVida) return null

  function handleClose() {
    if (eliminando) return
    onClose()
  }

  async function handleConfirmar() {
    if (eliminando) return

    setEliminando(true)
    try {
      await sgbhApi.eliminarMedioVida(medioVida.medio_vida_id)
      toast.success('Medio de vida eliminado correctamente')
      onEliminado?.(medioVida.medio_vida_id)
      onClose()
    } catch (error) {
      console.error(error)
      toast.error(getErrorMessage(error, 'No se pudo eliminar el medio de vida'))
    } finally {
      setEliminando(false)
    }
  }

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-eliminar-medio-vida"
        className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4"
      >
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 id="titulo-eliminar-medio-vida" className="text-lg font-semibold text-[#1e3064]">
            Eliminar medio de vida
          </h2>
        </div>
        <p className="px-6 py-4 text-sm text-gray-700">
          ¿Confirma que desea eliminar el {descripcionMedioVida(medioVida)}?
        </p>
        <div className="flex justify-end gap-3 px-6 py-4">
          <button
            type="button"
            onClick={handleClose}
            disabled={eliminando}
            autoFocus
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleConfirmar}
            disabled={eliminando}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors disabled:opacity-50"
          >
            {eliminando ? 'Eliminando...' : 'Eliminar'}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  )
}
