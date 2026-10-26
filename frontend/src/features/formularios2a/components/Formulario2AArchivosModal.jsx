import { useCallback, useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import DownloadIcon from '@components/icons/DownloadIcon'
import TrashIcon from '@components/icons/TrashIcon'
import { sgbhApi } from '@api/sgbhApi'
import Formulario2AArchivoEliminarModal from '@features/formularios2a/components/Formulario2AArchivoEliminarModal'

const actionButtonClassName =
  'group relative inline-flex items-center justify-center w-8 h-8 text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50'

const deleteButtonClassName =
  'group relative inline-flex items-center justify-center w-8 h-8 text-red-600 bg-white border border-gray-300 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 transition-colors disabled:opacity-50'

const actionTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-[#1e3064] px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

const deleteTooltipClassName =
  'pointer-events-none absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-red-600 px-2 py-1 text-xs font-medium text-white opacity-0 transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function formatTamano(bytes) {
  const value = Number(bytes)
  if (!Number.isFinite(value) || value < 0) return ''
  if (value < 1024) return `${value.toLocaleString('es-PE')} B`
  if (value < 1024 * 1024) {
    return `${(value / 1024).toLocaleString('es-PE', { maximumFractionDigits: 1 })} KB`
  }
  return `${(value / (1024 * 1024)).toLocaleString('es-PE', { maximumFractionDigits: 1 })} MB`
}

export default function Formulario2AArchivosModal({ isOpen, formulario, onClose }) {
  const [archivos, setArchivos] = useState([])
  const [cargando, setCargando] = useState(false)
  const [subiendo, setSubiendo] = useState(false)
  const [progreso, setProgreso] = useState(null)
  const [archivoEnCurso, setArchivoEnCurso] = useState(null)
  const [archivoAEliminar, setArchivoAEliminar] = useState(null)
  const [descargandoId, setDescargandoId] = useState(null)
  const [arrastrando, setArrastrando] = useState(false)
  const abortRef = useRef(null)
  const cargaSeq = useRef(0)
  const estuvoAbierto = useRef(false)
  const [listaDe, setListaDe] = useState(null)
  const formulario2aId = formulario?.formulario_2a_id
  const listaActual = isOpen ? formulario2aId ?? null : null

  if (listaActual !== listaDe) {
    setListaDe(listaActual)
    if (listaActual) {
      setCargando(true)
      setArchivos([])
    }
  }

  const cargar = useCallback(async () => {
    if (!formulario2aId) return

    const seq = cargaSeq.current + 1
    cargaSeq.current = seq
    setCargando(true)
    try {
      const rows = await sgbhApi.buscarArchivosFormulario2A({
        formulario_2a_id: formulario2aId,
        esta_activo: true,
      })
      if (cargaSeq.current !== seq) return
      setArchivos(Array.isArray(rows) ? rows : [])
    } catch (error) {
      if (cargaSeq.current !== seq) return
      console.error(error)
      toast.error(
        getErrorMessage(
          error,
          'No se pudo obtener la búsqueda de archivos del formulario EDAN 2A',
        ),
      )
    } finally {
      if (cargaSeq.current === seq) setCargando(false)
    }
  }, [formulario2aId])

  useEffect(() => {
    if (!isOpen) return undefined
    cargar()
    return undefined
  }, [isOpen, cargar])

  useEffect(() => {
    if (isOpen) {
      estuvoAbierto.current = true
      return undefined
    }
    if (!estuvoAbierto.current) return undefined

    estuvoAbierto.current = false
    cargaSeq.current += 1
    abortRef.current?.abort()
    abortRef.current = null
    setArchivos([])
    setCargando(false)
    setSubiendo(false)
    setProgreso(null)
    setArchivoEnCurso(null)
    setArchivoAEliminar(null)
    setDescargandoId(null)
    setArrastrando(false)
    return undefined
  }, [isOpen])

  useEffect(() => {
    if (!isOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !subiendo && archivoAEliminar === null) {
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, subiendo, archivoAEliminar, onClose])

  if (!isOpen || !formulario) return null

  function handleClose() {
    if (subiendo || archivoAEliminar) return
    onClose()
  }

  async function subir(archivo) {
    if (subiendo || !formulario2aId) return
    if (!archivo || archivo.size < 1) {
      toast.error('El archivo está vacío')
      return
    }

    const controller = new AbortController()
    abortRef.current = controller
    setSubiendo(true)
    setArchivoEnCurso({ nombre: archivo.name, tamano: archivo.size })
    setProgreso(0)

    try {
      await sgbhApi.crearArchivoFormulario2A(formulario2aId, archivo, {
        signal: controller.signal,
        onUploadProgress: (event) => {
          if (!event.total) return
          setProgreso(Math.min(100, Math.round((event.loaded * 100) / event.total)))
        },
      })
      toast.success('Archivo registrado correctamente')
      await cargar()
    } catch (error) {
      if (error?.code === 'ERR_CANCELED') return
      console.error(error)
      toast.error(
        getErrorMessage(error, 'No se pudo registrar el archivo del formulario EDAN 2A'),
      )
    } finally {
      if (abortRef.current === controller) abortRef.current = null
      setSubiendo(false)
      setArchivoEnCurso(null)
      setProgreso(null)
    }
  }

  function handleArchivosSeleccionados(fileList) {
    const files = Array.from(fileList || [])
    if (files.length === 0) return
    if (files.length > 1) {
      toast.error('Solo se puede subir un archivo por solicitud')
      return
    }
    subir(files[0])
  }

  async function handleDescargar(archivo) {
    if (descargandoId) return

    setDescargandoId(archivo.archivo_id)
    try {
      await sgbhApi.descargarArchivoFormulario2A(
        formulario2aId,
        archivo.archivo_id,
        archivo.nombre_original,
      )
    } catch (error) {
      console.error(error)
      toast.error(
        getErrorMessage(error, 'No se pudo descargar el archivo del formulario EDAN 2A'),
      )
    } finally {
      setDescargandoId(null)
    }
  }

  const zonaClassName = arrastrando
    ? 'border-[#1e3064] bg-gray-50'
    : 'border-gray-300 bg-white'

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div className="absolute inset-0 bg-black/50" onClick={handleClose} />

        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="titulo-archivos-formulario-2a"
          className="relative bg-white rounded-lg shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-x-hidden overflow-y-auto"
        >
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <div>
              <h2 id="titulo-archivos-formulario-2a" className="text-lg font-semibold text-[#1e3064]">
                Archivos adjuntos
              </h2>
              <p className="mt-1 text-sm text-gray-600">
                {formulario.codigo_sinpad
                  ? `Formulario EDAN 2A con código SINPAD ${formulario.codigo_sinpad}`
                  : 'Formulario EDAN 2A'}
              </p>
            </div>
            <button
              type="button"
              onClick={handleClose}
              disabled={subiendo}
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
            <div>
              <p className="text-sm font-medium text-[#1e3064] mb-2">Subir archivo</p>
              <label
                htmlFor="archivo-formulario-2a"
                onDragEnter={(event) => {
                  event.preventDefault()
                  if (!subiendo) setArrastrando(true)
                }}
                onDragOver={(event) => event.preventDefault()}
                onDragLeave={(event) => {
                  event.preventDefault()
                  if (event.currentTarget.contains(event.relatedTarget)) return
                  setArrastrando(false)
                }}
                onDrop={(event) => {
                  event.preventDefault()
                  setArrastrando(false)
                  if (subiendo) return
                  handleArchivosSeleccionados(event.dataTransfer.files)
                }}
                className={`flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed px-4 py-8 text-center focus-within:ring-2 focus-within:ring-[#1e3064] ${zonaClassName} ${subiendo ? 'pointer-events-none opacity-60' : ''}`}
              >
                <input
                  id="archivo-formulario-2a"
                  type="file"
                  autoFocus
                  disabled={subiendo}
                  className="sr-only"
                  onChange={(event) => {
                    handleArchivosSeleccionados(event.target.files)
                    event.target.value = ''
                  }}
                />
                <svg xmlns="http://www.w3.org/2000/svg" className="mb-2 h-8 w-8 text-[#1e3064]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M12 16V4" />
                  <path d="m7 9 5-5 5 5" />
                  <path d="M4 20h16" />
                </svg>
                <span className="text-sm font-medium text-gray-800">
                  Haga clic para subir o arrastre el archivo
                </span>
                <span className="mt-1 text-xs text-gray-500">Seleccione un archivo</span>
              </label>
            </div>

            {archivoEnCurso && (
              <div className="rounded-md border border-gray-200 px-3 py-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-gray-800">{archivoEnCurso.nombre}</p>
                    <p className="text-xs text-gray-500">
                      {formatTamano(archivoEnCurso.tamano)}
                      {' · '}
                      Subiendo...
                      {progreso !== null ? ` ${progreso}%` : ''}
                    </p>
                  </div>
                </div>
                <div
                  role="progressbar"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={progreso ?? 0}
                  aria-label="Progreso de la carga"
                  className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-gray-200"
                >
                  <div
                    className="h-1.5 rounded-full bg-[#1e3064]"
                    style={{ width: `${progreso ?? 0}%` }}
                  />
                </div>
              </div>
            )}

            <div className="border-t border-gray-200 pt-4">
              <h3 className="text-sm font-medium text-[#1e3064] mb-3">Archivos subidos</h3>
              {cargando ? (
                <p className="text-sm text-gray-600">Cargando...</p>
              ) : archivos.length === 0 ? (
                <p className="text-sm text-gray-500">No hay archivos adjuntos</p>
              ) : (
                <ul className="max-h-64 space-y-2 overflow-x-hidden overflow-y-auto">
                  {archivos.map((archivo) => {
                    const tamano = formatTamano(archivo.tamano_bytes)
                    const descargando = descargandoId === archivo.archivo_id

                    return (
                      <li
                        key={archivo.archivo_id}
                        className="flex items-center justify-between gap-3 rounded-md border border-gray-200 px-3 py-2"
                      >
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium text-gray-800">
                            {archivo.nombre_original}
                          </p>
                          {tamano && <p className="text-xs text-gray-500">{tamano}</p>}
                        </div>
                        <div className="flex shrink-0 gap-2">
                          <button
                            type="button"
                            aria-label={descargando ? 'Descargando' : 'Descargar'}
                            disabled={Boolean(descargandoId)}
                            onClick={() => handleDescargar(archivo)}
                            className={actionButtonClassName}
                          >
                            <DownloadIcon className="w-4 h-4" />
                            <span className={actionTooltipClassName} aria-hidden="true">
                              {descargando ? 'Descargando...' : 'Descargar'}
                            </span>
                          </button>
                          <button
                            type="button"
                            aria-label="Eliminar"
                            disabled={subiendo}
                            onClick={() => setArchivoAEliminar(archivo)}
                            className={deleteButtonClassName}
                          >
                            <TrashIcon className="w-4 h-4" />
                            <span className={deleteTooltipClassName} aria-hidden="true">
                              Eliminar
                            </span>
                          </button>
                        </div>
                      </li>
                    )
                  })}
                </ul>
              )}
            </div>
          </div>
        </div>
      </div>

      <Formulario2AArchivoEliminarModal
        isOpen={archivoAEliminar !== null}
        formulario2aId={formulario2aId}
        archivo={archivoAEliminar}
        onClose={() => setArchivoAEliminar(null)}
        onEliminado={(archivoId) => {
          setArchivos((prev) => prev.filter((item) => item.archivo_id !== archivoId))
        }}
      />
    </>
  )
}
