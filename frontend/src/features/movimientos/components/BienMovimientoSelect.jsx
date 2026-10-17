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

export function etiquetaUnidadMedida(bien) {
  if (!bien) return ''
  const nombre = bien.unidad_medida_nombre || ''
  const abreviatura = bien.unidad_medida_abreviatura || ''
  if (nombre && abreviatura) return `${nombre} (${abreviatura})`
  return nombre || abreviatura
}

export default function BienMovimientoSelect({ inputId, value, onChange, disabled }) {
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
          const rows = await sgbhApi.buscarBienes({ nombre: texto })
          if (requestId !== requestRef.current) {
            resolve([])
            return
          }
          resolve(
            rows.map((row) => ({
              value: row.bien_id,
              label: row.nombre,
              unidad_medida_nombre: row.unidad_medida_nombre,
              unidad_medida_abreviatura: row.unidad_medida_abreviatura,
            })),
          )
        } catch (error) {
          if (requestId === requestRef.current) {
            toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de bienes'))
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
      placeholder="Buscar por nombre"
      loadingMessage={() => 'Buscando...'}
      noOptionsMessage={({ inputValue }) =>
        inputValue.trim() ? 'No se encontraron bienes' : 'Escriba un nombre para buscar'
      }
      styles={selectStyles}
    />
  )
}
