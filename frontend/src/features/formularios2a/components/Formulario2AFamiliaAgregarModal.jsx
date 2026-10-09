import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function descripcionVivienda(vivienda) {
  const titulo = `vivienda ${vivienda.numero_orden}`
  if (!vivienda.numero_lote) return titulo
  return `${titulo} (${vivienda.numero_lote})`
}

export default function Formulario2AFamiliaAgregarModal({
  isOpen,
  vivienda,
  onClose,
  onAgregada,
}) {
  const [agregando, setAgregando] = useState(false)

  useEffect(() => {
    if (!isOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !agregando) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, agregando, onClose])

  if (!isOpen || !vivienda) return null

  function handleClose() {
    if (agregando) return
    onClose()
  }

  async function handleConfirmar() {
    if (agregando) return

    setAgregando(true)
    try {
      await sgbhApi.crearFamilia({ vivienda_id: vivienda.vivienda_id })
      toast.success('Familia registrada correctamente')
      await onAgregada?.()
      onClose()
    } catch (error) {
      console.error(error)
      toast.error(getErrorMessage(error, 'No se pudo registrar la familia'))
    } finally {
      setAgregando(false)
    }
  }

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-agregar-familia"
        className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4"
      >
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 id="titulo-agregar-familia" className="text-lg font-semibold text-[#1e3064]">
            Agregar familia
          </h2>
        </div>
        <p className="px-6 py-4 text-sm text-gray-700">
          ¿Confirma que desea agregar una familia a la {descripcionVivienda(vivienda)}?
        </p>
        <div className="flex justify-end gap-3 px-6 py-4">
          <button
            type="button"
            onClick={handleClose}
            disabled={agregando}
            autoFocus
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleConfirmar}
            disabled={agregando}
            className="px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] transition-colors disabled:opacity-50"
          >
            {agregando ? 'Agregando...' : 'Agregar'}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  )
}
