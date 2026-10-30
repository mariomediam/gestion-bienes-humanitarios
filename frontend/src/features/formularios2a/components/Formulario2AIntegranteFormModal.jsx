import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import CatalogoSelect from '@features/formularios2a/components/CatalogoSelect'
import PersonaFormModal from '@features/formularios2a/components/PersonaFormModal'
import PersonaSelect, { etiquetaPersona } from '@features/formularios2a/components/PersonaSelect'

// DDL check CK_f2a_integrante_grado allows grado_lesion_id only for this id.
const TIPO_DANIO_PERMITE_GRADO = 1

const EMPTY_FORM = {
  persona: null,
  rol_familiar: null,
  edad: '',
  condicion_persona: null,
  tipo_danio_personal: null,
  grado_lesion: null,
  gestante_semanas: '',
  tipo_discapacidad: null,
  enfermedad_cronica: null,
}

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'text-xs font-medium text-[#1e3064]'

const accionLabelClassName =
  'shrink-0 text-xs font-medium text-[#1e3064] underline decoration-[#1e3064]/40 underline-offset-2 hover:decoration-[#1e3064] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#1e3064] rounded-sm disabled:cursor-not-allowed disabled:opacity-50'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function textoCampo(value) {
  if (value === null || value === undefined) return ''
  return String(value)
}

function opcionCatalogo(id, nombre) {
  if (id === null || id === undefined) return null
  return {
    value: id,
    label: nombre ?? '',
  }
}

function formFromIntegrante(integrante) {
  return {
    persona: {
      value: integrante.persona_id,
      label: etiquetaPersona(integrante),
    },
    rol_familiar: opcionCatalogo(integrante.rol_familiar_id, integrante.rol_familiar_nombre),
    edad: textoCampo(integrante.edad),
    condicion_persona: opcionCatalogo(
      integrante.condicion_persona_id,
      integrante.condicion_persona_nombre,
    ),
    tipo_danio_personal: opcionCatalogo(
      integrante.tipo_danio_personal_id,
      integrante.tipo_danio_personal_nombre,
    ),
    grado_lesion: opcionCatalogo(integrante.grado_lesion_id, integrante.grado_lesion_nombre),
    gestante_semanas: textoCampo(integrante.gestante_semanas),
    tipo_discapacidad: opcionCatalogo(
      integrante.tipo_discapacidad_id,
      integrante.tipo_discapacidad_nombre,
    ),
    enfermedad_cronica: opcionCatalogo(
      integrante.enfermedad_cronica_id,
      integrante.enfermedad_cronica_nombre,
    ),
  }
}

function edadEnAnios(fechaNacimiento, hoy = new Date()) {
  if (!fechaNacimiento) return null
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(fechaNacimiento))
  if (!match) return null

  const anio = Number(match[1])
  const mes = Number(match[2])
  const dia = Number(match[3])
  let edad = hoy.getFullYear() - anio
  const mesHoy = hoy.getMonth() + 1
  const diaHoy = hoy.getDate()
  if (mesHoy < mes || (mesHoy === mes && diaHoy < dia)) {
    edad -= 1
  }
  if (edad < 0 || !Number.isSafeInteger(edad)) return null
  return edad
}

function parseEntero(value) {
  const texto = value.trim()
  if (!/^\d+$/.test(texto)) return null
  const numero = Number(texto)
  if (!Number.isSafeInteger(numero)) return null
  return numero
}

function validate(form) {
  const errors = {}

  if (!form.persona) {
    errors.persona = 'El campo persona_id es obligatorio'
  }

  if (!form.rol_familiar) {
    errors.rol_familiar = 'El campo rol_familiar_id es obligatorio'
  }

  if (!form.edad.trim()) {
    errors.edad = 'El campo edad es obligatorio'
  } else {
    const edad = parseEntero(form.edad)
    if (edad === null) {
      errors.edad = 'El campo edad debe ser un número entero'
    } else if (edad < 0 || edad > 130) {
      errors.edad = 'El campo edad debe estar entre 0 y 130'
    }
  }

  if (!form.condicion_persona) {
    errors.condicion_persona = 'El campo condicion_persona_id es obligatorio'
  }

  const semanasTexto = form.gestante_semanas.trim()
  if (semanasTexto) {
    const semanas = parseEntero(form.gestante_semanas)
    if (semanas === null) {
      errors.gestante_semanas = 'El campo gestante_semanas debe ser un número entero'
    } else if (semanas < 1 || semanas > 45) {
      errors.gestante_semanas = 'El campo gestante_semanas debe estar entre 1 y 45'
    }
  }

  if (form.grado_lesion && form.tipo_danio_personal?.value !== TIPO_DANIO_PERMITE_GRADO) {
    errors.grado_lesion =
      'El campo grado_lesion_id solo puede enviarse cuando tipo_danio_personal_id es 1'
  }

  return errors
}

function Campo({ id, label, error, children, className = '', accion = null }) {
  return (
    <div className={`min-w-0 ${className}`}>
      <div className="mb-1 flex items-center justify-between gap-3">
        <label htmlFor={id} className={labelClassName}>
          {label}
        </label>
        {accion}
      </div>
      {children}
      {error && <p className="mt-1 text-xs text-red-600">{error}</p>}
    </div>
  )
}

export default function Formulario2AIntegranteFormModal({
  isOpen,
  familiaId,
  integrante = null,
  onClose,
  onSaved,
}) {
  const isEdit = integrante !== null
  const [form, setForm] = useState(() =>
    integrante ? formFromIntegrante(integrante) : EMPTY_FORM,
  )
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [crearPersonaAbierto, setCrearPersonaAbierto] = useState(false)

  useEffect(() => {
    if (!isOpen) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape' && !loading && !crearPersonaAbierto) {
        setForm(EMPTY_FORM)
        setErrors({})
        onClose()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, loading, crearPersonaAbierto, onClose])

  if (!isOpen) return null

  function handleChange(name, value) {
    setForm((current) => ({ ...current, [name]: value }))
    setErrors((current) => ({
      ...current,
      [name]: '',
      ...(name === 'tipo_danio_personal' ? { grado_lesion: '' } : {}),
    }))
  }

  function handlePersonaChange(option) {
    const edad = option ? edadEnAnios(option.fecha_nacimiento) : null
    const edadTexto = edad === null ? (option ? '' : null) : String(edad)
    setForm((current) => ({
      ...current,
      persona: option,
      ...(edadTexto === null ? {} : { edad: edadTexto }),
    }))
    setErrors((current) => ({
      ...current,
      persona: '',
      ...(edadTexto === null ? {} : { edad: '' }),
    }))
  }

  function handleClose() {
    if (loading) return
    setCrearPersonaAbierto(false)
    setForm(EMPTY_FORM)
    setErrors({})
    onClose()
  }

  function cerrarTrasPersona() {
    setCrearPersonaAbierto(false)
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
      persona_id: form.persona.value,
      rol_familiar_id: form.rol_familiar.value,
      edad: parseEntero(form.edad),
      condicion_persona_id: form.condicion_persona.value,
    }

    if (!isEdit) payload.familia_id = familiaId

    if (form.tipo_danio_personal) {
      payload.tipo_danio_personal_id = form.tipo_danio_personal.value
    }
    if (form.grado_lesion) {
      payload.grado_lesion_id = form.grado_lesion.value
    }
    const semanas = form.gestante_semanas.trim()
    if (semanas) {
      payload.gestante_semanas = parseEntero(form.gestante_semanas)
    }
    if (form.tipo_discapacidad) {
      payload.tipo_discapacidad_id = form.tipo_discapacidad.value
    }
    if (form.enfermedad_cronica) {
      payload.enfermedad_cronica_id = form.enfermedad_cronica.value
    }

    setLoading(true)
    try {
      const saved = isEdit
        ? await sgbhApi.actualizarIntegrante(integrante.integrante_id, payload)
        : await sgbhApi.crearIntegrante(payload)
      toast.success(
        isEdit ? 'Integrante modificado correctamente' : 'Integrante registrado correctamente',
      )
      setForm(EMPTY_FORM)
      setErrors({})
      onSaved(saved)
    } catch (error) {
      toast.error(
        getErrorMessage(
          error,
          isEdit ? 'No se pudo modificar el integrante' : 'No se pudo registrar el integrante',
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {!crearPersonaAbierto && createPortal(
    <div
      className="fixed inset-0 z-50 grid p-4"
      style={{ gridTemplateRows: 'minmax(0, 1fr)', alignItems: 'center', justifyItems: 'center' }}
    >
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-integrante"
        onClick={(event) => event.stopPropagation()}
        className="formulario-2a-scroll relative z-10 w-full max-w-2xl rounded-lg bg-white shadow-xl"
        style={{ maxHeight: '100%', minHeight: 0, overflowY: 'scroll' }}
      >
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4">
          <h2 id="titulo-integrante" className="text-lg font-semibold text-[#1e3064]">
            {isEdit ? 'Modificar integrante' : 'Agregar integrante'}
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
            <Campo
              id="persona-integrante"
              label="Persona"
              error={errors.persona}
              className="sm:col-span-2"
              accion={
                <button
                  type="button"
                  onClick={() => setCrearPersonaAbierto(true)}
                  disabled={loading}
                  className={accionLabelClassName}
                >
                  Crear persona
                </button>
              }
            >
              <PersonaSelect
                inputId="persona-integrante"
                value={form.persona}
                onChange={handlePersonaChange}
                disabled={loading}
              />
            </Campo>

            <Campo id="rol-familiar-integrante" label="Rol familiar" error={errors.rol_familiar}>
              <CatalogoSelect
                inputId="rol-familiar-integrante"
                value={form.rol_familiar}
                onChange={(option) => handleChange('rol_familiar', option)}
                disabled={loading}
                cargar={sgbhApi.getRolesFamiliares}
                idKey="rol_familiar_id"
                placeholder="Seleccione un rol familiar"
                mensajeVacio="No se encontraron roles familiares"
                mensajeError="No se pudo obtener el catálogo de roles familiares"
              />
            </Campo>

            <Campo id="edad-integrante" label="Edad" error={errors.edad}>
              <input
                id="edad-integrante"
                type="text"
                inputMode="numeric"
                value={form.edad}
                onChange={(event) => handleChange('edad', event.target.value)}
                maxLength={3}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo
              id="condicion-persona-integrante"
              label="Condición de persona"
              error={errors.condicion_persona}
              className="sm:col-span-2"
            >
              <CatalogoSelect
                inputId="condicion-persona-integrante"
                value={form.condicion_persona}
                onChange={(option) => handleChange('condicion_persona', option)}
                disabled={loading}
                cargar={sgbhApi.getCondicionesPersona}
                idKey="condicion_persona_id"
                placeholder="Seleccione una condición de persona"
                mensajeVacio="No se encontraron condiciones de persona"
                mensajeError="No se pudo obtener el catálogo de condiciones de persona"
              />
            </Campo>

            <Campo
              id="tipo-danio-personal-integrante"
              label="Tipo de daño personal"
              error={errors.tipo_danio_personal}
            >
              <CatalogoSelect
                inputId="tipo-danio-personal-integrante"
                value={form.tipo_danio_personal}
                onChange={(option) => handleChange('tipo_danio_personal', option)}
                disabled={loading}
                cargar={sgbhApi.getTiposDanioPersonal}
                idKey="tipo_danio_personal_id"
                placeholder="Seleccione un tipo de daño personal"
                mensajeVacio="No se encontraron tipos de daño personal"
                mensajeError="No se pudo obtener el catálogo de tipos de daño personal"
              />
            </Campo>

            <Campo id="grado-lesion-integrante" label="Grado de lesión" error={errors.grado_lesion}>
              <CatalogoSelect
                inputId="grado-lesion-integrante"
                value={form.grado_lesion}
                onChange={(option) => handleChange('grado_lesion', option)}
                disabled={loading}
                cargar={sgbhApi.getGradosLesion}
                idKey="grado_lesion_id"
                placeholder="Seleccione un grado de lesión"
                mensajeVacio="No se encontraron grados de lesión"
                mensajeError="No se pudo obtener el catálogo de grados de lesión"
              />
            </Campo>

            <Campo
              id="gestante-semanas-integrante"
              label="Semanas de gestación"
              error={errors.gestante_semanas}
            >
              <input
                id="gestante-semanas-integrante"
                type="text"
                inputMode="numeric"
                value={form.gestante_semanas}
                onChange={(event) => handleChange('gestante_semanas', event.target.value)}
                maxLength={2}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo
              id="tipo-discapacidad-integrante"
              label="Tipo de discapacidad"
              error={errors.tipo_discapacidad}
            >
              <CatalogoSelect
                inputId="tipo-discapacidad-integrante"
                value={form.tipo_discapacidad}
                onChange={(option) => handleChange('tipo_discapacidad', option)}
                disabled={loading}
                cargar={sgbhApi.getTiposDiscapacidad}
                idKey="tipo_discapacidad_id"
                placeholder="Seleccione un tipo de discapacidad"
                mensajeVacio="No se encontraron tipos de discapacidad"
                mensajeError="No se pudo obtener el catálogo de tipos de discapacidad"
              />
            </Campo>

            <Campo
              id="enfermedad-cronica-integrante"
              label="Enfermedad crónica"
              error={errors.enfermedad_cronica}
              className="sm:col-span-2"
            >
              <CatalogoSelect
                inputId="enfermedad-cronica-integrante"
                value={form.enfermedad_cronica}
                onChange={(option) => handleChange('enfermedad_cronica', option)}
                disabled={loading}
                cargar={sgbhApi.getEnfermedadesCronicas}
                idKey="enfermedad_cronica_id"
                placeholder="Seleccione una enfermedad crónica"
                mensajeVacio="No se encontraron enfermedades crónicas"
                mensajeError="No se pudo obtener el catálogo de enfermedades crónicas"
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
      )}

      <PersonaFormModal
        isOpen={crearPersonaAbierto}
        onClose={cerrarTrasPersona}
        onSaved={cerrarTrasPersona}
      />
    </>
  )
}
