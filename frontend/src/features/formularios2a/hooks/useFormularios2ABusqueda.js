import { useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useFormularios2ABusqueda() {
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [formularios, setFormularios] = useState([])

  async function buscar(params) {
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarFormularios2A(params)
      setFormularios(rows)
      setSearched(true)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de formularios EDAN 2A'))
    } finally {
      setLoading(false)
    }
  }

  function limpiarResultados() {
    setFormularios([])
    setSearched(false)
  }

  return {
    loading,
    searched,
    formularios,
    buscar,
    limpiarResultados,
  }
}
