import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function usePlanillaBahReporte(planillaEntregaId) {
  const [loading, setLoading] = useState(true)
  const [reporte, setReporte] = useState(null)

  useEffect(() => {
    let active = true

    async function load() {
      setLoading(true)
      try {
        const data = await sgbhApi.getPlanillaBahReporte(planillaEntregaId)
        if (active) setReporte(data)
      } catch (error) {
        if (!active) return
        setReporte(null)
        toast.error(getErrorMessage(error, 'No se pudo obtener el reporte de la planilla BAH'))
      } finally {
        if (active) setLoading(false)
      }
    }

    load()
    return () => {
      active = false
    }
  }, [planillaEntregaId])

  return { loading, reporte }
}
