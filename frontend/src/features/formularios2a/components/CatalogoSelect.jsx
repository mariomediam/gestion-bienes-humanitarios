import { useEffect, useRef, useState } from 'react'
import Select from 'react-select'
import { toast } from 'sonner'

const selectStyles = {
  control: (base, state) => ({
    ...base,
    minHeight: 38,
    borderColor: state.isFocused ? '#1e3064' : '#d1d5db',
    boxShadow: state.isFocused ? '0 0 0 2px #1e3064' : 'none',
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

function etiquetaOpcion(row, incluirCodigoFormulario) {
  const nombre = row.nombre ?? ''
  if (!incluirCodigoFormulario) return nombre
  const codigo = row.codigo_formulario
  if (codigo === null || codigo === undefined || codigo === '') return nombre
  return `${codigo} - ${nombre}`
}

export default function CatalogoSelect({
  inputId,
  value,
  onChange,
  disabled,
  cargar,
  idKey,
  placeholder,
  mensajeVacio,
  mensajeError,
  onFilas,
  filtros,
  habilitado = true,
  incluirCodigoFormulario = false,
}) {
  const [options, setOptions] = useState([])
  const [loading, setLoading] = useState(habilitado)
  const onFilasRef = useRef(onFilas)
  onFilasRef.current = onFilas
  const filtrosKey = JSON.stringify(filtros ?? null)

  useEffect(() => {
    if (!habilitado) {
      setOptions([])
      setLoading(false)
      return undefined
    }

    let active = true
    setLoading(true)
    setOptions([])

    const extra = JSON.parse(filtrosKey)
    const params = { esta_activo: true }
    if (extra) Object.assign(params, extra)

    cargar(params)
      .then((rows) => {
        if (!active) return
        onFilasRef.current?.(rows)
        setOptions(
          rows.map((row) => ({
            value: row[idKey],
            label: etiquetaOpcion(row, incluirCodigoFormulario),
            codigo: row.codigo,
          })),
        )
      })
      .catch((error) => {
        if (active) {
          toast.error(getErrorMessage(error, mensajeError))
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [cargar, idKey, mensajeError, filtrosKey, habilitado, incluirCodigoFormulario])

  const selected =
    value == null
      ? value
      : (options.find((option) => option.value === value.value) ?? value)

  return (
    <Select
      inputId={inputId}
      instanceId={inputId}
      value={selected}
      onChange={onChange}
      options={options}
      isDisabled={disabled || loading || !habilitado}
      isLoading={loading}
      isClearable
      menuPortalTarget={document.body}
      menuPosition="fixed"
      placeholder={placeholder}
      loadingMessage={() => 'Cargando...'}
      noOptionsMessage={() => mensajeVacio}
      styles={selectStyles}
    />
  )
}
