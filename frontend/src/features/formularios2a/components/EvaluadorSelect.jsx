import { useEffect, useState } from 'react'
import Select from 'react-select'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

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

function nombreEvaluador(row) {
  return [row.apellido_paterno, row.apellido_materno, row.nombres].filter(Boolean).join(' ')
}

export default function EvaluadorSelect({ inputId, value, onChange, disabled }) {
  const [options, setOptions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true

    sgbhApi
      .buscarEvaluadores({ esta_activo: true })
      .then((rows) => {
        if (!active) return
        setOptions(
          rows
            .map((row) => ({
              value: row.personal_id,
              label: nombreEvaluador(row),
            }))
            .sort((left, right) => left.label.localeCompare(right.label, 'es')),
        )
      })
      .catch((error) => {
        if (active) {
          toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de evaluadores'))
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
  }, [])

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
      placeholder="Seleccione un evaluador"
      loadingMessage={() => 'Cargando...'}
      noOptionsMessage={() => 'No se encontraron evaluadores'}
      styles={selectStyles}
    />
  )
}
