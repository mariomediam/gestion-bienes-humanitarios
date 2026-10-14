import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import CatalogoSelect from '@features/formularios2a/components/CatalogoSelect'

const CANTIDAD_MAX = 2147483647
const OBSERVACION_MAX = 500

const EMPTY_FORM = {
  categoria: null,
  tipo_medio_vida: null,
  cantidad: '',
  observacion: '',
}

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

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

function formFromMedioVida(medioVida) {
  return {
    categoria: opcionCatalogo(
      medioVida.categoria_medio_vida_id,
      medioVida.categoria_medio_vida_nombre,
    ),
    tipo_medio_vida: opcionCatalogo(
      medioVida.tipo_medio_vida_id,
      medioVida.tipo_medio_vida_nombre,
    ),
    cantidad: textoCampo(medioVida.cantidad),
    observacion: textoCampo(medioVida.observacion),
  }
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

  if (!form.categoria) {
    errors.categoria = 'El campo categoria_medio_vida_id es obligatorio'
  }

  if (!form.tipo_medio_vida) {
    errors.tipo_medio_vida = 'El campo tipo_medio_vida_id es obligatorio'
  }

  if (!form.cantidad.trim()) {
    errors.cantidad = 'El campo cantidad es obligatorio'
  } else {
    const cantidad = parseEntero(form.cantidad)
    if (cantidad === null || cantidad > CANTIDAD_MAX) {
      errors.cantidad = 'El campo cantidad debe ser un número entero'
    } else if (cantidad < 1) {
      errors.cantidad = 'El campo cantidad debe ser mayor que cero'
    }
  }

  if (form.observacion.trim().length > OBSERVACION_MAX) {
    errors.observacion = 'El campo observacion no debe superar 500 caracteres'
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

export default function Formulario2AMedioVidaFormModal({
  isOpen,
  familiaId,
  medioVida = null,
  onClose,
  onSaved,
}) {
  const isEdit = medioVida !== null
  const [form, setForm] = useState(() =>
    medioVida ? formFromMedioVida(medioVida) : EMPTY_FORM,
  )
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
    setErrors((current) => ({ ...current, [name]: '' }))
  }

  function handleCategoriaChange(option) {
    setForm((current) => ({
      ...current,
      categoria: option,
      tipo_medio_vida: null,
    }))
    setErrors((current) => ({
      ...current,
      categoria: '',
      tipo_medio_vida: '',
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
      tipo_medio_vida_id: form.tipo_medio_vida.value,
      cantidad: parseEntero(form.cantidad),
    }

    if (!isEdit) payload.familia_id = familiaId

    const observacion = form.observacion.trim()
    if (observacion) payload.observacion = observacion

    setLoading(true)
    try {
      const saved = isEdit
        ? await sgbhApi.actualizarMedioVida(medioVida.medio_vida_id, payload)
        : await sgbhApi.crearMedioVida(payload)
      toast.success(
        isEdit
          ? 'Medio de vida modificado correctamente'
          : 'Medio de vida registrado correctamente',
      )
      setForm(EMPTY_FORM)
      setErrors({})
      onSaved(saved)
    } catch (error) {
      toast.error(
        getErrorMessage(
          error,
          isEdit
            ? 'No se pudo modificar el medio de vida'
            : 'No se pudo registrar el medio de vida',
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  const filtrosTipo = form.categoria
    ? { categoria_medio_vida_id: form.categoria.value }
    : undefined

  return createPortal(
    <div
      className="fixed inset-0 z-50 grid p-4"
      style={{ gridTemplateRows: 'minmax(0, 1fr)', alignItems: 'center', justifyItems: 'center' }}
    >
      <div className="absolute inset-0 bg-black/50" onClick={handleClose} />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="titulo-medio-vida"
        onClick={(event) => event.stopPropagation()}
        className="formulario-2a-scroll relative z-10 w-full max-w-2xl rounded-lg bg-white shadow-xl"
        style={{ maxHeight: '100%', minHeight: 0, overflowY: 'scroll' }}
      >
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4">
          <h2 id="titulo-medio-vida" className="text-lg font-semibold text-[#1e3064]">
            {isEdit ? 'Modificar medio de vida' : 'Agregar medio de vida'}
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
              id="categoria-medio-vida"
              label="Categoría de medio de vida"
              error={errors.categoria}
              className="sm:col-span-2"
            >
              <CatalogoSelect
                inputId="categoria-medio-vida"
                value={form.categoria}
                onChange={handleCategoriaChange}
                disabled={loading}
                cargar={sgbhApi.getCategoriasMediosVida}
                idKey="categoria_medio_vida_id"
                placeholder="Seleccione una categoría de medio de vida"
                mensajeVacio="No se encontraron categorías de medios de vida"
                mensajeError="No se pudo obtener el catálogo de categorías de medios de vida"
              />
            </Campo>

            <Campo
              id="tipo-medio-vida"
              label="Tipo de medio de vida"
              error={errors.tipo_medio_vida}
              className="sm:col-span-2"
            >
              <CatalogoSelect
                inputId="tipo-medio-vida"
                value={form.tipo_medio_vida}
                onChange={(option) => handleChange('tipo_medio_vida', option)}
                disabled={loading}
                habilitado={Boolean(form.categoria)}
                filtros={filtrosTipo}
                cargar={sgbhApi.getTiposMediosVida}
                idKey="tipo_medio_vida_id"
                placeholder={
                  form.categoria
                    ? 'Seleccione un tipo de medio de vida'
                    : 'Seleccione una categoría de medio de vida'
                }
                mensajeVacio="No se encontraron tipos de medio de vida"
                mensajeError="No se pudo obtener el catálogo de tipos de medio de vida"
              />
            </Campo>

            <Campo id="cantidad-medio-vida" label="Cantidad" error={errors.cantidad}>
              <input
                id="cantidad-medio-vida"
                type="text"
                inputMode="numeric"
                value={form.cantidad}
                onChange={(event) => handleChange('cantidad', event.target.value)}
                maxLength={10}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo
              id="observacion-medio-vida"
              label="Observación"
              error={errors.observacion}
              className="sm:col-span-2"
            >
              <textarea
                id="observacion-medio-vida"
                value={form.observacion}
                onChange={(event) => handleChange('observacion', event.target.value)}
                maxLength={OBSERVACION_MAX}
                rows={3}
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
