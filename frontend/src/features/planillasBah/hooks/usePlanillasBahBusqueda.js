import { useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function usePlanillasBahBusqueda() {
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [planillas, setPlanillas] = useState([])

  async function buscar(params) {
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarPlanillasBah(params)
      setPlanillas(rows)
      setSearched(true)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de planillas BAH'))
    } finally {
      setLoading(false)
    }
  }

  function limpiarResultados() {
    setPlanillas([])
    setSearched(false)
  }

  return {
    loading,
    searched,
    planillas,
    buscar,
    limpiarResultados,
  }
}
