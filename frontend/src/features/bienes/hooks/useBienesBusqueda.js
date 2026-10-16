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

  function reemplazarBien(bien) {
    setBienes((current) =>
      current.map((item) => (item.bien_id === bien.bien_id ? bien : item)),
    )
  }

  function quitarBien(bienId) {
    setBienes((current) => current.filter((item) => item.bien_id !== bienId))
  }

  return {
    loading,
    searched,
    bienes,
    buscar,
    limpiarResultados,
    reemplazarBien,
    quitarBien,
  }
}
