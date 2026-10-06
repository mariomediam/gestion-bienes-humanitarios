import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import DistritoSelect from '@components/DistritoSelect'
import EvaluadorSelect from '@features/formularios2a/components/EvaluadorSelect'

const INSTITUCION = 'MUNICIPALIDAD PROVINCIAL DE PIURA'
const ESTADO_REGISTRO_ID = 1
const SMALLINT_MAX = 32767

const EMPTY_FORM = {
  distrito: null,
  fecha_empadronamiento: '',
  hora_empadronamiento: '',
  localidad: '',
  barrio_sector_urbanizacion: '',
  caserio: '',
  anexo: '',
  calle_manzana: '',
  edificio_piso_dpto: '',
  otros_ubicacion: '',
  numero_hoja: '',
  total_hojas: '',
  evaluador: null,
}

const TEXT_FIELDS = [
  ['localidad', 200],
  ['barrio_sector_urbanizacion', 250],
  ['caserio', 200],
  ['anexo', 200],
  ['calle_manzana', 250],
  ['edificio_piso_dpto', 250],
  ['otros_ubicacion', 250],
]

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function parseEnteroPositivo(value) {
  const text = String(value).trim()
  if (text === '') return { empty: true }
  if (!/^\d+$/.test(text)) return { invalid: true }
  const number = Number(text)
  if (number < 1 || number > SMALLINT_MAX) return { invalid: true }
  return { value: number }
}

function validate(form) {
  const errors = {}
  if (!form.distrito) {
    errors.distrito = 'El distrito es obligatorio'
  }
  if (!form.fecha_empadronamiento) {
    errors.fecha_empadronamiento = 'La fecha de empadronamiento es obligatoria'
  }
  if (!form.evaluador) {
    errors.evaluador = 'El evaluador es obligatorio'
  }

  const numeroHoja = parseEnteroPositivo(form.numero_hoja)
  if (numeroHoja.invalid) {
    errors.numero_hoja = 'El campo numero_hoja debe ser un número entero mayor que cero'
  }

  const totalHojas = parseEnteroPositivo(form.total_hojas)
  if (totalHojas.invalid) {
    errors.total_hojas = 'El campo total_hojas debe ser un número entero mayor que cero'
  }

  if (!numeroHoja.invalid && !totalHojas.invalid && !totalHojas.empty) {
    const numeroEfectivo = numeroHoja.empty ? 1 : numeroHoja.value
    if (totalHojas.value < numeroEfectivo) {
      errors.total_hojas = 'El campo total_hojas debe ser mayor o igual que numero_hoja'
    }
  }

  return { errors, numeroHoja, totalHojas }
}

function Campo({ id, label, error, children, className = '' }) {
  return (
    <div className={`min-w-0 ${className}`}>
      <label htmlFor={id} className={labelClassName}>
        {label}
      </label>
      {children}
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  )
}

export default function Formulario2AFormModal({
  isOpen,
  emergenciaId,
  codigoSinpad,
  onClose,
  onSaved,
}) {
  const [form, setForm] = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!isOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !loading) {
        setForm(EMPTY_FORM)
        setErrors({})
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, loading, onClose])

  if (!isOpen) return null

  function handleChange(name, value) {
    setForm((current) => ({ ...current, [name]: value }))
    if (errors[name]) {
      setErrors((current) => ({ ...current, [name]: '' }))
    }
  }

  function handleClose() {
    if (loading) return
    setForm(EMPTY_FORM)
    setErrors({})
    onClose()
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const { errors: nextErrors, numeroHoja, totalHojas } = validate(form)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    const payload = {
      emergencia_id: emergenciaId,
      departamento_id: form.distrito.departamento_id,
      provincia_id: form.distrito.provincia_id,
      distrito_id: form.distrito.distrito_id,
      fecha_empadronamiento: form.fecha_empadronamiento,
      institucion: INSTITUCION,
      evaluador_id: form.evaluador.value,
      estado_registro_id: ESTADO_REGISTRO_ID,
    }

    if (form.hora_empadronamiento) {
      payload.hora_empadronamiento = form.hora_empadronamiento
    }

    TEXT_FIELDS.forEach(([name]) => {
      const text = form[name].trim()
      if (text) payload[name] = text
    })

    if (!numeroHoja.empty) payload.numero_hoja = numeroHoja.value
    if (!totalHojas.empty) payload.total_hojas = totalHojas.value

    setLoading(true)
    try {
      const saved = await sgbhApi.crearFormulario2A(payload)
      toast.success('Formulario EDAN 2A registrado correctamente')
      setForm(EMPTY_FORM)
      setErrors({})
      onSaved(saved)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo registrar el formulario EDAN 2A'))
    } finally {
      setLoading(false)
    }
  }

  return createPortal(
    <div
      className="fixed inset-0 z-50 grid p-4"
      style={{ gridTemplateRows: 'minmax(0, 1fr)', alignItems: 'center', justifyItems: 'center' }}
    >
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-formulario-2a"
        onClick={(event) => event.stopPropagation()}
        className="formulario-2a-scroll relative z-10 w-full max-w-2xl rounded-lg bg-white shadow-xl"
        style={{ maxHeight: '100%', minHeight: 0, overflowY: 'scroll' }}
      >
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4">
          <h2 id="titulo-formulario-2a" className="text-lg font-semibold text-[#1e3064]">
            Datos del formulario 2A
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
          {codigoSinpad && (
            <p className="text-sm text-gray-600">
              Código SINPAD: <span className="font-medium text-gray-800">{codigoSinpad}</span>
            </p>
          )}

          <div className="grid min-w-0 grid-cols-1 gap-4 sm:grid-cols-2">
            <Campo id="distrito-formulario-2a-nuevo" label="Distrito" error={errors.distrito} className="sm:col-span-2">
              <DistritoSelect
                inputId="distrito-formulario-2a-nuevo"
                value={form.distrito}
                onChange={(option) => handleChange('distrito', option)}
                disabled={loading}
              />
            </Campo>

            <Campo id="fecha-empadronamiento-nueva" label="Fecha de empadronamiento" error={errors.fecha_empadronamiento}>
              <input
                id="fecha-empadronamiento-nueva"
                type="date"
                value={form.fecha_empadronamiento}
                onChange={(event) => handleChange('fecha_empadronamiento', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="hora-empadronamiento-nueva" label="Hora de empadronamiento" error={errors.hora_empadronamiento}>
              <input
                id="hora-empadronamiento-nueva"
                type="time"
                value={form.hora_empadronamiento}
                onChange={(event) => handleChange('hora_empadronamiento', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="localidad-formulario-2a-nueva" label="Localidad" error={errors.localidad}>
              <input
                id="localidad-formulario-2a-nueva"
                type="text"
                value={form.localidad}
                onChange={(event) => handleChange('localidad', event.target.value)}
                maxLength={200}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="barrio-formulario-2a-nuevo" label="Barrio, sector o urbanización" error={errors.barrio_sector_urbanizacion}>
              <input
                id="barrio-formulario-2a-nuevo"
                type="text"
                value={form.barrio_sector_urbanizacion}
                onChange={(event) => handleChange('barrio_sector_urbanizacion', event.target.value)}
                maxLength={250}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="caserio-formulario-2a-nuevo" label="Caserío" error={errors.caserio}>
              <input
                id="caserio-formulario-2a-nuevo"
                type="text"
                value={form.caserio}
                onChange={(event) => handleChange('caserio', event.target.value)}
                maxLength={200}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="anexo-formulario-2a-nuevo" label="Anexo" error={errors.anexo}>
              <input
                id="anexo-formulario-2a-nuevo"
                type="text"
                value={form.anexo}
                onChange={(event) => handleChange('anexo', event.target.value)}
                maxLength={200}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="calle-formulario-2a-nueva" label="Calle o manzana" error={errors.calle_manzana}>
              <input
                id="calle-formulario-2a-nueva"
                type="text"
                value={form.calle_manzana}
                onChange={(event) => handleChange('calle_manzana', event.target.value)}
                maxLength={250}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="edificio-formulario-2a-nuevo" label="Edificio, piso o departamento" error={errors.edificio_piso_dpto}>
              <input
                id="edificio-formulario-2a-nuevo"
                type="text"
                value={form.edificio_piso_dpto}
                onChange={(event) => handleChange('edificio_piso_dpto', event.target.value)}
                maxLength={250}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="otros-ubicacion-formulario-2a" label="Otros datos de ubicación" error={errors.otros_ubicacion} className="sm:col-span-2">
              <input
                id="otros-ubicacion-formulario-2a"
                type="text"
                value={form.otros_ubicacion}
                onChange={(event) => handleChange('otros_ubicacion', event.target.value)}
                maxLength={250}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="numero-hoja-formulario-2a" label="Número de hoja" error={errors.numero_hoja}>
              <input
                id="numero-hoja-formulario-2a"
                type="number"
                min={1}
                max={SMALLINT_MAX}
                step={1}
                value={form.numero_hoja}
                onChange={(event) => handleChange('numero_hoja', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="total-hojas-formulario-2a" label="Total de hojas" error={errors.total_hojas}>
              <input
                id="total-hojas-formulario-2a"
                type="number"
                min={1}
                max={SMALLINT_MAX}
                step={1}
                value={form.total_hojas}
                onChange={(event) => handleChange('total_hojas', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="evaluador-formulario-2a-nuevo" label="Evaluador" error={errors.evaluador} className="sm:col-span-2">
              <EvaluadorSelect
                inputId="evaluador-formulario-2a-nuevo"
                value={form.evaluador}
                onChange={(option) => handleChange('evaluador', option)}
                disabled={loading}
              />
            </Campo>
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
              {loading ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      </div>
    </div>,
    document.body,
  )
}
