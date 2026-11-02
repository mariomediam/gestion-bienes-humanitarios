import { useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import DistritoSelect from '@components/DistritoSelect'
import { completarArchivo } from '@features/formularios2a/completarCargaFormularios2A'
import EvaluadorSelect from '@features/formularios2a/components/EvaluadorSelect'
import Formulario2ACargaPreview from '@features/formularios2a/components/Formulario2ACargaPreview'

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

const buttonClassName =
  'inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50'

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

function mapaFilas(rows, idKey) {
  const mapa = new Map()
  if (!Array.isArray(rows)) return mapa
  rows.forEach((row) => {
    mapa.set(row[idKey], row)
  })
  return mapa
}

async function cargarCatalogos() {
  const pedidos = [
    ['tiposUso', 'tipo_uso_instalacion_id', sgbhApi.getTiposUsoInstalacion()],
    ['condicionesVivienda', 'condicion_vivienda_id', sgbhApi.getCondicionesVivienda()],
    ['materialesTecho', 'material_techo_id', sgbhApi.getMaterialesTecho()],
    ['materialesPared', 'material_pared_id', sgbhApi.getMaterialesPared()],
    ['materialesPiso', 'material_piso_id', sgbhApi.getMaterialesPiso()],
    ['roles', 'rol_familiar_id', sgbhApi.getRolesFamiliares()],
    ['condicionesPersona', 'condicion_persona_id', sgbhApi.getCondicionesPersona()],
    ['tiposDanio', 'tipo_danio_personal_id', sgbhApi.getTiposDanioPersonal()],
    ['gradosLesion', 'grado_lesion_id', sgbhApi.getGradosLesion()],
    ['tiposDiscapacidad', 'tipo_discapacidad_id', sgbhApi.getTiposDiscapacidad()],
    ['enfermedades', 'enfermedad_cronica_id', sgbhApi.getEnfermedadesCronicas()],
    ['tiposDocumento', 'tipo_documento_id', sgbhApi.getTiposDocumento()],
    ['tiposMedioVida', 'tipo_medio_vida_id', sgbhApi.getTiposMediosVida()],
    ['categoriasMedioVida', 'categoria_medio_vida_id', sgbhApi.getCategoriasMediosVida()],
  ]
  const resultados = await Promise.allSettled(pedidos.map((pedido) => pedido[2]))
  const catalogos = {}
  let error = null
  resultados.forEach((resultado, indice) => {
    const [clave, idKey] = pedidos[indice]
    if (resultado.status === 'fulfilled') {
      catalogos[clave] = mapaFilas(resultado.value, idKey)
      return
    }
    catalogos[clave] = new Map()
    if (!error) error = resultado.reason
  })
  if (error) {
    toast.error(getErrorMessage(error, 'No se pudo obtener la información de los catálogos'))
  }
  return catalogos
}

export default function Formularios2ACargaPage() {
  const navigate = useNavigate()
  const archivoInputRef = useRef(null)
  const [archivo, setArchivo] = useState(null)
  const [datos, setDatos] = useState(null)
  const [catalogos, setCatalogos] = useState(null)
  const [leyendo, setLeyendo] = useState(false)
  const [codigoSinpad, setCodigoSinpad] = useState('')
  const [distrito, setDistrito] = useState(null)
  const [evaluador, setEvaluador] = useState(null)
  const [errores, setErrores] = useState({})
  const [cargando, setCargando] = useState(false)

  function limpiarError(campo) {
    if (!errores[campo]) return
    setErrores((prev) => ({ ...prev, [campo]: undefined }))
  }

  async function handleArchivo(event) {
    const seleccionado = event.target.files?.[0] ?? null
    event.target.value = ''
    if (!seleccionado) return

    setLeyendo(true)
    try {
      let leido
      try {
        const texto = (await seleccionado.text()).replace(/^\uFEFF/, '')
        leido = JSON.parse(texto)
      } catch {
        toast.error('El archivo no contiene un JSON válido')
        return
      }
      if (!leido || typeof leido !== 'object' || Array.isArray(leido)) {
        toast.error('El archivo JSON no tiene el formato esperado')
        return
      }
      if (!Array.isArray(leido.formularios) || leido.formularios.length === 0) {
        toast.error('El archivo no contiene formularios')
        return
      }

      const catalogosLeidos = await cargarCatalogos()
      setArchivo(seleccionado)
      setDatos(leido)
      setCatalogos(catalogosLeidos)
      setErrores({})
    } finally {
      setLeyendo(false)
    }
  }

  function validar() {
    const nextErrors = {}
    if (!codigoSinpad.trim()) {
      nextErrors.codigoSinpad = 'El código SINPAD es obligatorio'
    }
    if (!distrito) {
      nextErrors.distrito = 'El distrito es obligatorio'
    }
    if (!evaluador) {
      nextErrors.evaluador = 'El evaluador es obligatorio'
    }
    return nextErrors
  }

  async function handleCargar(event) {
    event.preventDefault()
    if (cargando || !datos || !archivo) return

    const nextErrors = validar()
    setErrores(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    setCargando(true)
    try {
      const rows = await sgbhApi.buscarEmergencias({ codigo_sinpad: codigoSinpad.trim() })
      if (!Array.isArray(rows) || rows.length === 0 || !rows[0]?.emergencia_id) {
        toast.error('No se encontró una emergencia con el código SINPAD indicado')
        return
      }
      if (rows.length > 1) {
        toast.error('Se encontró más de una emergencia con el código SINPAD indicado')
        return
      }

      const completado = completarArchivo(datos, {
        emergenciaId: rows[0].emergencia_id,
        distrito,
        evaluadorId: evaluador.value,
      })
      const archivoCompletado = new File(
        [JSON.stringify(completado)],
        archivo.name,
        { type: 'application/json' },
      )
      const resultado = await sgbhApi.cargarFormularios2A(archivoCompletado)
      toast.success(mensajeExito(resultado.formularios || []))
      navigate('/formularios-2A')
    } catch (error) {
      console.error(error)
      toast.error(getErrorMessage(error, 'No se pudieron cargar los formularios EDAN 2A'))
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="space-y-6">
      <Link
        to="/formularios-2A"
        className="inline-flex text-sm font-medium text-[#1e3064] hover:underline focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 rounded-sm"
      >
        Volver al listado
      </Link>

      <div>
        <h1 className="text-2xl font-bold text-[#1e3064]">Cargar archivo JSON</h1>
        <p className="mt-1 text-sm text-gray-600">
          {archivo ? archivo.name : 'Seleccione el archivo JSON generado por el sistema móvil'}
        </p>
      </div>

      <div>
        <input
          ref={archivoInputRef}
          id="archivo-carga-formularios-2a"
          type="file"
          accept=".json,application/json"
          className="sr-only"
          disabled={leyendo || cargando}
          onChange={handleArchivo}
        />
        <button
          type="button"
          className={buttonClassName}
          disabled={leyendo || cargando}
          onClick={() => archivoInputRef.current?.click()}
        >
          {leyendo ? 'Cargando...' : 'Seleccionar archivo JSON'}
        </button>
      </div>

      {datos && catalogos && (
        <form onSubmit={handleCargar} className="space-y-6">
          {datos.formularios.map((formulario, indice) => (
            <Formulario2ACargaPreview
              key={`formulario-${indice}`}
              formulario={formulario}
              indice={indice}
              catalogos={catalogos}
            />
          ))}

          <section className="bg-white rounded-lg border border-gray-200 px-5 py-4 space-y-4">
            <div>
              <label htmlFor="codigo-sinpad-carga-formularios-2a" className={labelClassName}>
                Código SINPAD
              </label>
              <input
                id="codigo-sinpad-carga-formularios-2a"
                type="text"
                value={codigoSinpad}
                maxLength={30}
                disabled={cargando}
                onChange={(event) => {
                  setCodigoSinpad(event.target.value)
                  limpiarError('codigoSinpad')
                }}
                className={inputClassName}
              />
              {errores.codigoSinpad && (
                <p className="mt-1 text-xs text-red-600">{errores.codigoSinpad}</p>
              )}
            </div>
            <div>
              <label htmlFor="distrito-carga-formularios-2a" className={labelClassName}>
                Distrito
              </label>
              <DistritoSelect
                inputId="distrito-carga-formularios-2a"
                value={distrito}
                disabled={cargando}
                onChange={(option) => {
                  setDistrito(option)
                  limpiarError('distrito')
                }}
              />
              {errores.distrito && (
                <p className="mt-1 text-xs text-red-600">{errores.distrito}</p>
              )}
            </div>
            <div>
              <label htmlFor="evaluador-carga-formularios-2a" className={labelClassName}>
                Evaluador
              </label>
              <EvaluadorSelect
                inputId="evaluador-carga-formularios-2a"
                value={evaluador}
                disabled={cargando}
                onChange={(option) => {
                  setEvaluador(option)
                  limpiarError('evaluador')
                }}
              />
              {errores.evaluador && (
                <p className="mt-1 text-xs text-red-600">{errores.evaluador}</p>
              )}
            </div>
            <div className="flex justify-end">
              <button type="submit" className={buttonClassName} disabled={cargando}>
                {cargando ? 'Cargando...' : 'Cargar'}
              </button>
            </div>
          </section>
        </form>
      )}
    </div>
  )
}
