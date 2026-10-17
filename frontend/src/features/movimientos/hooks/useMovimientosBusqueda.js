import { useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useMovimientosBusqueda() {
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [movimientos, setMovimientos] = useState([])

  async function buscar(params) {
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarMovimientos(params)
      setMovimientos(rows)
      setSearched(true)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de movimientos de almacén'))
    } finally {
      setLoading(false)
    }
  }

  function limpiarResultados() {
    setMovimientos([])
    setSearched(false)
  }

  function quitarMovimiento(movimientoId) {
    setMovimientos((current) => current.filter((item) => item.movimiento_id !== movimientoId))
  }

  return {
    loading,
    searched,
    movimientos,
    buscar,
    limpiarResultados,
    quitarMovimiento,
  }
}
