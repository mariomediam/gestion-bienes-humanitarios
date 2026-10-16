import { useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useBienesBusqueda() {
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [bienes, setBienes] = useState([])

  async function buscar(params) {
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarBienes(params)
      setBienes(rows)
      setSearched(true)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de bienes'))
    } finally {
      setLoading(false)
    }
  }

  function limpiarResultados() {
    setBienes([])
    setSearched(false)
  }

  return {
    loading,
    searched,
    bienes,
    buscar,
    limpiarResultados,
  }
}
