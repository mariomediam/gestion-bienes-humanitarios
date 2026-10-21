import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import { mostrarMovimientoRecienCreado } from '@features/movimientos/hooks/useMovimientosBusqueda'
import EncargadoAlmacenSelect from '@features/movimientos/components/EncargadoAlmacenSelect'
import MovimientoDetalleFilas from '@features/movimientos/components/MovimientoDetalleFilas'
import TipoMovimientoSelect from '@features/movimientos/components/TipoMovimientoSelect'

const ALMACEN_CENTRAL_ID = 1
const ESTADO_MOVIMIENTO_CONFIRMADO_ID = 2
const TIPO_MOVIMIENTO_ENTREGA_BAH_ID = 7

const EMPTY_FORM = {
  tipo_movimiento_id: '',
  naturaleza: '',
  fecha_movimiento: '',
  documento_referencia: '',
  fecha_documento: '',
  destinatario: '',
  observacion: '',
  encargado: null,
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

function fechaMovimientoParaInput(value) {
  if (!value) return ''
  const coincidencia = String(value).trim().match(/^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2})/)
  if (!coincidencia) return ''
  return `${coincidencia[1]}T${coincidencia[2]}`
}

function fechaDocumentoParaInput(value) {
  if (!value) return ''
  const coincidencia = String(value).trim().match(/^(\d{4}-\d{2}-\d{2})/)
  return coincidencia ? coincidencia[1] : ''
}

function cantidadParaFormulario(cantidad, naturaleza) {
  let texto = String(cantidad ?? '').trim()
  if (!texto) return ''
  if ((naturaleza === 'E' || naturaleza === 'S') && texto.startsWith('-')) {
    texto = texto.slice(1)
  }
  if (texto.includes('.')) {
    texto = texto.replace(/0+$/, '').replace(/\.$/, '')
  }
  return texto
}

function formularioDesdeMovimiento(movimiento, siguienteKey) {
  const naturaleza = movimiento.tipo_movimiento_naturaleza || ''
  return {
    form: {
      tipo_movimiento_id: movimiento.tipo_movimiento_id
        ? String(movimiento.tipo_movimiento_id)
        : '',
      naturaleza,
      fecha_movimiento: fechaMovimientoParaInput(movimiento.fecha_movimiento),
      documento_referencia: movimiento.documento_referencia ?? '',
      fecha_documento: fechaDocumentoParaInput(movimiento.fecha_documento),
      destinatario: movimiento.destinatario ?? '',
      observacion: movimiento.observacion ?? '',
      encargado: movimiento.encargado_almacen_id
        ? {
            value: movimiento.encargado_almacen_id,
            label: movimiento.encargado_almacen_nombre || '',
          }
        : null,
    },
    lineas: (movimiento.detalles || []).map((detalle) => ({
      key: siguienteKey(),
      bien: {
        value: detalle.bien_id,
        label: detalle.bien_nombre,
        unidad_medida_nombre: detalle.unidad_medida_nombre || '',
        unidad_medida_abreviatura: detalle.unidad_medida_abreviatura || '',
      },
      cantidad: cantidadParaFormulario(detalle.cantidad, naturaleza),
      cantidad_texto: detalle.cantidad_texto ?? '',
    })),
  }
}

function validarFormulario(form, lineas) {
  const errores = {}

  if (!form.tipo_movimiento_id) {
    errores.tipo_movimiento_id = 'El tipo de movimiento es obligatorio'
  }
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

    const errorCantidad = validarCantidad(linea.cantidad, form.naturaleza)
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

export default function MovimientoFormPage() {
  const { movimientoId } = useParams()
  const esEdicion = Boolean(movimientoId)
  const navigate = useNavigate()
  const lineaId = useRef(0)
  const [form, setForm] = useState(EMPTY_FORM)
  const [lineas, setLineas] = useState([])
  const [errores, setErrores] = useState({})
  const [loading, setLoading] = useState(false)
  const [cargandoMovimiento, setCargandoMovimiento] = useState(esEdicion)

  useEffect(() => {
    if (!movimientoId) {
      setForm(EMPTY_FORM)
      setLineas([])
      setErrores({})
      setCargandoMovimiento(false)
      return undefined
    }

    let active = true
    let salir = false
    setCargandoMovimiento(true)
    setErrores({})

    sgbhApi
      .buscarMovimientos({ movimiento_id: movimientoId })
      .then((rows) => {
        if (!active) return
        const movimiento = Array.isArray(rows) ? rows[0] : null
        if (!movimiento) {
          salir = true
          toast.error('El movimiento de almacén indicado no existe')
          navigate('/alm-movimientos')
          return
        }
        const cargado = formularioDesdeMovimiento(movimiento, () => {
          lineaId.current += 1
          return lineaId.current
        })
        setForm(cargado.form)
        setLineas(cargado.lineas)
      })
      .catch((error) => {
        if (!active) return
        salir = true
        toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de movimientos de almacén'))
        navigate('/alm-movimientos')
      })
      .finally(() => {
        if (active && !salir) {
          setCargandoMovimiento(false)
        }
      })

    return () => {
      active = false
    }
  }, [movimientoId, navigate])

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

  function handleTipoChange(tipoMovimientoId, tipo) {
    setForm((current) => ({
      ...current,
      tipo_movimiento_id: tipoMovimientoId,
      naturaleza: tipo?.naturaleza || '',
    }))
    limpiarError('tipo_movimiento_id')
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
    const nextErrores = validarFormulario(form, lineas)
    setErrores(nextErrores)
    if (Object.keys(nextErrores).length > 0) return

    const fechaMovimiento = fechaHoraApi(form.fecha_movimiento)
    const payload = {
      almacen_id: ALMACEN_CENTRAL_ID,
      tipo_movimiento_id: Number(form.tipo_movimiento_id),
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
        cantidad: cantidadParaApi(linea.cantidad, form.naturaleza),
        cantidad_texto: textoOpcional(linea.cantidad_texto),
        es_devolvible: false,
        observacion: '',
      })),
    }

    setLoading(true)
    try {
      if (esEdicion) {
        await sgbhApi.actualizarMovimiento(movimientoId, payload)
        toast.success('Movimiento modificado correctamente')
      } else {
        const creado = await sgbhApi.crearMovimiento(payload)
        toast.success('Movimiento registrado correctamente')
        if (creado?.movimiento_id) {
          await mostrarMovimientoRecienCreado(creado.movimiento_id)
        }
      }
      navigate('/alm-movimientos')
    } catch (error) {
      toast.error(
        getErrorMessage(
          error,
          esEdicion
            ? 'No se pudo modificar el movimiento de almacén'
            : 'No se pudo registrar el movimiento de almacén',
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  if (cargandoMovimiento) {
    return (
      <div className="space-y-6">
        <Link
          to="/alm-movimientos"
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
        to="/alm-movimientos"
        className="inline-flex text-sm font-medium text-[#1e3064] hover:underline focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 rounded-sm"
      >
        Volver al listado
      </Link>

      <div>
        <h1 className="text-2xl font-bold text-[#1e3064]">
          {esEdicion ? 'Modificar movimiento' : 'Agregar movimiento'}
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          {esEdicion
            ? 'Modificación de un movimiento de almacén y sus bienes'
            : 'Registro de un movimiento de almacén y sus bienes'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <section className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
          <h2 className="text-lg font-semibold text-[#1e3064]">Datos del movimiento</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="tipo-movimiento-nuevo" className={labelClassName}>
                Tipo de movimiento
              </label>
              <TipoMovimientoSelect
                id="tipo-movimiento-nuevo"
                value={form.tipo_movimiento_id}
                onChange={handleTipoChange}
                disabled={loading}
                excluirIds={[TIPO_MOVIMIENTO_ENTREGA_BAH_ID]}
              />
              {errores.tipo_movimiento_id && (
                <p className="mt-1 text-xs text-red-600">{errores.tipo_movimiento_id}</p>
              )}
            </div>

            <div>
              <label htmlFor="fecha-movimiento-nueva" className={labelClassName}>
                Fecha de movimiento
              </label>
              <input
                id="fecha-movimiento-nueva"
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
              <label htmlFor="documento-referencia-nuevo" className={labelClassName}>
                Documento de referencia
              </label>
              <input
                id="documento-referencia-nuevo"
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
              <label htmlFor="fecha-documento-nueva" className={labelClassName}>
                Fecha de documento
              </label>
              <input
                id="fecha-documento-nueva"
                type="date"
                value={form.fecha_documento}
                onChange={(event) => handleChange('fecha_documento', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
            </div>

            <div>
              <label htmlFor="destinatario-nuevo" className={labelClassName}>
                Destinatario
              </label>
              <input
                id="destinatario-nuevo"
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
              <label htmlFor="encargado-almacen-nuevo" className={labelClassName}>
                Encargado de almacén
              </label>
              <EncargadoAlmacenSelect
                inputId="encargado-almacen-nuevo"
                value={form.encargado}
                onChange={(encargado) => handleChange('encargado', encargado)}
                disabled={loading}
              />
              {errores.encargado && (
                <p className="mt-1 text-xs text-red-600">{errores.encargado}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label htmlFor="observacion-movimiento-nueva" className={labelClassName}>
                Observación
              </label>
              <textarea
                id="observacion-movimiento-nueva"
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

        <MovimientoDetalleFilas
          lineas={lineas}
          errores={errores}
          naturaleza={form.naturaleza}
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
            {loading ? 'Grabando...' : 'Grabar movimiento'}
          </button>
          <Link
            to="/alm-movimientos"
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            Cancelar
          </Link>
        </div>
      </form>
    </div>
  )
}
