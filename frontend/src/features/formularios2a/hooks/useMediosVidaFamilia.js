import { useCallback, useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useMediosVidaFamilia(familiaId) {
  const [loading, setLoading] = useState(true)
  const [consultado, setConsultado] = useState(false)
  const [mediosVida, setMediosVida] = useState([])
  const requestId = useRef(0)
  const familiaIdRef = useRef(familiaId)

  if (familiaIdRef.current !== familiaId) {
    familiaIdRef.current = familiaId
    requestId.current += 1
    setMediosVida([])
    setConsultado(false)
    setLoading(true)
  }

  const cargarMediosVida = useCallback(async () => {
    const current = ++requestId.current
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarMediosVida({ familia_id: familiaId })
      if (current !== requestId.current) return
      setMediosVida(rows)
      setConsultado(true)
    } catch (error) {
      if (current !== requestId.current) return
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de medios de vida'))
    } finally {
      if (current === requestId.current) setLoading(false)
    }
  }, [familiaId])

  useEffect(() => {
    return () => {
      requestId.current += 1
    }
  }, [])

  return { loading, consultado, mediosVida, cargarMediosVida }
}
