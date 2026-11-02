import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function mensajeExito(formularios) {
  const cantidad = formularios.length
  if (cantidad === 1) {
    return `Se cargó el formulario EDAN 2A ${formularios[0].formulario_2a_id}`
  }
  const ids = formularios.map((formulario) => formulario.formulario_2a_id).join(', ')
  return `Se cargaron ${cantidad} formularios EDAN 2A: ${ids}`
}

export default function Formulario2ACargaModal({ isOpen, onClose }) {
  const [archivo, setArchivo] = useState(null)
  const [cargando, setCargando] = useState(false)

  useEffect(() => {
    if (!isOpen) {
      setArchivo(null)
      return undefined
    }

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !cargando) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, cargando, onClose])

  if (!isOpen) return null

  function handleClose() {
    if (cargando) return
    onClose()
  }

  async function handleConfirmar() {
    if (cargando || !archivo) return

    setCargando(true)
    try {
      const resultado = await sgbhApi.cargarFormularios2A(archivo)
      toast.success(mensajeExito(resultado.formularios || []))
      onClose()
    } catch (error) {
      console.error(error)
      toast.error(getErrorMessage(error, 'No se pudieron cargar los formularios EDAN 2A'))
    } finally {
      setCargando(false)
    }
  }

  return createPortal(
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-cargar-formularios-2a"
        className="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4"
      >
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 id="titulo-cargar-formularios-2a" className="text-lg font-semibold text-[#1e3064]">
            Cargar archivo JSON
          </h2>
        </div>
        <div className="px-6 py-4">
          <p className="text-sm text-gray-700">
            Seleccione el archivo JSON generado por el sistema móvil. Si la carga
            falla, no se guarda ningún formulario del archivo.
          </p>
          <label htmlFor="archivo-carga-formularios-2a" className="mt-4 block text-sm font-medium text-gray-700">
            Archivo JSON
          </label>
          <input
            id="archivo-carga-formularios-2a"
            type="file"
            accept=".json,application/json"
            disabled={cargando}
            onChange={(event) => setArchivo(event.target.files?.[0] ?? null)}
            className="mt-1 block w-full text-sm text-gray-700 file:mr-3 file:rounded-md file:border-0 file:bg-[#1e3064] file:px-3 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-[#2a4080] disabled:opacity-50"
          />
        </div>
        <div className="flex justify-end gap-3 px-6 py-4">
          <button
            type="button"
            onClick={handleClose}
            disabled={cargando}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleConfirmar}
            disabled={cargando || !archivo}
            className="px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] transition-colors disabled:opacity-50"
          >
            {cargando ? 'Cargando...' : 'Cargar'}
          </button>
        </div>
      </div>
    </div>,
    document.body,
  )
}
