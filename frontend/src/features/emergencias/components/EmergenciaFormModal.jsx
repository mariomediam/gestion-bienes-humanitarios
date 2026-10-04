import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import TipoPeligroSelect from '@features/emergencias/components/TipoPeligroSelect'

const EMPTY_FORM = {
  numero_evaluacion: '',
  codigo_sinpad: '',
  tipoPeligro: null,
  fecha_emergencia: '',
  hora_ocurrencia_estimada: '',
}

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function toTimeInput(hora) {
  if (!hora) return ''
  return String(hora).slice(0, 5)
}

function formFromEmergencia(emergencia) {
  return {
    numero_evaluacion: emergencia.numero_evaluacion ?? '',
    codigo_sinpad: emergencia.codigo_sinpad ?? '',
    tipoPeligro: emergencia.tipo_peligro_id
      ? {
          value: emergencia.tipo_peligro_id,
          label: emergencia.nombre_tipo_peligro ?? '',
        }
      : null,
    fecha_emergencia: emergencia.fecha_emergencia
      ? String(emergencia.fecha_emergencia).slice(0, 10)
      : '',
    hora_ocurrencia_estimada: toTimeInput(emergencia.hora_ocurrencia_estimada),
  }
}

export default function EmergenciaFormModal({ isOpen, onClose, onSaved, emergencia = null }) {
  const [form, setForm] = useState(() =>
    emergencia ? formFromEmergencia(emergencia) : EMPTY_FORM,
  )
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const isEdit = emergencia !== null

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

  function validate() {
    const nextErrors = {}
    if (!form.numero_evaluacion.trim()) {
      nextErrors.numero_evaluacion = 'El número de evaluación es obligatorio'
    }
    if (!form.codigo_sinpad.trim()) {
      nextErrors.codigo_sinpad = 'El código SINPAD es obligatorio'
    }
    if (!form.tipoPeligro) {
      nextErrors.tipoPeligro = 'El tipo de peligro es obligatorio'
    }
    if (!form.fecha_emergencia) {
      nextErrors.fecha_emergencia = 'La fecha de emergencia es obligatoria'
    }
    return nextErrors
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const nextErrors = validate()
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    const payload = {
      numero_evaluacion: form.numero_evaluacion.trim(),
      codigo_sinpad: form.codigo_sinpad.trim(),
      tipo_peligro_id: form.tipoPeligro.value,
      fecha_emergencia: form.fecha_emergencia,
    }
    if (form.hora_ocurrencia_estimada) {
      payload.hora_ocurrencia_estimada = form.hora_ocurrencia_estimada
    }
    if (isEdit) {
      payload.esta_activo = emergencia.esta_activo
    }

    setLoading(true)
    try {
      const saved = isEdit
        ? await sgbhApi.actualizarEmergencia(emergencia.emergencia_id, payload)
        : await sgbhApi.crearEmergencia(payload)
      toast.success(
        isEdit ? 'Emergencia modificada correctamente' : 'Emergencia registrada correctamente',
      )
      setForm(EMPTY_FORM)
      setErrors({})
      onSaved(saved)
    } catch (error) {
      toast.error(
        getErrorMessage(
          error,
          isEdit ? 'No se pudo modificar la emergencia' : 'No se pudo registrar la emergencia',
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-emergencia"
        className="relative bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 id="titulo-emergencia" className="text-lg font-semibold text-[#1e3064]">
            {isEdit ? 'Modificar emergencia' : 'Agregar nueva emergencia'}
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="numero-evaluacion-nueva" className={labelClassName}>
                Número de evaluación
              </label>
              <input
                id="numero-evaluacion-nueva"
                type="text"
                value={form.numero_evaluacion}
                onChange={(event) => handleChange('numero_evaluacion', event.target.value)}
                maxLength={50}
                disabled={loading}
                autoFocus
                className={inputClassName}
              />
              {errors.numero_evaluacion && (
                <p className="mt-1 text-xs text-red-600">{errors.numero_evaluacion}</p>
              )}
            </div>

            <div>
              <label htmlFor="codigo-sinpad-nueva" className={labelClassName}>
                Código SINPAD
              </label>
              <input
                id="codigo-sinpad-nueva"
                type="text"
                value={form.codigo_sinpad}
                onChange={(event) => handleChange('codigo_sinpad', event.target.value)}
                maxLength={30}
                disabled={loading}
                className={inputClassName}
              />
              {errors.codigo_sinpad && (
                <p className="mt-1 text-xs text-red-600">{errors.codigo_sinpad}</p>
              )}
            </div>

            <div>
              <label htmlFor="tipo-peligro-nueva" className={labelClassName}>
                Tipo de peligro
              </label>
              <TipoPeligroSelect
                inputId="tipo-peligro-nueva"
                value={form.tipoPeligro}
                onChange={(option) => handleChange('tipoPeligro', option)}
                disabled={loading}
              />
              {errors.tipoPeligro && (
                <p className="mt-1 text-xs text-red-600">{errors.tipoPeligro}</p>
              )}
            </div>

            <div>
              <label htmlFor="fecha-emergencia-nueva" className={labelClassName}>
                Fecha de emergencia
              </label>
              <input
                id="fecha-emergencia-nueva"
                type="date"
                value={form.fecha_emergencia}
                onChange={(event) => handleChange('fecha_emergencia', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
              {errors.fecha_emergencia && (
                <p className="mt-1 text-xs text-red-600">{errors.fecha_emergencia}</p>
              )}
            </div>

            <div>
              <label htmlFor="hora-ocurrencia-nueva" className={labelClassName}>
                Hora estimada
              </label>
              <input
                id="hora-ocurrencia-nueva"
                type="time"
                value={form.hora_ocurrencia_estimada}
                onChange={(event) => handleChange('hora_ocurrencia_estimada', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
            </div>
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
    </div>
  )
}
