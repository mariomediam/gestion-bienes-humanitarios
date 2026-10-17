import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

const selectClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function TipoMovimientoSelect({
  id,
  value,
  onChange,
  disabled,
  excluirIds = [],
}) {
  const [tipos, setTipos] = useState([])
  const [loading, setLoading] = useState(true)
  const excluidos = new Set(excluirIds.map(Number))
  const visibles = tipos.filter((tipo) => !excluidos.has(Number(tipo.tipo_movimiento_id)))

  useEffect(() => {
    let active = true

    sgbhApi
      .getTiposMovimiento()
      .then((rows) => {
        if (active) {
          setTipos(rows)
        }
      })
      .catch((error) => {
        if (active) {
          toast.error(getErrorMessage(error, 'No se pudo obtener el catálogo de tipos de movimiento'))
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
    <select
      id={id}
      value={value}
      onChange={(event) => {
        const selectedId = event.target.value
        const tipo = visibles.find(
          (item) => String(item.tipo_movimiento_id) === selectedId,
        ) || null
        onChange(selectedId, tipo)
      }}
      disabled={disabled || loading}
      className={selectClassName}
    >
      <option value="">
        {loading ? 'Cargando...' : 'Seleccione un tipo de movimiento'}
      </option>
      {visibles.map((tipo) => (
        <option key={tipo.tipo_movimiento_id} value={tipo.tipo_movimiento_id}>
          {tipo.nombre}
        </option>
      ))}
    </select>
  )
}
