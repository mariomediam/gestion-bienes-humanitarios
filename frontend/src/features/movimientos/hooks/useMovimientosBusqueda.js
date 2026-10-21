import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import { buildMovimientoSearchParams } from '@features/movimientos/searchParams'
import useMovimientosBusquedaStore from '@store/movimientosBusquedaStore'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export async function mostrarMovimientoRecienCreado(movimientoId) {
  const { prepararMovimientoCreado, setResultados } = useMovimientosBusquedaStore.getState()
  prepararMovimientoCreado(movimientoId)

  try {
    const rows = await sgbhApi.buscarMovimientos({ movimiento_id: movimientoId })
    setResultados(rows)
    useMovimientosBusquedaStore.setState({ movimientoCreadoId: null })
  } catch (error) {
    toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de movimientos de almacén'))
  }
}

export default function useMovimientosBusqueda() {
  const [loading, setLoading] = useState(false)
  const bienNombre = useMovimientosBusquedaStore((state) => state.bienNombre)
  const filtros = useMovimientosBusquedaStore((state) => state.filtros)
  const avanzadaAbierta = useMovimientosBusquedaStore((state) => state.avanzadaAbierta)
  const searched = useMovimientosBusquedaStore((state) => state.searched)
  const movimientos = useMovimientosBusquedaStore((state) => state.movimientos)
  const setBienNombre = useMovimientosBusquedaStore((state) => state.setBienNombre)
  const setFiltro = useMovimientosBusquedaStore((state) => state.setFiltro)
  const toggleAvanzada = useMovimientosBusquedaStore((state) => state.toggleAvanzada)
  const limpiar = useMovimientosBusquedaStore((state) => state.limpiar)
  const solicitarActualizacion = useMovimientosBusquedaStore((state) => state.solicitarActualizacion)
  const quitarMovimiento = useMovimientosBusquedaStore((state) => state.quitarMovimiento)

  async function ejecutarBusqueda() {
    const { bienNombre: nombreActual, filtros: filtrosActuales, setResultados } =
      useMovimientosBusquedaStore.getState()
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarMovimientos(
        buildMovimientoSearchParams(nombreActual, filtrosActuales),
      )
      setResultados(rows)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de movimientos de almacén'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const { movimientoCreadoId, searched: yaBuscado, actualizarAlRegresar } =
      useMovimientosBusquedaStore.getState()

    if (movimientoCreadoId) {
      mostrarMovimientoRecienCreado(movimientoCreadoId)
      return
    }

    if (!yaBuscado || !actualizarAlRegresar) return

    useMovimientosBusquedaStore.setState({ actualizarAlRegresar: false })
    ejecutarBusqueda()
  }, [])

  function buscar(event) {
    event.preventDefault()
    ejecutarBusqueda()
  }

  return {
    loading,
    searched,
    movimientos,
    bienNombre,
    filtros,
    avanzadaAbierta,
    setBienNombre,
    setFiltro,
    toggleAvanzada,
    buscar,
    limpiar,
    solicitarActualizacion,
    quitarMovimiento,
  }
}
