import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import EncargadoAlmacenSelect from '@features/movimientos/components/EncargadoAlmacenSelect'
import MovimientoDetalleFilas from '@features/movimientos/components/MovimientoDetalleFilas'
import TipoMovimientoSelect from '@features/movimientos/components/TipoMovimientoSelect'

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

export default function MovimientoVerPage() {
  const { movimientoId } = useParams()
  const navigate = useNavigate()
  const lineaId = useRef(0)
  const [form, setForm] = useState(EMPTY_FORM)
  const [lineas, setLineas] = useState([])
  const [cargandoMovimiento, setCargandoMovimiento] = useState(true)

  useEffect(() => {
    let active = true
    let salir = false
    setCargandoMovimiento(true)

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
        <h1 className="text-2xl font-bold text-[#1e3064]">Ver movimiento</h1>
        <p className="mt-1 text-sm text-gray-600">
          Consulta de un movimiento de almacén y sus bienes
        </p>
      </div>

      <div className="space-y-6">
        <section className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
          <h2 className="text-lg font-semibold text-[#1e3064]">Datos del movimiento</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="tipo-movimiento-ver" className={labelClassName}>
                Tipo de movimiento
              </label>
              <TipoMovimientoSelect
                id="tipo-movimiento-ver"
                value={form.tipo_movimiento_id}
                onChange={() => {}}
                disabled
              />
            </div>

            <div>
              <label htmlFor="fecha-movimiento-ver" className={labelClassName}>
                Fecha de movimiento
              </label>
              <input
                id="fecha-movimiento-ver"
                type="datetime-local"
                value={form.fecha_movimiento}
                readOnly
                disabled
                className={inputClassName}
              />
            </div>

            <div>
              <label htmlFor="documento-referencia-ver" className={labelClassName}>
                Documento de referencia
              </label>
              <input
                id="documento-referencia-ver"
                type="text"
                value={form.documento_referencia}
                readOnly
                disabled
                className={inputClassName}
              />
            </div>

            <div>
              <label htmlFor="fecha-documento-ver" className={labelClassName}>
                Fecha de documento
              </label>
              <input
                id="fecha-documento-ver"
                type="date"
                value={form.fecha_documento}
                readOnly
                disabled
                className={inputClassName}
              />
            </div>

            <div>
              <label htmlFor="destinatario-ver" className={labelClassName}>
                Destinatario
              </label>
              <input
                id="destinatario-ver"
                type="text"
                value={form.destinatario}
                readOnly
                disabled
                className={inputClassName}
              />
            </div>

            <div>
              <label htmlFor="encargado-almacen-ver" className={labelClassName}>
                Encargado de almacén
              </label>
              <EncargadoAlmacenSelect
                inputId="encargado-almacen-ver"
                value={form.encargado}
                onChange={() => {}}
                disabled
              />
            </div>

            <div className="md:col-span-2">
              <label htmlFor="observacion-movimiento-ver" className={labelClassName}>
                Observación
              </label>
              <textarea
                id="observacion-movimiento-ver"
                value={form.observacion}
                readOnly
                disabled
                rows={3}
                className={inputClassName}
              />
            </div>
          </div>
        </section>

        <MovimientoDetalleFilas
          lineas={lineas}
          errores={{}}
          naturaleza={form.naturaleza}
          soloLectura
          onAgregar={() => {}}
          onQuitar={() => {}}
          onCambiar={() => {}}
        />

        <div>
          <Link
            to="/alm-movimientos"
            className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
          >
            Volver al listado
          </Link>
        </div>
      </div>
    </div>
  )
}
