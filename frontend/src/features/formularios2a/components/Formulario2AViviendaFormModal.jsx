import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import CatalogoSelect from '@features/formularios2a/components/CatalogoSelect'

const NUMERO_LOTE_MAX = 50

const EMPTY_FORM = {
  numero_lote: '',
  tenencia_propia: '',
  tipo_uso_instalacion: null,
  condicion_vivienda: null,
  material_techo: null,
  material_pared: null,
  material_piso: null,
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

function formFromVivienda(vivienda) {
  let tenenciaPropia = ''
  if (vivienda.tenencia_propia === true) tenenciaPropia = '1'
  if (vivienda.tenencia_propia === false) tenenciaPropia = '0'

  return {
    numero_lote: textoCampo(vivienda.numero_lote),
    tenencia_propia: tenenciaPropia,
    tipo_uso_instalacion: opcionCatalogo(
      vivienda.tipo_uso_instalacion_id,
      vivienda.tipo_uso_instalacion_nombre,
    ),
    condicion_vivienda: opcionCatalogo(
      vivienda.condicion_vivienda_id,
      vivienda.condicion_vivienda_nombre,
    ),
    material_techo: opcionCatalogo(vivienda.material_techo_id, vivienda.material_techo_nombre),
    material_pared: opcionCatalogo(vivienda.material_pared_id, vivienda.material_pared_nombre),
    material_piso: opcionCatalogo(vivienda.material_piso_id, vivienda.material_piso_nombre),
  }
}

function validate(form) {
  const errors = {}
  const numeroLote = form.numero_lote.trim()

  if (!numeroLote) {
    errors.numero_lote = 'El campo numero_lote es obligatorio'
  } else if (numeroLote.length > NUMERO_LOTE_MAX) {
    errors.numero_lote = 'El campo numero_lote no debe superar 50 caracteres'
  }

  if (!form.tipo_uso_instalacion) {
    errors.tipo_uso_instalacion = 'El campo tipo_uso_instalacion_id es obligatorio'
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

export default function Formulario2AViviendaFormModal({
  isOpen,
  formulario2aId,
  vivienda = null,
  onClose,
  onSaved,
}) {
  const isEdit = vivienda !== null
  const [form, setForm] = useState(() =>
    vivienda ? formFromVivienda(vivienda) : EMPTY_FORM,
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
    const nextErrors = validate(form)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    const payload = {
      numero_lote: form.numero_lote.trim(),
      tipo_uso_instalacion_id: form.tipo_uso_instalacion.value,
    }

    if (!isEdit) payload.formulario_2a_id = formulario2aId

    if (form.tenencia_propia === '1') payload.tenencia_propia = true
    if (form.tenencia_propia === '0') payload.tenencia_propia = false
    if (form.condicion_vivienda) {
      payload.condicion_vivienda_id = form.condicion_vivienda.value
    }
    if (form.material_techo) payload.material_techo_id = form.material_techo.value
    if (form.material_pared) payload.material_pared_id = form.material_pared.value
    if (form.material_piso) payload.material_piso_id = form.material_piso.value

    setLoading(true)
    try {
      const saved = isEdit
        ? await sgbhApi.actualizarVivienda(vivienda.vivienda_id, payload)
        : await sgbhApi.crearVivienda(payload)
      toast.success(
        isEdit ? 'Vivienda modificada correctamente' : 'Vivienda registrada correctamente',
      )
      setForm(EMPTY_FORM)
      setErrors({})
      onSaved(saved)
    } catch (error) {
      toast.error(
        getErrorMessage(
          error,
          isEdit ? 'No se pudo modificar la vivienda' : 'No se pudo registrar la vivienda',
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
        aria-labelledby="titulo-vivienda"
        onClick={(event) => event.stopPropagation()}
        className="formulario-2a-scroll relative z-10 w-full max-w-2xl rounded-lg bg-white shadow-xl"
        style={{ maxHeight: '100%', minHeight: 0, overflowY: 'scroll' }}
      >
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-gray-200 bg-white px-6 py-4">
          <h2 id="titulo-vivienda" className="text-lg font-semibold text-[#1e3064]">
            {isEdit ? 'Modificar vivienda' : 'Agregar vivienda'}
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
            <Campo id="numero-lote-vivienda" label="Número de lote" error={errors.numero_lote}>
              <input
                id="numero-lote-vivienda"
                type="text"
                value={form.numero_lote}
                onChange={(event) => handleChange('numero_lote', event.target.value)}
                maxLength={NUMERO_LOTE_MAX}
                disabled={loading}
                className={inputClassName}
              />
            </Campo>

            <Campo id="tenencia-propia-vivienda" label="Tenencia propia" error={errors.tenencia_propia}>
              <select
                id="tenencia-propia-vivienda"
                value={form.tenencia_propia}
                onChange={(event) => handleChange('tenencia_propia', event.target.value)}
                disabled={loading}
                className={inputClassName}
              >
                <option value="">Seleccione</option>
                <option value="1">Sí</option>
                <option value="0">No</option>
              </select>
            </Campo>

            <Campo
              id="tipo-uso-instalacion-vivienda"
              label="Tipo de uso de instalación"
              error={errors.tipo_uso_instalacion}
              className="sm:col-span-2"
            >
              <CatalogoSelect
                inputId="tipo-uso-instalacion-vivienda"
                value={form.tipo_uso_instalacion}
                onChange={(option) => handleChange('tipo_uso_instalacion', option)}
                disabled={loading}
                cargar={sgbhApi.getTiposUsoInstalacion}
                idKey="tipo_uso_instalacion_id"
                placeholder="Seleccione un tipo de uso de instalación"
                mensajeVacio="No se encontraron tipos de uso de instalación"
                mensajeError="No se pudo obtener el catálogo de tipos de uso de instalación"
              />
            </Campo>

            <Campo
              id="condicion-vivienda"
              label="Condición de vivienda"
              error={errors.condicion_vivienda}
              className="sm:col-span-2"
            >
              <CatalogoSelect
                inputId="condicion-vivienda"
                value={form.condicion_vivienda}
                onChange={(option) => handleChange('condicion_vivienda', option)}
                disabled={loading}
                cargar={sgbhApi.getCondicionesVivienda}
                idKey="condicion_vivienda_id"
                placeholder="Seleccione una condición de vivienda"
                mensajeVacio="No se encontraron condiciones de vivienda"
                mensajeError="No se pudo obtener el catálogo de condiciones de vivienda"
              />
            </Campo>

            <Campo id="material-techo-vivienda" label="Material de techo" error={errors.material_techo}>
              <CatalogoSelect
                inputId="material-techo-vivienda"
                value={form.material_techo}
                onChange={(option) => handleChange('material_techo', option)}
                disabled={loading}
                cargar={sgbhApi.getMaterialesTecho}
                idKey="material_techo_id"
                placeholder="Seleccione un material de techo"
                mensajeVacio="No se encontraron materiales de techo"
                mensajeError="No se pudo obtener el catálogo de materiales de techo"
              />
            </Campo>

            <Campo id="material-pared-vivienda" label="Material de pared" error={errors.material_pared}>
              <CatalogoSelect
                inputId="material-pared-vivienda"
                value={form.material_pared}
                onChange={(option) => handleChange('material_pared', option)}
                disabled={loading}
                cargar={sgbhApi.getMaterialesPared}
                idKey="material_pared_id"
                placeholder="Seleccione un material de pared"
                mensajeVacio="No se encontraron materiales de pared"
                mensajeError="No se pudo obtener el catálogo de materiales de pared"
              />
            </Campo>

            <Campo id="material-piso-vivienda" label="Material de piso" error={errors.material_piso} className="sm:col-span-2">
              <CatalogoSelect
                inputId="material-piso-vivienda"
                value={form.material_piso}
                onChange={(option) => handleChange('material_piso', option)}
                disabled={loading}
                cargar={sgbhApi.getMaterialesPiso}
                idKey="material_piso_id"
                placeholder="Seleccione un material de piso"
                mensajeVacio="No se encontraron materiales de piso"
                mensajeError="No se pudo obtener el catálogo de materiales de piso"
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
