import { useCallback, useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useIntegrantesFamilia(familiaId) {
  const [loading, setLoading] = useState(true)
  const [consultado, setConsultado] = useState(false)
  const [integrantes, setIntegrantes] = useState([])
  const requestId = useRef(0)
  const familiaIdRef = useRef(familiaId)

  if (familiaIdRef.current !== familiaId) {
    familiaIdRef.current = familiaId
    requestId.current += 1
    setIntegrantes([])
    setConsultado(false)
    setLoading(true)
  }

  const cargarIntegrantes = useCallback(async () => {
    const current = ++requestId.current
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarIntegrantes({ familia_id: familiaId })
      if (current !== requestId.current) return
      setIntegrantes(rows)
      setConsultado(true)
    } catch (error) {
      if (current !== requestId.current) return
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de integrantes'))
    } finally {
      if (current === requestId.current) setLoading(false)
    }
  }, [familiaId])

  useEffect(() => {
    return () => {
      requestId.current += 1
    }
  }, [])

  return { loading, consultado, integrantes, cargarIntegrantes }
}
