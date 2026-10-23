import { useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import useStockActualBusquedaStore from '@store/stockActualBusquedaStore'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useStockActualBusqueda() {
  const [loading, setLoading] = useState(false)
  const bien = useStockActualBusquedaStore((state) => state.bien)
  const searched = useStockActualBusquedaStore((state) => state.searched)
  const filas = useStockActualBusquedaStore((state) => state.filas)
  const setBien = useStockActualBusquedaStore((state) => state.setBien)
  const limpiar = useStockActualBusquedaStore((state) => state.limpiar)

  async function buscar(params) {
    setLoading(true)

    try {
      const rows = await sgbhApi.getStockActual(params)
      useStockActualBusquedaStore.getState().setResultados(rows)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener el stock actual'))
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    searched,
    filas,
    bien,
    setBien,
    buscar,
    limpiar,
  }
}
