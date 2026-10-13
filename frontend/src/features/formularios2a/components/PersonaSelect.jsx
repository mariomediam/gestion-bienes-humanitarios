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

export function etiquetaPersona(row) {
  const nombre = [row.apellido_paterno, row.apellido_materno, row.nombres]
    .filter((parte) => parte !== null && parte !== undefined && parte !== '')
    .join(' ')
  if (!row.numero_documento) return nombre
  return `${row.numero_documento} - ${nombre}`
}

function parametrosBusqueda(texto) {
  if (/^\d+$/.test(texto)) {
    return { numero_documento: texto }
  }
  return { nombre_completo: texto }
}

export default function PersonaSelect({ inputId, value, onChange, disabled }) {
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
    const texto = inputValue.trim()

    return new Promise((resolve) => {
      pendingRef.current.push(resolve)

      timeoutRef.current = setTimeout(async () => {
        pendingRef.current = pendingRef.current.filter((item) => item !== resolve)

        if (!texto || requestId !== requestRef.current) {
          resolve([])
          return
        }

        try {
          const rows = await sgbhApi.buscarPersonas(parametrosBusqueda(texto))
          if (requestId !== requestRef.current) {
            resolve([])
            return
          }
          resolve(
            rows.map((row) => ({
              value: row.persona_id,
              label: etiquetaPersona(row),
            })),
          )
        } catch (error) {
          if (requestId === requestRef.current) {
            toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de personas'))
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
      menuPortalTarget={document.body}
      menuPosition="fixed"
      placeholder="Buscar por documento o nombre"
      loadingMessage={() => 'Buscando...'}
      noOptionsMessage={({ inputValue }) =>
        inputValue.trim() ? 'No se encontraron personas' : 'Escriba un documento o nombre para buscar'
      }
      styles={selectStyles}
    />
  )
}
