import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import { formatFechaMovimiento } from '@utils/dates'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function descripcionMovimiento(movimiento) {
  const partes = []

  if (movimiento.tipo_movimiento_nombre) {
    partes.push(movimiento.tipo_movimiento_nombre)
  }

  const fecha = formatFechaMovimiento(movimiento.fecha_movimiento)
  if (fecha !== '—') {
    partes.push(`del ${fecha}`)
  }

  if (movimiento.documento_referencia) {
    partes.push(`con documento ${movimiento.documento_referencia}`)
  }

  return partes.length > 0 ? ` ${partes.join(' ')}` : ''
}

export default function MovimientoEliminarModal({ isOpen, movimiento, onClose, onEliminado }) {
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

  if (!isOpen || !movimiento) return null

  function handleClose() {
    if (eliminando) return
    onClose()
  }

  async function handleConfirmar() {
    if (eliminando) return

    setEliminando(true)
    try {
      await sgbhApi.eliminarMovimiento(movimiento.movimiento_id)
      toast.success('Movimiento de almacén eliminado correctamente')
      onEliminado(movimiento.movimiento_id)
      onClose()
    } catch (error) {
      console.error(error)
      toast.error(getErrorMessage(error, 'No se pudo eliminar el movimiento de almacén'))
    } finally {
      setEliminando(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-eliminar-movimiento"
        className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4"
      >
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 id="titulo-eliminar-movimiento" className="text-lg font-semibold text-[#1e3064]">
            Eliminar movimiento de almacén
          </h2>
        </div>
        <p className="px-6 py-4 text-sm text-gray-700">
          ¿Confirma que desea eliminar el movimiento de almacén
          {descripcionMovimiento(movimiento)} y su detalle?
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
    </div>
  )
}
