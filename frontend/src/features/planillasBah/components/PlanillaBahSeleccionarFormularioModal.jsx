import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import { textoVisible } from '@features/planillasBah/formato'

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

export const MENSAJE_FORMULARIO_CON_PLANILLA =
  'El formulario EDAN 2A ya tiene registrada una planilla BAH'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function textoUbicacionVivienda(vivienda) {
  const partes = [vivienda.distrito_nombre, vivienda.barrio_sector_urbanizacion].filter(
    (parte) => parte !== null && parte !== undefined && String(parte).trim() !== '',
  )

  if (partes.length === 0) {
    return '—'
  }

  return partes.join(' - ')
}

export default function PlanillaBahSeleccionarFormularioModal({
  isOpen,
  onClose,
  onSeleccionado,
}) {
  const [codigoSinpad, setCodigoSinpad] = useState('')
  const [error, setError] = useState('')
  const [buscando, setBuscando] = useState(false)
  const [buscado, setBuscado] = useState(false)
  const [viviendas, setViviendas] = useState([])
  const [seleccionandoId, setSeleccionandoId] = useState(null)

  const ocupado = buscando || seleccionandoId !== null
  const abiertoAntes = useRef(false)

  useEffect(() => {
    if (abiertoAntes.current && !isOpen) {
      setCodigoSinpad('')
      setError('')
      setBuscando(false)
      setBuscado(false)
      setViviendas([])
      setSeleccionandoId(null)
    }
    abiertoAntes.current = isOpen
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !ocupado) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, ocupado, onClose])

  if (!isOpen) return null

  function handleClose() {
    if (ocupado) return
    onClose()
  }

  async function handleBuscar(event) {
    event.preventDefault()
    const codigo = codigoSinpad.trim()
    if (!codigo) {
      setError('El código SINPAD es obligatorio')
      return
    }

    setBuscando(true)
    setBuscado(false)
    try {
      const rows = await sgbhApi.buscarViviendas({ codigo_sinpad: codigo })
      setViviendas(Array.isArray(rows) ? rows : [])
      setBuscado(true)
    } catch (requestError) {
      toast.error(getErrorMessage(requestError, 'No se pudo obtener la búsqueda de viviendas'))
    } finally {
      setBuscando(false)
    }
  }

  async function handleSeleccionar(vivienda) {
    if (ocupado) return

    setSeleccionandoId(vivienda.vivienda_id)
    try {
      const data = await sgbhApi.formulario2ATienePlanillaBah(vivienda.formulario_2a_id)
      if (data?.tiene_planilla_bah) {
        toast.error(MENSAJE_FORMULARIO_CON_PLANILLA)
        return
      }
      onSeleccionado(vivienda)
    } catch (requestError) {
      toast.error(
        getErrorMessage(
          requestError,
          'No se pudo consultar si el formulario EDAN 2A tiene planilla BAH',
        ),
      )
    } finally {
      setSeleccionandoId(null)
    }
  }

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-seleccionar-formulario-planilla"
        className="relative bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] flex flex-col"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2
            id="titulo-seleccionar-formulario-planilla"
            className="text-lg font-semibold text-[#1e3064]"
          >
            Seleccionar formulario 2A
          </h2>
          <button
            type="button"
            onClick={handleClose}
            disabled={ocupado}
            aria-label="Cerrar"
            className="text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleBuscar} className="px-6 py-4 space-y-4 overflow-y-auto">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="flex-1">
              <label htmlFor="codigo-sinpad-planilla-bah" className={labelClassName}>
                Código SINPAD
              </label>
              <input
                id="codigo-sinpad-planilla-bah"
                type="text"
                value={codigoSinpad}
                onChange={(event) => {
                  setCodigoSinpad(event.target.value)
                  if (error) setError('')
                }}
                maxLength={30}
                disabled={ocupado}
                autoFocus
                className={inputClassName}
              />
              {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
            </div>
            <button
              type="submit"
              disabled={ocupado}
              className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50"
            >
              {buscando ? 'Buscando...' : 'Buscar'}
            </button>
          </div>

          {buscado && (
            <div className="overflow-x-auto border border-gray-200 rounded-md">
              <table className="min-w-full text-sm text-left">
                <thead className="bg-gray-50 text-gray-500">
                  <tr>
                    <th scope="col" className="px-4 py-3 font-medium">Código SINPAD</th>
                    <th scope="col" className="px-4 py-3 font-medium">Ubicación</th>
                    <th scope="col" className="px-4 py-3 font-medium">Lote</th>
                    <th scope="col" className="px-4 py-3 font-medium">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {viviendas.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-4 py-6 text-center text-gray-500">
                        No se encontraron viviendas
                      </td>
                    </tr>
                  ) : (
                    viviendas.map((vivienda) => {
                      const seleccionando = seleccionandoId === vivienda.vivienda_id
                      return (
                        <tr key={vivienda.vivienda_id} className="border-t border-gray-100">
                          <td className="px-4 py-3 text-gray-800 whitespace-nowrap">
                            {textoVisible(vivienda.codigo_sinpad)}
                          </td>
                          <td className="px-4 py-3 text-gray-800">
                            {textoUbicacionVivienda(vivienda)}
                          </td>
                          <td className="px-4 py-3 text-gray-800 whitespace-nowrap">
                            {textoVisible(vivienda.numero_lote)}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <button
                              type="button"
                              onClick={() => handleSeleccionar(vivienda)}
                              disabled={ocupado}
                              className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                              {seleccionando ? 'Verificando...' : 'Seleccionar'}
                            </button>
                          </td>
                        </tr>
                      )
                    })
                  )}
                </tbody>
              </table>
            </div>
          )}
        </form>
      </div>
    </div>,
    document.body,
  )
}
