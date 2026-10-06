import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useFormulario2ADetalle(formulario2aId) {
  const [loading, setLoading] = useState(true)
  const [formulario, setFormulario] = useState(null)

  useEffect(() => {
    let active = true

    async function load() {
      setLoading(true)
      try {
        const data = await sgbhApi.getFormulario2A(formulario2aId)
        if (active) setFormulario(data)
      } catch (error) {
        if (!active) return
        setFormulario(null)
        toast.error(getErrorMessage(error, 'No se pudo obtener el formulario EDAN 2A'))
      } finally {
        if (active) setLoading(false)
      }
    }

    load()
    return () => {
      active = false
    }
  }, [formulario2aId])

  function reemplazarFormulario(data) {
    setFormulario(data)
  }

  return { loading, formulario, reemplazarFormulario }
}
