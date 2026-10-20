import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import EncargadoAlmacenSelect from '@features/movimientos/components/EncargadoAlmacenSelect'
import MovimientoDetalleFilas from '@features/movimientos/components/MovimientoDetalleFilas'
import IntegranteReceptorSelect from '@features/planillasBah/components/IntegranteReceptorSelect'
import { MENSAJE_FORMULARIO_CON_PLANILLA } from '@features/planillasBah/components/PlanillaBahSeleccionarFormularioModal'

const ALMACEN_CENTRAL_ID = 1
const ESTADO_MOVIMIENTO_CONFIRMADO_ID = 2
const TIPO_MOVIMIENTO_ENTREGA_BAH_ID = 7
const ESTADO_PLANILLA_EMITIDA_ID = 2
const INT_MIN = -2147483648
const INT_MAX = 2147483647

const EMPTY_FORM = {
  fecha_movimiento: '',
  documento_referencia: '',
  fecha_documento: '',
  destinatario: '',
  observacion: '',
  encargado: null,
  numero_planilla: '',
  anio_planilla: '',
  integrante_receptor_id: '',
  fecha_entrega: '',
  planilla_observacion: '',
}

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function textoOpcional(value) {
  const texto = value.trim()
  return texto || null
}

function fechaHoraApi(value) {
  if (!value) return null
  return value.length === 16 ? `${value}:00` : value
}

function idFormulario(raw) {
  if (!/^\d+$/.test(String(raw || ''))) return null
  const value = Number(raw)
  if (!Number.isInteger(value) || value < 1 || value > INT_MAX) return null
  return value
}

function normalizarCantidad(raw) {
  return String(raw ?? '').trim().replace(',', '.')
}

function validarCantidad(raw, naturaleza) {
  const texto = normalizarCantidad(raw)
  if (!texto) return 'La cantidad es obligatoria'
  if (!/^-?\d+(\.\d+)?$/.test(texto)) {
    return 'La cantidad debe ser un número decimal'
  }

  const sinSigno = texto.startsWith('-') ? texto.slice(1) : texto
  const [entera, decimal = ''] = sinSigno.split('.')
  if (entera.length > 12 || decimal.length > 6) {
    return 'La cantidad debe tener como máximo 18 dígitos y 6 decimales'
  }

  if (Number(texto) === 0) return 'La cantidad debe ser distinta de cero'
  if (naturaleza !== 'M' && texto.startsWith('-')) {
    return 'La cantidad debe ingresarse en positivo'
  }
  return ''
}

function cantidadParaApi(raw, naturaleza) {
  const texto = normalizarCantidad(raw)
  if (naturaleza === 'S') return `-${texto}`
  return texto
}

function leerEntero(raw, etiqueta, { obligatorio }) {
  const texto = String(raw ?? '').trim()
  if (!texto) {
    return {
      value: null,
      error: obligatorio ? `El ${etiqueta} es obligatorio` : '',
    }
  }
  if (!/^-?\d+$/.test(texto)) {
    return { value: null, error: `El ${etiqueta} debe ser un número entero` }
  }
  const value = Number(texto)
  if (!Number.isSafeInteger(value) || value < INT_MIN || value > INT_MAX) {
    return { value: null, error: `El ${etiqueta} debe ser un número entero` }
  }
  return { value, error: '' }
}

function validarFormulario(form, lineas, naturaleza) {
  const errores = {}

  if (!form.fecha_movimiento) {
    errores.fecha_movimiento = 'La fecha de movimiento es obligatoria'
  }
  if (form.documento_referencia.trim().length > 100) {
    errores.documento_referencia = 'El documento de referencia no debe superar 100 caracteres'
  }
  if (form.destinatario.trim().length > 250) {
    errores.destinatario = 'El destinatario no debe superar 250 caracteres'
  }
  if (form.observacion.trim().length > 1000) {
    errores.observacion = 'La observación no debe superar 1000 caracteres'
  }
  if (!form.encargado) {
    errores.encargado = 'El encargado de almacén es obligatorio'
  }

  const numero = leerEntero(form.numero_planilla, 'número de planilla', { obligatorio: false })
  if (numero.error) errores.numero_planilla = numero.error

  const anio = leerEntero(form.anio_planilla, 'año de planilla', { obligatorio: true })
  if (anio.error) errores.anio_planilla = anio.error

  if (!form.integrante_receptor_id) {
    errores.integrante_receptor_id = 'El integrante receptor es obligatorio'
  }
  if (!form.fecha_entrega) {
    errores.fecha_entrega = 'La fecha de entrega es obligatoria'
  }
  if (form.planilla_observacion.trim().length > 1000) {
    errores.planilla_observacion = 'La observación no debe superar 1000 caracteres'
  }

  if (lineas.length === 0) {
    errores.detalles = 'Debe registrar al menos un detalle'
  }

  const bienesVistos = new Set()
  lineas.forEach((linea) => {
    const errorLinea = {}
    if (!linea.bien) {
      errorLinea.bien = 'El bien es obligatorio'
    } else if (bienesVistos.has(linea.bien.value)) {
      errorLinea.bien = 'El bien ya está registrado con la misma modalidad de devolución en este movimiento'
    } else {
      bienesVistos.add(linea.bien.value)
    }

    const errorCantidad = validarCantidad(linea.cantidad, naturaleza)
    if (errorCantidad) {
      errorLinea.cantidad = errorCantidad
    }
    if (linea.cantidad_texto.trim().length > 30) {
      errorLinea.cantidad_texto = 'La cantidad textual no debe superar 30 caracteres'
    }
    if (Object.keys(errorLinea).length > 0) {
      errores[linea.key] = errorLinea
    }
  })

  return errores
}

export default function PlanillaBahFormPage() {
  const { formulario2aId } = useParams()
  const navigate = useNavigate()
  const lineaId = useRef(0)
  const [form, setForm] = useState(EMPTY_FORM)
  const [lineas, setLineas] = useState([])
  const [errores, setErrores] = useState({})
  const [naturaleza, setNaturaleza] = useState('')
  const [loading, setLoading] = useState(false)
  const [cargando, setCargando] = useState(true)
  const formularioId = idFormulario(formulario2aId)

  useEffect(() => {
    if (!formularioId) {
      toast.error('El formulario 2A indicado no es válido')
      navigate('/alm-planilla-bah', { replace: true })
      return undefined
    }

    let active = true
    setCargando(true)

    Promise.all([
      sgbhApi.formulario2ATienePlanillaBah(formularioId),
      sgbhApi.getTiposMovimiento(),
    ])
      .then(([planilla, tipos]) => {
        if (!active) return
        if (planilla?.tiene_planilla_bah) {
          toast.error(MENSAJE_FORMULARIO_CON_PLANILLA)
          navigate('/alm-planilla-bah', { replace: true })
          return
        }
        const tipo = (Array.isArray(tipos) ? tipos : []).find(
          (item) => Number(item.tipo_movimiento_id) === TIPO_MOVIMIENTO_ENTREGA_BAH_ID,
        )
        if (!tipo?.naturaleza) {
          toast.error('No se encontró el tipo de movimiento de la planilla BAH')
          navigate('/alm-planilla-bah', { replace: true })
          return
        }
        setNaturaleza(tipo.naturaleza)
        setCargando(false)
      })
      .catch((error) => {
        if (!active) return
        toast.error(getErrorMessage(error, 'No se pudo preparar el registro de la planilla BAH'))
        navigate('/alm-planilla-bah', { replace: true })
      })

    return () => {
      active = false
    }
  }, [formularioId, navigate])

  function crearLinea() {
    lineaId.current += 1
    return {
      key: lineaId.current,
      bien: null,
      cantidad: '',
      cantidad_texto: '',
    }
  }

  function limpiarError(name) {
    setErrores((current) => {
      if (!current[name]) return current
      const next = { ...current }
      delete next[name]
      return next
    })
  }

  function handleChange(name, value) {
    setForm((current) => ({ ...current, [name]: value }))
    limpiarError(name)
  }

  function handleAgregarBien() {
    setLineas((current) => [...current, crearLinea()])
    limpiarError('detalles')
  }

  function handleQuitarBien(key) {
    setLineas((current) => current.filter((linea) => linea.key !== key))
    limpiarError(key)
  }

  function handleCambiarLinea(key, name, value) {
    setLineas((current) =>
      current.map((linea) => (linea.key === key ? { ...linea, [name]: value } : linea)),
    )
    setErrores((current) => {
      const errorLinea = current[key]
      if (!errorLinea?.[name]) return current
      const nextLinea = { ...errorLinea }
      delete nextLinea[name]
      const next = { ...current }
      if (Object.keys(nextLinea).length === 0) {
        delete next[key]
      } else {
        next[key] = nextLinea
      }
      return next
    })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const nextErrores = validarFormulario(form, lineas, naturaleza)
    setErrores(nextErrores)
    if (Object.keys(nextErrores).length > 0) return

    const fechaMovimiento = fechaHoraApi(form.fecha_movimiento)
    const numero = leerEntero(form.numero_planilla, 'número de planilla', { obligatorio: false })
    const anio = leerEntero(form.anio_planilla, 'año de planilla', { obligatorio: true })
    const payload = {
      almacen_id: ALMACEN_CENTRAL_ID,
      tipo_movimiento_id: TIPO_MOVIMIENTO_ENTREGA_BAH_ID,
      estado_movimiento_id: ESTADO_MOVIMIENTO_CONFIRMADO_ID,
      movimiento_origen_id: null,
      fecha_movimiento: fechaMovimiento,
      documento_referencia: textoOpcional(form.documento_referencia),
      fecha_documento: form.fecha_documento || null,
      destinatario: textoOpcional(form.destinatario),
      observacion: textoOpcional(form.observacion),
      fecha_confirmacion: fechaMovimiento,
      encargado_almacen_id: form.encargado.value,
      detalles: lineas.map((linea) => ({
        bien_id: linea.bien.value,
        cantidad: cantidadParaApi(linea.cantidad, naturaleza),
        cantidad_texto: textoOpcional(linea.cantidad_texto),
        es_devolvible: false,
        observacion: '',
      })),
      anio_planilla: anio.value,
      numero_planilla: numero.value,
      integrante_receptor_id: Number(form.integrante_receptor_id),
      fecha_entrega: form.fecha_entrega,
      estado_planilla_id: ESTADO_PLANILLA_EMITIDA_ID,
      planilla_entrega_observacion: textoOpcional(form.planilla_observacion),
      fecha_emision: fechaMovimiento,
    }

    setLoading(true)
    try {
      await sgbhApi.crearPlanillaBah(payload)
      toast.success('Planilla BAH registrada correctamente')
      navigate('/alm-planilla-bah')
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo registrar la planilla BAH'))
    } finally {
      setLoading(false)
    }
  }

  if (cargando) {
    return (
      <div className="space-y-6">
        <Link
          to="/alm-planilla-bah"
          className="inline-flex text-sm font-medium text-[#1e3064] hover:underline focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 rounded-sm"
        >
          Volver al listado
        </Link>
        <p className="text-sm text-gray-600">Cargando...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Link
        to="/alm-planilla-bah"
        className="inline-flex text-sm font-medium text-[#1e3064] hover:underline focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 rounded-sm"
      >
        Volver al listado
      </Link>

      <div>
        <h1 className="text-2xl font-bold text-[#1e3064]">Agregar planilla BAH</h1>
        <p className="mt-1 text-sm text-gray-600">
          Registro de una planilla BAH y sus bienes
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <section className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
          <h2 className="text-lg font-semibold text-[#1e3064]">
            Datos del movimiento de almacén
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="fecha-movimiento-planilla" className={labelClassName}>
                Fecha de movimiento
              </label>
              <input
                id="fecha-movimiento-planilla"
                type="datetime-local"
                value={form.fecha_movimiento}
                onChange={(event) => handleChange('fecha_movimiento', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
              {errores.fecha_movimiento && (
                <p className="mt-1 text-xs text-red-600">{errores.fecha_movimiento}</p>
              )}
            </div>

            <div>
              <label htmlFor="documento-referencia-planilla" className={labelClassName}>
                Documento de referencia
              </label>
              <input
                id="documento-referencia-planilla"
                type="text"
                value={form.documento_referencia}
                onChange={(event) => handleChange('documento_referencia', event.target.value)}
                maxLength={100}
                disabled={loading}
                className={inputClassName}
              />
              {errores.documento_referencia && (
                <p className="mt-1 text-xs text-red-600">{errores.documento_referencia}</p>
              )}
            </div>

            <div>
              <label htmlFor="fecha-documento-planilla" className={labelClassName}>
                Fecha del documento
              </label>
              <input
                id="fecha-documento-planilla"
                type="date"
                value={form.fecha_documento}
                onChange={(event) => handleChange('fecha_documento', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
            </div>

            <div>
              <label htmlFor="destinatario-planilla" className={labelClassName}>
                Destinatario
              </label>
              <input
                id="destinatario-planilla"
                type="text"
                value={form.destinatario}
                onChange={(event) => handleChange('destinatario', event.target.value)}
                maxLength={250}
                disabled={loading}
                className={inputClassName}
              />
              {errores.destinatario && (
                <p className="mt-1 text-xs text-red-600">{errores.destinatario}</p>
              )}
            </div>

            <div>
              <label htmlFor="encargado-almacen-planilla" className={labelClassName}>
                Encargado de almacén
              </label>
              <EncargadoAlmacenSelect
                inputId="encargado-almacen-planilla"
                value={form.encargado}
                onChange={(encargado) => handleChange('encargado', encargado)}
                disabled={loading}
              />
              {errores.encargado && (
                <p className="mt-1 text-xs text-red-600">{errores.encargado}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label htmlFor="observacion-movimiento-planilla" className={labelClassName}>
                Observaciones
              </label>
              <textarea
                id="observacion-movimiento-planilla"
                value={form.observacion}
                onChange={(event) => handleChange('observacion', event.target.value)}
                maxLength={1000}
                rows={3}
                disabled={loading}
                className={inputClassName}
              />
              {errores.observacion && (
                <p className="mt-1 text-xs text-red-600">{errores.observacion}</p>
              )}
            </div>
          </div>
        </section>

        <section className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
          <h2 className="text-lg font-semibold text-[#1e3064]">Datos de la planilla de BAH</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="numero-planilla" className={labelClassName}>
                Número de planilla
              </label>
              <input
                id="numero-planilla"
                type="text"
                inputMode="numeric"
                value={form.numero_planilla}
                onChange={(event) => handleChange('numero_planilla', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
              {errores.numero_planilla && (
                <p className="mt-1 text-xs text-red-600">{errores.numero_planilla}</p>
              )}
            </div>

            <div>
              <label htmlFor="anio-planilla" className={labelClassName}>
                Año de planilla
              </label>
              <input
                id="anio-planilla"
                type="text"
                inputMode="numeric"
                value={form.anio_planilla}
                onChange={(event) => handleChange('anio_planilla', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
              {errores.anio_planilla && (
                <p className="mt-1 text-xs text-red-600">{errores.anio_planilla}</p>
              )}
            </div>

            <div>
              <label htmlFor="integrante-receptor-planilla" className={labelClassName}>
                Integrante receptor
              </label>
              <IntegranteReceptorSelect
                id="integrante-receptor-planilla"
                formulario2aId={formularioId}
                value={form.integrante_receptor_id}
                onChange={(integranteId) => handleChange('integrante_receptor_id', integranteId)}
                disabled={loading}
              />
              {errores.integrante_receptor_id && (
                <p className="mt-1 text-xs text-red-600">{errores.integrante_receptor_id}</p>
              )}
            </div>

            <div>
              <label htmlFor="fecha-entrega-planilla" className={labelClassName}>
                Fecha de entrega
              </label>
              <input
                id="fecha-entrega-planilla"
                type="date"
                value={form.fecha_entrega}
                onChange={(event) => handleChange('fecha_entrega', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
              {errores.fecha_entrega && (
                <p className="mt-1 text-xs text-red-600">{errores.fecha_entrega}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label htmlFor="observacion-planilla" className={labelClassName}>
                Observación
              </label>
              <textarea
                id="observacion-planilla"
                value={form.planilla_observacion}
                onChange={(event) => handleChange('planilla_observacion', event.target.value)}
                maxLength={1000}
                rows={3}
                disabled={loading}
                className={inputClassName}
              />
              {errores.planilla_observacion && (
                <p className="mt-1 text-xs text-red-600">{errores.planilla_observacion}</p>
              )}
            </div>
          </div>
        </section>

        <MovimientoDetalleFilas
          lineas={lineas}
          errores={errores}
          naturaleza={naturaleza}
          disabled={loading}
          onAgregar={handleAgregarBien}
          onQuitar={handleQuitarBien}
          onCambiar={handleCambiarLinea}
        />

        <div className="flex flex-wrap gap-2">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Grabando...' : 'Grabar planilla'}
          </button>
          <Link
            to="/alm-planilla-bah"
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            Cancelar
          </Link>
        </div>
      </form>
    </div>
  )
}
