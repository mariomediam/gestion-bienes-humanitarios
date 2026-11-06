import { useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import DevolucionOrigenBusquedaForm from '@features/devoluciones/components/DevolucionOrigenBusquedaForm'
import DevolucionOrigenResultados from '@features/devoluciones/components/DevolucionOrigenResultados'
import {
  FILTROS_MOVIMIENTO_ORIGEN,
  buildMovimientoOrigenSearchParams,
} from '@features/devoluciones/movimientoOrigenSearchParams'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function DevolucionOrigenModal({
  isOpen,
  movimientoSeleccionadoId,
  onClose,
  onSeleccionar,
}) {
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [movimientos, setMovimientos] = useState([])
  const [filtros, setFiltros] = useState(FILTROS_MOVIMIENTO_ORIGEN)
  const busquedaRef = useRef(0)

  useEffect(() => {
    if (!isOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !loading) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, loading, onClose])

  useEffect(() => {
    if (!isOpen) return

    busquedaRef.current += 1
    setFiltros(FILTROS_MOVIMIENTO_ORIGEN)
    setMovimientos([])
    setSearched(false)
    setLoading(false)
  }, [isOpen])

  if (!isOpen) return null

  function handleClose() {
    if (loading) return
    busquedaRef.current += 1
    onClose()
  }

  function handleFiltroChange(name, value) {
    setFiltros((current) => ({ ...current, [name]: value }))
  }

  function handleLimpiar() {
    setFiltros(FILTROS_MOVIMIENTO_ORIGEN)
    setMovimientos([])
    setSearched(false)
  }

  async function handleBuscar(event) {
    event.preventDefault()
    const busquedaId = busquedaRef.current + 1
    busquedaRef.current = busquedaId
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarMovimientos(buildMovimientoOrigenSearchParams(filtros))
      if (busquedaRef.current !== busquedaId) return
      setMovimientos(rows)
      setSearched(true)
    } catch (error) {
      if (busquedaRef.current !== busquedaId) return
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de movimientos de almacén'))
    } finally {
      if (busquedaRef.current === busquedaId) {
        setLoading(false)
      }
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-buscar-movimiento-origen"
        className="relative bg-white rounded-lg shadow-xl w-full max-w-5xl mx-4 max-h-[90vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 id="titulo-buscar-movimiento-origen" className="text-lg font-semibold text-[#1e3064]">
            Buscar movimiento origen
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

        <div className="px-6 py-4 space-y-4">
          <DevolucionOrigenBusquedaForm
            filtros={filtros}
            onFiltroChange={handleFiltroChange}
            onSubmit={handleBuscar}
            onLimpiar={handleLimpiar}
            loading={loading}
          />

          {searched && (
            <DevolucionOrigenResultados
              movimientos={movimientos}
              movimientoSeleccionadoId={movimientoSeleccionadoId}
              onSeleccionar={onSeleccionar}
            />
          )}
        </div>
      </div>
    </div>
  )
}
