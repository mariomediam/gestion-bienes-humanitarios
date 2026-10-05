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
    zIndex: 30,
    fontSize: '0.875rem',
  }),
  placeholder: (base) => ({
    ...base,
    color: '#9ca3af',
  }),
}

let distritosRequest = null

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function loadDistritosActivos() {
  if (!distritosRequest) {
    distritosRequest = sgbhApi
      .buscarDistritos({ f_activo: true })
      .then((rows) =>
        rows
          .map((row) => ({
            value: `${row.departamento_id}${row.provincia_id}${row.distrito_id}`,
            label: `${row.distrito_nombre} (${row.departamento_id}${row.provincia_id}${row.distrito_id})`,
            departamento_id: row.departamento_id,
            provincia_id: row.provincia_id,
            distrito_id: row.distrito_id,
          }))
          .sort((left, right) => left.label.localeCompare(right.label, 'es')),
      )
      .catch((error) => {
        distritosRequest = null
        throw error
      })
  }

  return distritosRequest
}

export default function DistritoSelect({ inputId, value, onChange, disabled }) {
  const [options, setOptions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true

    loadDistritosActivos()
      .then((rows) => {
        if (active) {
          setOptions(rows)
        }
      })
      .catch((error) => {
        if (active) {
          toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de distritos'))
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
      placeholder="Seleccione un distrito"
      loadingMessage={() => 'Cargando...'}
      noOptionsMessage={() => 'No se encontraron distritos'}
      styles={selectStyles}
    />
  )
}
