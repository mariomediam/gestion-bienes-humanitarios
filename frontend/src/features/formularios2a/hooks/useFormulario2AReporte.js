import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useFormulario2AReporte(formulario2aId) {
  const [loading, setLoading] = useState(true)
  const [reporte, setReporte] = useState(null)

  useEffect(() => {
    let active = true

    async function load() {
      setLoading(true)
      try {
        const data = await sgbhApi.getFormulario2AReporte(formulario2aId)
        if (active) setReporte(data)
      } catch (error) {
        if (!active) return
        setReporte(null)
        toast.error(getErrorMessage(error, 'No se pudo obtener el reporte del formulario EDAN 2A'))
      } finally {
        if (active) setLoading(false)
      }
    }

    load()
    return () => {
      active = false
    }
  }, [formulario2aId])

  return { loading, reporte }
}
