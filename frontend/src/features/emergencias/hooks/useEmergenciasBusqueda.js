import { useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useEmergenciasBusqueda() {
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [emergencias, setEmergencias] = useState([])

  async function buscar(params) {
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarEmergencias(params)
      setEmergencias(rows)
      setSearched(true)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de emergencias'))
    } finally {
      setLoading(false)
    }
  }

  function limpiarResultados() {
    setEmergencias([])
    setSearched(false)
  }

  function reemplazarEmergencia(emergencia) {
    setEmergencias((current) =>
      current.map((item) =>
        item.emergencia_id === emergencia.emergencia_id ? emergencia : item,
      ),
    )
  }

  function quitarEmergencia(emergenciaId) {
    setEmergencias((current) =>
      current.filter((item) => item.emergencia_id !== emergenciaId),
    )
  }

  return {
    loading,
    searched,
    emergencias,
    buscar,
    limpiarResultados,
    reemplazarEmergencia,
    quitarEmergencia,
  }
}
