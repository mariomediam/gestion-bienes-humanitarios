import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import EncargadoAlmacenSelect from '@features/movimientos/components/EncargadoAlmacenSelect'
import {
  cantidadSuperaSaldo,
  normalizarCantidad,
  saldoDevolucion,
} from '@features/devoluciones/cantidades'
import DevolucionBienes from '@features/devoluciones/components/DevolucionBienes'
import { mostrarDevolucionRecienCreada } from '@features/devoluciones/hooks/useDevolucionesBusqueda'
import useDevolucionesBusquedaStore from '@store/devolucionesBusquedaStore'

const ALMACEN_CENTRAL_ID = 1
const ESTADO_MOVIMIENTO_CONFIRMADO_ID = 2
const CODIGO_DEVOLUCION = 'DEVOLUCION'

const EMPTY_FORM = {
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
  const texto = String(value ?? '').trim()
  return texto || null
}

function fechaHoraApi(value) {
  if (!value) return null
  return value.length === 16 ? `${value}:00` : value
}

function validarCantidad(raw) {
  const texto = normalizarCantidad(raw)
  if (!texto) return 'La cantidad es obligatoria'
  if (!/^\d+(\.\d+)?$/.test(texto)) {
    return 'La cantidad debe ser un número decimal'
  }

  const [entera, decimal = ''] = texto.split('.')
  if (entera.length > 12 || decimal.length > 6) {
    return 'La cantidad debe tener como máximo 18 dígitos y 6 decimales'
  }

  if (Number(texto) === 0) return 'La cantidad debe ser distinta de cero'
  return ''
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

function cantidadParaFormulario(cantidad) {
  let texto = String(cantidad ?? '').trim()
  if (!texto) return ''
  if (texto.startsWith('-')) {
    texto = texto.slice(1)
  }
  if (texto.includes('.')) {
    texto = texto.replace(/0+$/, '').replace(/\.$/, '')
  }
  return texto
}

function formularioDesdeMovimiento(movimiento) {
  return {
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
  }
}

function bienesDesdeOrigen(filas, detalles) {
  const pendientes = new Map()
  for (const detalle of detalles || []) {
    const lista = pendientes.get(detalle.bien_id) || []
    lista.push(detalle)
    pendientes.set(detalle.bien_id, lista)
  }

  return (filas || []).map((fila, index) => {
    const guardados = pendientes.get(fila.bien_id) || []
    const detalle = guardados.shift()

    return {
      key: `${fila.bien_id}-${index}`,
      bien_id: fila.bien_id,
      bien_nombre: fila.bien_nombre,
      abreviatura_nombre: fila.abreviatura_nombre,
      saldo: saldoDevolucion(fila.cantidad_origen, fila.cantidad_entrada),
      cantidad: detalle ? cantidadParaFormulario(detalle.cantidad) : '',
      cantidad_texto: detalle?.cantidad_texto ?? '',
      observacion: detalle?.movimiento_detalle_observacion ?? '',
    }
  })
}

function validarFormulario(form, bienes, esEdicion) {
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

  const conCantidad = bienes.filter((bien) => normalizarCantidad(bien.cantidad) !== '')
  if (conCantidad.length === 0) {
    errores.detalles = 'Debe registrar al menos un detalle'
  }

  bienes.forEach((bien) => {
    const cantidad = normalizarCantidad(bien.cantidad)
    if (!cantidad) return

    const errorLinea = {}
    const errorCantidad = validarCantidad(cantidad)
    if (errorCantidad) {
      errorLinea.cantidad = errorCantidad
    } else if (!esEdicion && cantidadSuperaSaldo(cantidad, bien.saldo)) {
      errorLinea.cantidad = 'La cantidad a devolver no puede ser mayor al saldo'
    }

    if (Object.keys(errorLinea).length > 0) {
      errores[bien.key] = errorLinea
    }
  })

  return errores
}

export default function DevolucionFormPage() {
  const { movimientoId, movimientoOrigenId } = useParams()
  const esEdicion = Boolean(movimientoId)
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY_FORM)
  const [bienes, setBienes] = useState([])
  const [tipoDevolucionId, setTipoDevolucionId] = useState(null)
  const [origenId, setOrigenId] = useState(movimientoOrigenId || null)
  const [errores, setErrores] = useState({})
  const [loading, setLoading] = useState(false)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    let active = true
    let salir = false
    setCargando(true)
    setErrores({})

    async function cargar() {
      try {
        const tipos = await sgbhApi.getTiposMovimiento({ codigo: CODIGO_DEVOLUCION })
        const tipo = Array.isArray(tipos) ? tipos[0] : null
        if (!tipo) {
          salir = true
          toast.error('No se encontró el tipo de movimiento de devolución')
          navigate('/alm-devolucion')
          return
        }
        if (!active) return
        setTipoDevolucionId(tipo.tipo_movimiento_id)

        if (esEdicion) {
          const rows = await sgbhApi.buscarMovimientos({ movimiento_id: movimientoId })
          const movimiento = Array.isArray(rows) ? rows[0] : null
          if (
            !movimiento
            || movimiento.tipo_movimiento_codigo !== CODIGO_DEVOLUCION
            || !movimiento.movimiento_origen_id
          ) {
            salir = true
            toast.error('La devolución indicada no existe')
            navigate('/alm-devolucion')
            return
          }
          const filas = await sgbhApi.getCantidadesPorDevolver(movimiento.movimiento_origen_id)
          if (!active) return
          setOrigenId(movimiento.movimiento_origen_id)
          setForm(formularioDesdeMovimiento(movimiento))
          setBienes(bienesDesdeOrigen(filas, movimiento.detalles))
          return
        }

        const filas = await sgbhApi.getCantidadesPorDevolver(movimientoOrigenId)
        if (!active) return
        setOrigenId(movimientoOrigenId)
        setForm(EMPTY_FORM)
        setBienes(bienesDesdeOrigen(filas, []))
      } catch (error) {
        if (!active) return
        salir = true
        toast.error(getErrorMessage(error, 'No se pudo obtener la devolución'))
        navigate('/alm-devolucion')
      } finally {
        if (active && !salir) {
          setCargando(false)
        }
      }
    }

    cargar()

    return () => {
      active = false
    }
  }, [esEdicion, movimientoId, movimientoOrigenId, navigate])

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

  function handleCambiarCantidad(key, value) {
    setBienes((current) =>
      current.map((bien) => (bien.key === key ? { ...bien, cantidad: value } : bien)),
    )
    setErrores((current) => {
      const errorLinea = current[key]
      if (!errorLinea?.cantidad && !current.detalles) return current
      const next = { ...current }
      if (errorLinea?.cantidad) {
        const nextLinea = { ...errorLinea }
        delete nextLinea.cantidad
        if (Object.keys(nextLinea).length === 0) {
          delete next[key]
        } else {
          next[key] = nextLinea
        }
      }
      delete next.detalles
      return next
    })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const nextErrores = validarFormulario(form, bienes, esEdicion)
    setErrores(nextErrores)
    if (Object.keys(nextErrores).length > 0 || !tipoDevolucionId || !origenId) return

    const fechaMovimiento = fechaHoraApi(form.fecha_movimiento)
    const payload = {
      almacen_id: ALMACEN_CENTRAL_ID,
      tipo_movimiento_id: Number(tipoDevolucionId),
      estado_movimiento_id: ESTADO_MOVIMIENTO_CONFIRMADO_ID,
      movimiento_origen_id: Number(origenId),
      fecha_movimiento: fechaMovimiento,
      documento_referencia: textoOpcional(form.documento_referencia),
      fecha_documento: form.fecha_documento || null,
      destinatario: textoOpcional(form.destinatario),
      observacion: textoOpcional(form.observacion),
      fecha_confirmacion: fechaMovimiento,
      encargado_almacen_id: form.encargado.value,
      detalles: bienes
        .filter((bien) => normalizarCantidad(bien.cantidad) !== '')
        .map((bien) => ({
          bien_id: bien.bien_id,
          cantidad: normalizarCantidad(bien.cantidad),
          cantidad_texto: textoOpcional(bien.cantidad_texto),
          es_devolvible: false,
          observacion: bien.observacion ?? '',
        })),
    }

    setLoading(true)
    try {
      if (esEdicion) {
        await sgbhApi.actualizarMovimiento(movimientoId, payload)
        toast.success('Devolución modificada correctamente')
        useDevolucionesBusquedaStore.getState().solicitarActualizacion()
      } else {
        const creado = await sgbhApi.crearMovimiento(payload)
        toast.success('Devolución registrada correctamente')
        if (creado?.movimiento_id) {
          await mostrarDevolucionRecienCreada(creado.movimiento_id)
        }
      }
      navigate('/alm-devolucion')
    } catch (error) {
      toast.error(
        getErrorMessage(
          error,
          esEdicion
            ? 'No se pudo modificar la devolución'
            : 'No se pudo registrar la devolución',
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  if (cargando) {
    return (
      <div className="space-y-6">
        <Link
          to="/alm-devolucion"
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
        to="/alm-devolucion"
        className="inline-flex text-sm font-medium text-[#1e3064] hover:underline focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 rounded-sm"
      >
        Volver al listado
      </Link>

      <div>
        <h1 className="text-2xl font-bold text-[#1e3064]">
          {esEdicion ? 'Modificar devolución' : 'Agregar devolución'}
        </h1>
        <p className="mt-1 text-sm text-gray-600">
          {esEdicion
            ? 'Modificación de una devolución y sus bienes'
            : 'Registro de una devolución y sus bienes'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <section className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
          <h2 className="text-lg font-semibold text-[#1e3064]">Datos de la devolución</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="fecha-movimiento-devolucion" className={labelClassName}>
                Fecha de movimiento
              </label>
              <input
                id="fecha-movimiento-devolucion"
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
              <label htmlFor="documento-referencia-devolucion-nueva" className={labelClassName}>
                Documento de referencia
              </label>
              <input
                id="documento-referencia-devolucion-nueva"
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
              <label htmlFor="fecha-documento-devolucion" className={labelClassName}>
                Fecha de documento
              </label>
              <input
                id="fecha-documento-devolucion"
                type="date"
                value={form.fecha_documento}
                onChange={(event) => handleChange('fecha_documento', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
            </div>

            <div>
              <label htmlFor="destinatario-devolucion" className={labelClassName}>
                Destinatario
              </label>
              <input
                id="destinatario-devolucion"
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
              <label htmlFor="encargado-almacen-devolucion" className={labelClassName}>
                Encargado de almacén
              </label>
              <EncargadoAlmacenSelect
                inputId="encargado-almacen-devolucion"
                value={form.encargado}
                onChange={(encargado) => handleChange('encargado', encargado)}
                disabled={loading}
              />
              {errores.encargado && (
                <p className="mt-1 text-xs text-red-600">{errores.encargado}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label htmlFor="observacion-devolucion" className={labelClassName}>
                Observación
              </label>
              <textarea
                id="observacion-devolucion"
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

        <DevolucionBienes
          bienes={bienes}
          errores={errores}
          disabled={loading}
          onCambiarCantidad={handleCambiarCantidad}
        />

        <div className="flex flex-wrap gap-2">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Grabando...' : 'Grabar devolución'}
          </button>
          <Link
            to="/alm-devolucion"
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            Cancelar
          </Link>
        </div>
      </form>
    </div>
  )
}
