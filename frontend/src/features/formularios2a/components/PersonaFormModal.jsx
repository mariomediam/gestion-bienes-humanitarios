import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import CatalogoSelect from '@features/formularios2a/components/CatalogoSelect'

const OPCIONES_SEXO = [
  { value: 'M', label: 'Masculino' },
  { value: 'F', label: 'Femenino' },
  { value: 'D', label: 'Desconocido' },
]

const SEXO_DEFECTO = 'D'

const EMPTY_FORM = {
  tipo_documento: null,
  numero_documento: '',
  apellido_paterno: '',
  apellido_materno: '',
  nombres: '',
  fecha_nacimiento: '',
  sexo: SEXO_DEFECTO,
  telefono: '',
  correo: '',
}

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

const MENSAJE_DOCUMENTO =
  'Los campos tipo_documento_id y numero_documento deben enviarse juntos o ambos vacíos'

const CODIGO_DNI = 'DNI'

function codigoTipoDocumento(tipoDocumento, tiposDocumento) {
  if (!tipoDocumento) return null
  const fila = tiposDocumento.find((row) => row.tipo_documento_id === tipoDocumento.value)
  if (fila) return fila.codigo
  return tipoDocumento.codigo ?? null
}

function puedeConsultarReniec(tipoDocumento, numeroDocumento, tiposDocumento) {
  return (
    codigoTipoDocumento(tipoDocumento, tiposDocumento) === CODIGO_DNI &&
    /^\d{8}$/.test(numeroDocumento.trim())
  )
}

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function textoCampo(value) {
  if (value === null || value === undefined) return ''
  return String(value)
}

function opcionCatalogo(id, nombre, codigo) {
  if (id === null || id === undefined) return null
  return {
    value: id,
    label: nombre ?? '',
    codigo: codigo ?? null,
  }
}

function formFromPersona(persona) {
  return {
    tipo_documento: opcionCatalogo(
      persona.tipo_documento_id,
      persona.nombre_tipo_documento,
      persona.codigo_tipo_documento,
    ),
    numero_documento: textoCampo(persona.numero_documento),
    apellido_paterno: textoCampo(persona.apellido_paterno),
    apellido_materno: textoCampo(persona.apellido_materno),
    nombres: textoCampo(persona.nombres),
    fecha_nacimiento: textoCampo(persona.fecha_nacimiento),
    sexo: OPCIONES_SEXO.some((opcion) => opcion.value === persona.sexo)
      ? persona.sexo
      : SEXO_DEFECTO,
    telefono: textoCampo(persona.telefono),
    correo: textoCampo(persona.correo),
  }
}

function validarTexto(value, field, maxLength, errors) {
  const texto = value.trim()
  if (!texto) {
    errors[field] = `El campo ${field} es obligatorio`
    return
  }
  if (texto.length > maxLength) {
    errors[field] = `El campo ${field} no debe superar ${maxLength} caracteres`
  }
}

function validarTextoOpcional(value, field, maxLength, errors) {
  if (value.trim().length > maxLength) {
    errors[field] = `El campo ${field} no debe superar ${maxLength} caracteres`
  }
}

function validate(form) {
  const errors = {}

  validarTexto(form.apellido_paterno, 'apellido_paterno', 50, errors)
  validarTexto(form.apellido_materno, 'apellido_materno', 50, errors)
  validarTexto(form.nombres, 'nombres', 150, errors)
  validarTextoOpcional(form.telefono, 'telefono', 50, errors)
  validarTextoOpcional(form.correo, 'correo', 50, errors)

  if (!form.fecha_nacimiento) {
    errors.fecha_nacimiento = 'El campo fecha_nacimiento es obligatorio'
  }

  if (!OPCIONES_SEXO.some((opcion) => opcion.value === form.sexo)) {
    errors.sexo = 'El campo sexo es obligatorio'
  }

  const numero = form.numero_documento.trim()
  const tieneTipo = form.tipo_documento !== null
  const tieneNumero = numero !== ''
  if (tieneTipo !== tieneNumero) {
    if (!tieneTipo) errors.tipo_documento = MENSAJE_DOCUMENTO
    if (!tieneNumero) errors.numero_documento = MENSAJE_DOCUMENTO
  } else if (numero.length > 20) {
    errors.numero_documento = 'El campo numero_documento no debe superar 20 caracteres'
  }

  return errors
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

export default function PersonaFormModal({
  isOpen,
  persona = null,
  onClose,
  onSaved,
}) {
  const isEdit = persona !== null
  const [form, setForm] = useState(() => (persona ? formFromPersona(persona) : EMPTY_FORM))
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [tiposDocumento, setTiposDocumento] = useState([])

  useEffect(() => {
    if (!isOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !loading) onClose()
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, loading, onClose])

  if (!isOpen) return null

  function handleChange(name, value) {
    setForm((current) => ({ ...current, [name]: value }))
    setErrors((current) => ({
      ...current,
      [name]: '',
      ...(name === 'tipo_documento' || name === 'numero_documento'
        ? { tipo_documento: '', numero_documento: '' }
        : {}),
    }))
  }

  function handleClose() {
    if (loading) return
    setForm(EMPTY_FORM)
    setErrors({})
    onClose()
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const nextErrors = validate(form)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    const payload = {
      apellido_paterno: form.apellido_paterno.trim(),
      apellido_materno: form.apellido_materno.trim(),
      nombres: form.nombres.trim(),
      fecha_nacimiento: form.fecha_nacimiento,
      sexo: form.sexo,
      telefono: form.telefono.trim(),
      correo: form.correo.trim(),
    }

    const numero = form.numero_documento.trim()
    if (form.tipo_documento && numero) {
      payload.tipo_documento_id = form.tipo_documento.value
      payload.numero_documento = numero
    }

    if (isEdit) {
      payload.esta_activo = persona.esta_activo
    }

    setLoading(true)
    try {
      const saved = isEdit
        ? await sgbhApi.actualizarPersona(persona.persona_id, payload)
        : await sgbhApi.crearPersona(payload)
      toast.success(isEdit ? 'Persona modificada correctamente' : 'Persona registrada correctamente')
      setForm(EMPTY_FORM)
      setErrors({})
      onSaved(saved)
    } catch (error) {
      toast.error(
        getErrorMessage(
          error,
          isEdit ? 'No se pudo modificar la persona' : 'No se pudo registrar la persona',
        ),
      )
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
        aria-labelledby="titulo-persona"
        onClick={(event) => event.stopPropagation()}
        className="formulario-2a-scroll relative z-10 w-full max-w-2xl rounded-lg bg-white shadow-xl"
        style={{ maxHeight: '100%', minHeight: 0, overflowY: 'scroll' }}
      >
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4">
          <h2 id="titulo-persona" className="text-lg font-semibold text-[#1e3064]">
            {isEdit ? 'Modificar persona' : 'Crear persona'}
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
          <div className="grid min-w-0 grid-cols-1 gap-4 sm:grid-cols-2">
            <Campo id="tipo-documento-persona" label="Tipo de documento" error={errors.tipo_documento}>
              <CatalogoSelect
                inputId="tipo-documento-persona"
                value={form.tipo_documento}
                onChange={(option) => handleChange('tipo_documento', option)}
                disabled={loading}
                cargar={sgbhApi.getTiposDocumento}
                idKey="tipo_documento_id"
                onFilas={setTiposDocumento}
                placeholder="Seleccione un tipo de documento"
                mensajeVacio="No se encontraron tipos de documento"
                mensajeError="No se pudo obtener el catálogo de tipos de documento"
              />
            </Campo>

            <Campo
              id="numero-documento-persona"
              label="Número de documento"
              error={errors.numero_documento}
            >
              <input
                id="numero-documento-persona"
                type="text"
                value={form.numero_documento}
                onChange={(event) => handleChange('numero_documento', event.target.value)}
                maxLength={20}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <button
              type="button"
              disabled={
                loading ||
                !puedeConsultarReniec(form.tipo_documento, form.numero_documento, tiposDocumento)
              }
              className="w-full sm:col-span-2 px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-white"
            >
              Consultar RENIEC
            </button>

            <Campo
              id="apellido-paterno-persona"
              label="Apellido paterno"
              error={errors.apellido_paterno}
            >
              <input
                id="apellido-paterno-persona"
                type="text"
                value={form.apellido_paterno}
                onChange={(event) => handleChange('apellido_paterno', event.target.value)}
                maxLength={50}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo
              id="apellido-materno-persona"
              label="Apellido materno"
              error={errors.apellido_materno}
            >
              <input
                id="apellido-materno-persona"
                type="text"
                value={form.apellido_materno}
                onChange={(event) => handleChange('apellido_materno', event.target.value)}
                maxLength={50}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="nombres-persona" label="Nombres" error={errors.nombres} className="sm:col-span-2">
              <input
                id="nombres-persona"
                type="text"
                value={form.nombres}
                onChange={(event) => handleChange('nombres', event.target.value)}
                maxLength={150}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo
              id="fecha-nacimiento-persona"
              label="Fecha de nacimiento"
              error={errors.fecha_nacimiento}
            >
              <input
                id="fecha-nacimiento-persona"
                type="date"
                value={form.fecha_nacimiento}
                onChange={(event) => handleChange('fecha_nacimiento', event.target.value)}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="sexo-persona" label="Sexo" error={errors.sexo}>
              <select
                id="sexo-persona"
                value={form.sexo}
                onChange={(event) => handleChange('sexo', event.target.value)}
                disabled={loading}
                className={inputClassName}
              >
                {OPCIONES_SEXO.map((opcion) => (
                  <option key={opcion.value} value={opcion.value}>
                    {opcion.label}
                  </option>
                ))}
              </select>
            </Campo>

            <Campo id="telefono-persona" label="Teléfono" error={errors.telefono}>
              <input
                id="telefono-persona"
                type="text"
                value={form.telefono}
                onChange={(event) => handleChange('telefono', event.target.value)}
                maxLength={50}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="correo-persona" label="Correo" error={errors.correo}>
              <input
                id="correo-persona"
                type="text"
                value={form.correo}
                onChange={(event) => handleChange('correo', event.target.value)}
                maxLength={50}
                disabled={loading}
                className={inputClassName}
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
