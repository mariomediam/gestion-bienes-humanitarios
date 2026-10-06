import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function Formulario2ACodigoSinpadModal({ isOpen, onClose, onEncontrada }) {
  const [codigoSinpad, setCodigoSinpad] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!isOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !loading) {
        setCodigoSinpad('')
        setError('')
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, loading, onClose])

  if (!isOpen) return null

  function handleClose() {
    if (loading) return
    setCodigoSinpad('')
    setError('')
    onClose()
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const codigo = codigoSinpad.trim()
    if (!codigo) {
      setError('El código SINPAD es obligatorio')
      return
    }

    setLoading(true)
    try {
      const rows = await sgbhApi.buscarEmergencias({ codigo_sinpad: codigo })
      if (!Array.isArray(rows) || rows.length === 0 || !rows[0]?.emergencia_id) {
        toast.error('No se encontró una emergencia con el código SINPAD indicado')
        return
      }
      if (rows.length > 1) {
        toast.error('Se encontró más de una emergencia con el código SINPAD indicado')
        return
      }

      setCodigoSinpad('')
      setError('')
      onEncontrada(rows[0])
    } catch (requestError) {
      toast.error(getErrorMessage(requestError, 'No se pudo obtener la búsqueda de emergencias'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-codigo-sinpad-formulario-2a"
        className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 id="titulo-codigo-sinpad-formulario-2a" className="text-lg font-semibold text-[#1e3064]">
            Agregar formulario 2A
          </h2>
          <button
            type="button"
            onClick={handleClose}
            disabled={loading}
            aria-label="Cerrar"
            className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-4 space-y-4">
          <div>
            <label htmlFor="codigo-sinpad-formulario-2a" className={labelClassName}>
              Código SINPAD
            </label>
            <input
              id="codigo-sinpad-formulario-2a"
              type="text"
              value={codigoSinpad}
              onChange={(event) => {
                setCodigoSinpad(event.target.value)
                if (error) setError('')
              }}
              maxLength={30}
              disabled={loading}
              autoFocus
              className={inputClassName}
            />
            {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] transition-colors disabled:opacity-50"
            >
              {loading ? 'Buscando...' : 'Continuar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
