import { useCallback, useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useViviendasFormulario2A(formulario2aId) {
  const [loading, setLoading] = useState(true)
  const [consultado, setConsultado] = useState(false)
  const [viviendas, setViviendas] = useState([])
  const requestId = useRef(0)
  const formularioIdRef = useRef(formulario2aId)

  if (formularioIdRef.current !== formulario2aId) {
    formularioIdRef.current = formulario2aId
    requestId.current += 1
    setViviendas([])
    setConsultado(false)
    setLoading(true)
  }

  const cargarViviendas = useCallback(async () => {
    const current = ++requestId.current
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarViviendas({
        formulario_2a_id: formulario2aId,
      })
      if (current !== requestId.current) return
      setViviendas(rows)
      setConsultado(true)
    } catch (error) {
      if (current !== requestId.current) return
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de viviendas'))
    } finally {
      if (current === requestId.current) setLoading(false)
    }
  }, [formulario2aId])

  useEffect(() => {
    return () => {
      requestId.current += 1
    }
  }, [])

  return { loading, consultado, viviendas, cargarViviendas }
}
