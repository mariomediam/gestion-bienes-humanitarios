import { useEffect, useState } from 'react'
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
}) {
  const [options, setOptions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true

    cargar({ esta_activo: true })
      .then((rows) => {
        if (!active) return
        setOptions(
          rows.map((row) => ({
            value: row[idKey],
            label: row.nombre,
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
  }, [cargar, idKey, mensajeError])

  return (
    <Select
      inputId={inputId}
      instanceId={inputId}
      value={value}
      onChange={onChange}
      options={options}
      isDisabled={disabled || loading}
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
