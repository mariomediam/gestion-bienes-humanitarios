import { useCallback, useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useFamiliasVivienda(viviendaId) {
  const [loading, setLoading] = useState(true)
  const [consultado, setConsultado] = useState(false)
  const [familias, setFamilias] = useState([])
  const requestId = useRef(0)
  const viviendaIdRef = useRef(viviendaId)

  if (viviendaIdRef.current !== viviendaId) {
    viviendaIdRef.current = viviendaId
    requestId.current += 1
    setFamilias([])
    setConsultado(false)
    setLoading(true)
  }

  const cargarFamilias = useCallback(async () => {
    const current = ++requestId.current
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarFamilias({ vivienda_id: viviendaId })
      if (current !== requestId.current) return
      setFamilias(rows)
      setConsultado(true)
    } catch (error) {
      if (current !== requestId.current) return
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de familias'))
    } finally {
      if (current === requestId.current) setLoading(false)
    }
  }, [viviendaId])

  useEffect(() => {
    return () => {
      requestId.current += 1
    }
  }, [])

  return { loading, consultado, familias, cargarFamilias }
}
