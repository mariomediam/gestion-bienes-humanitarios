import { useEffect, useState } from 'react'
import Select from 'react-select'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

const EMPTY_FORM = {
  categoriaBien: null,
  unidadMedida: null,
  codigo: '',
  nombre: '',
  esta_activo: true,
  visible_planilla: true,
}

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

const selectStyles = {
  control: (base, state) => ({
    ...base,
    minHeight: 38,
    borderColor: state.isFocused ? '#1e3064' : '#d1d5db',
    boxShadow: state.isFocused ? '0 0 0 2px #1e3064' : 'none',
    backgroundColor: state.isDisabled ? '#f9fafb' : base.backgroundColor,
    '&:hover': {
      borderColor: state.isFocused ? '#1e3064' : '#d1d5db',
    },
    fontSize: '0.875rem',
  }),
  menu: (base) => ({
    ...base,
    zIndex: 60,
    fontSize: '0.875rem',
  }),
  menuPortal: (base) => ({
    ...base,
    zIndex: 60,
  }),
  placeholder: (base) => ({
    ...base,
    color: '#9ca3af',
  }),
}

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function formFromBien(bien) {
  return {
    categoriaBien: bien.categoria_bien_id
      ? {
          value: bien.categoria_bien_id,
          label: bien.categoria_bien_nombre ?? '',
        }
      : null,
    unidadMedida: bien.unidad_medida_id
      ? {
          value: bien.unidad_medida_id,
          label: bien.unidad_medida_nombre ?? '',
        }
      : null,
    codigo: bien.codigo ?? '',
    nombre: bien.nombre ?? '',
    esta_activo: bien.esta_activo,
    visible_planilla: bien.visible_planilla,
  }
}

function opcionSeleccionada(opciones, value) {
  if (value == null) return null
  return opciones.find((option) => option.value === value.value) ?? value
}

export default function BienFormModal({ isOpen, onClose, onSaved, bien = null }) {
  const [form, setForm] = useState(() => (bien ? formFromBien(bien) : EMPTY_FORM))
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [categorias, setCategorias] = useState([])
  const [unidades, setUnidades] = useState([])
  const [cargandoCategorias, setCargandoCategorias] = useState(false)
  const [cargandoUnidades, setCargandoUnidades] = useState(false)
  const isEdit = bien !== null

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

  useEffect(() => {
    if (!isOpen) return undefined

    let active = true
    setCargandoCategorias(true)
    setCargandoUnidades(true)

    sgbhApi
      .getCategoriasBienes()
      .then((rows) => {
        if (!active) return
        setCategorias(
          rows.map((row) => ({
            value: row.categoria_bien_id,
            label: row.nombre ?? '',
          })),
        )
      })
      .catch((error) => {
        if (active) {
          toast.error(
            getErrorMessage(error, 'No se pudo obtener el catálogo de categorías de bienes'),
          )
        }
      })
      .finally(() => {
        if (active) setCargandoCategorias(false)
      })

    sgbhApi
      .getUnidadesMedida()
      .then((rows) => {
        if (!active) return
        setUnidades(
          rows.map((row) => ({
            value: row.unidad_medida_id,
            label: row.nombre ?? '',
          })),
        )
      })
      .catch((error) => {
        if (active) {
          toast.error(
            getErrorMessage(error, 'No se pudo obtener el catálogo de unidades de medida'),
          )
        }
      })
      .finally(() => {
        if (active) setCargandoUnidades(false)
      })

    return () => {
      active = false
    }
  }, [isOpen])

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
    if (!form.categoriaBien) {
      nextErrors.categoriaBien = 'La categoría es obligatoria'
    }
    if (!form.unidadMedida) {
      nextErrors.unidadMedida = 'La unidad de medida es obligatoria'
    }
    if (!isEdit && !form.codigo.trim()) {
      nextErrors.codigo = 'El código es obligatorio'
    }
    if (!form.nombre.trim()) {
      nextErrors.nombre = 'El nombre es obligatorio'
    }
    return nextErrors
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const nextErrors = validate()
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    const payload = {
      categoria_bien_id: form.categoriaBien.value,
      unidad_medida_id: form.unidadMedida.value,
      nombre: form.nombre.trim(),
      esta_activo: form.esta_activo,
      visible_planilla: form.visible_planilla,
    }
    if (!isEdit) {
      payload.codigo = form.codigo.trim()
    }

    setLoading(true)
    try {
      const saved = isEdit
        ? await sgbhApi.actualizarBien(bien.bien_id, payload)
        : await sgbhApi.crearBien(payload)
      toast.success(isEdit ? 'Bien modificado correctamente' : 'Bien registrado correctamente')
      setForm(EMPTY_FORM)
      setErrors({})
      onSaved(saved)
    } catch (error) {
      toast.error(
        getErrorMessage(
          error,
          isEdit ? 'No se pudo modificar el bien' : 'No se pudo registrar el bien',
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
        aria-labelledby="titulo-bien"
        className="relative bg-white rounded-lg shadow-xl w-full max-w-2xl mx-4"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h2 id="titulo-bien" className="text-lg font-semibold text-[#1e3064]">
            {isEdit ? 'Modificar bien' : 'Agregar nuevo bien'}
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
              <label htmlFor="codigo-bien" className={labelClassName}>
                Código
              </label>
              <input
                id="codigo-bien"
                type="text"
                value={form.codigo}
                onChange={(event) => handleChange('codigo', event.target.value)}
                maxLength={50}
                disabled={loading || isEdit}
                className={inputClassName}
              />
              {errors.codigo && (
                <p className="mt-1 text-xs text-red-600">{errors.codigo}</p>
              )}
            </div>

            <div>
              <label htmlFor="nombre-bien-formulario" className={labelClassName}>
                Nombre
              </label>
              <input
                id="nombre-bien-formulario"
                type="text"
                value={form.nombre}
                onChange={(event) => handleChange('nombre', event.target.value)}
                maxLength={250}
                disabled={loading}
                className={inputClassName}
              />
              {errors.nombre && (
                <p className="mt-1 text-xs text-red-600">{errors.nombre}</p>
              )}
            </div>

            <div>
              <label htmlFor="categoria-bien" className={labelClassName}>
                Categoría
              </label>
              <Select
                inputId="categoria-bien"
                instanceId="categoria-bien"
                value={opcionSeleccionada(categorias, form.categoriaBien)}
                onChange={(option) => handleChange('categoriaBien', option)}
                options={categorias}
                isDisabled={loading || cargandoCategorias}
                isLoading={cargandoCategorias}
                isClearable
                menuPortalTarget={document.body}
                menuPosition="fixed"
                placeholder="Seleccione una categoría"
                loadingMessage={() => 'Cargando...'}
                noOptionsMessage={() => 'No hay categorías'}
                styles={selectStyles}
                autoFocus
              />
              {errors.categoriaBien && (
                <p className="mt-1 text-xs text-red-600">{errors.categoriaBien}</p>
              )}
            </div>

            <div>
              <label htmlFor="unidad-medida-bien" className={labelClassName}>
                Unidad de medida
              </label>
              <Select
                inputId="unidad-medida-bien"
                instanceId="unidad-medida-bien"
                value={opcionSeleccionada(unidades, form.unidadMedida)}
                onChange={(option) => handleChange('unidadMedida', option)}
                options={unidades}
                isDisabled={loading || cargandoUnidades}
                isLoading={cargandoUnidades}
                isClearable
                menuPortalTarget={document.body}
                menuPosition="fixed"
                placeholder="Seleccione una unidad de medida"
                loadingMessage={() => 'Cargando...'}
                noOptionsMessage={() => 'No hay unidades de medida'}
                styles={selectStyles}
              />
              {errors.unidadMedida && (
                <p className="mt-1 text-xs text-red-600">{errors.unidadMedida}</p>
              )}
            </div>

           

            <div>
              <label htmlFor="bien-esta-activo" className={labelClassName}>
                Activo
              </label>
              <input
                id="bien-esta-activo"
                type="checkbox"
                checked={form.esta_activo}
                onChange={(event) => handleChange('esta_activo', event.target.checked)}
                disabled={loading}
                className="mt-2 h-4 w-4 accent-[#1e3064]"
              />
            </div>

            <div>
              <label htmlFor="bien-visible-planilla" className={labelClassName}>
                Visible en planilla
              </label>
              <input
                id="bien-visible-planilla"
                type="checkbox"
                checked={form.visible_planilla}
                onChange={(event) => handleChange('visible_planilla', event.target.checked)}
                disabled={loading}
                className="mt-2 h-4 w-4 accent-[#1e3064]"
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
