import { useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useStockActualBusqueda() {
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [filas, setFilas] = useState([])

  async function buscar(params) {
    setLoading(true)

    try {
      const rows = await sgbhApi.getStockActual(params)
      setFilas(rows)
      setSearched(true)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener el stock actual'))
    } finally {
      setLoading(false)
    }
  }

  function limpiarResultados() {
    setFilas([])
    setSearched(false)
  }

  return {
    loading,
    searched,
    filas,
    buscar,
    limpiarResultados,
  }
}
