import { useCallback, useEffect, useRef } from 'react'
import AsyncSelect from 'react-select/async'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

const SEARCH_DELAY_MS = 400

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

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function TipoPeligroSelect({ inputId, value, onChange, disabled }) {
  const timeoutRef = useRef(null)
  const requestRef = useRef(0)
  const pendingRef = useRef([])

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
      pendingRef.current.forEach((resolvePrevious) => resolvePrevious([]))
    }
  }, [])

  const loadOptions = useCallback((inputValue) => {
    pendingRef.current.forEach((resolvePrevious) => resolvePrevious([]))
    pendingRef.current = []

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    const requestId = ++requestRef.current
    const nombre = inputValue.trim()

    return new Promise((resolve) => {
      pendingRef.current.push(resolve)

      timeoutRef.current = setTimeout(async () => {
        pendingRef.current = pendingRef.current.filter((item) => item !== resolve)

        if (!nombre || requestId !== requestRef.current) {
          resolve([])
          return
        }

        try {
          const rows = await sgbhApi.getTiposPeligro({ nombre })
          if (requestId !== requestRef.current) {
            resolve([])
            return
          }
          resolve(
            rows.map((row) => ({
              value: row.tipo_peligro_id,
              label: row.nombre,
            })),
          )
        } catch (error) {
          if (requestId === requestRef.current) {
            toast.error(
              getErrorMessage(error, 'No se pudo obtener el catálogo de tipos de peligro'),
            )
          }
          resolve([])
        }
      }, SEARCH_DELAY_MS)
    })
  }, [])

  return (
    <AsyncSelect
      inputId={inputId}
      instanceId={inputId}
      value={value}
      onChange={onChange}
      loadOptions={loadOptions}
      isDisabled={disabled}
      isClearable
      cacheOptions={false}
      defaultOptions={false}
      placeholder="Buscar por nombre"
      loadingMessage={() => 'Buscando...'}
      noOptionsMessage={({ inputValue }) =>
        inputValue.trim() ? 'No se encontraron tipos de peligro' : 'Escriba un nombre para buscar'
      }
      styles={selectStyles}
    />
  )
}
