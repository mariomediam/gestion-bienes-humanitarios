import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

const ROL_FAMILIAR_JEFE_ID = 1

const selectClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm bg-white focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function nombreIntegrante(row) {
  return [row.apellido_paterno, row.apellido_materno, row.nombres].filter(Boolean).join(' ')
}

export default function IntegranteReceptorSelect({
  id,
  formulario2aId,
  value,
  onChange,
  disabled,
}) {
  const [integrantes, setIntegrantes] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    setLoading(true)
    setIntegrantes([])

    sgbhApi
      .buscarIntegrantes({ formulario_2a_id: formulario2aId })
      .then((rows) => {
        if (!active) return
        const jefes = (Array.isArray(rows) ? rows : [])
          .filter((row) => Number(row.rol_familiar_id) === ROL_FAMILIAR_JEFE_ID)
          .map((row) => ({
            integrante_id: row.integrante_id,
            label: nombreIntegrante(row),
          }))
          .sort((left, right) => left.label.localeCompare(right.label, 'es'))
        setIntegrantes(jefes)
      })
      .catch((error) => {
        if (active) {
          toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de integrantes'))
        }
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [formulario2aId])

  return (
    <select
      id={id}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      disabled={disabled || loading}
      className={selectClassName}
    >
      <option value="">
        {loading ? 'Cargando...' : 'Seleccione un jefe de familia'}
      </option>
      {integrantes.map((integrante) => (
        <option key={integrante.integrante_id} value={integrante.integrante_id}>
          {integrante.label}
        </option>
      ))}
    </select>
  )
}
