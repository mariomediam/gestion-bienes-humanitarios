import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import { agruparDevoluciones } from '@features/devoluciones/agruparDevoluciones'
import { buildDevolucionSearchParams } from '@features/devoluciones/searchParams'
import useDevolucionesBusquedaStore from '@store/devolucionesBusquedaStore'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export async function mostrarDevolucionRecienCreada(movimientoId) {
  const { prepararDevolucionCreada, setResultados } = useDevolucionesBusquedaStore.getState()
  prepararDevolucionCreada(movimientoId)

  try {
    const rows = await sgbhApi.buscarDevoluciones({ movimiento_id: movimientoId })
    setResultados(agruparDevoluciones(rows))
    useDevolucionesBusquedaStore.setState({ devolucionCreadaId: null })
  } catch (error) {
    toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de devoluciones'))
  }
}

export default function useDevolucionesBusqueda() {
  const [loading, setLoading] = useState(false)
  const bienNombre = useDevolucionesBusquedaStore((state) => state.bienNombre)
  const filtros = useDevolucionesBusquedaStore((state) => state.filtros)
  const avanzadaAbierta = useDevolucionesBusquedaStore((state) => state.avanzadaAbierta)
  const searched = useDevolucionesBusquedaStore((state) => state.searched)
  const devoluciones = useDevolucionesBusquedaStore((state) => state.devoluciones)
  const setBienNombre = useDevolucionesBusquedaStore((state) => state.setBienNombre)
  const setFiltro = useDevolucionesBusquedaStore((state) => state.setFiltro)
  const toggleAvanzada = useDevolucionesBusquedaStore((state) => state.toggleAvanzada)
  const limpiar = useDevolucionesBusquedaStore((state) => state.limpiar)
  const solicitarActualizacion = useDevolucionesBusquedaStore((state) => state.solicitarActualizacion)
  const quitarDevolucion = useDevolucionesBusquedaStore((state) => state.quitarDevolucion)

  async function ejecutarBusqueda() {
    const { bienNombre: nombreActual, filtros: filtrosActuales, setResultados } =
      useDevolucionesBusquedaStore.getState()
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarDevoluciones(
        buildDevolucionSearchParams(nombreActual, filtrosActuales),
      )
      setResultados(agruparDevoluciones(rows))
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de devoluciones'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const { devolucionCreadaId, searched: yaBuscado, actualizarAlRegresar } =
      useDevolucionesBusquedaStore.getState()

    if (devolucionCreadaId) {
      mostrarDevolucionRecienCreada(devolucionCreadaId)
      return
    }

    if (!yaBuscado || !actualizarAlRegresar) return

    useDevolucionesBusquedaStore.setState({ actualizarAlRegresar: false })
    ejecutarBusqueda()
  }, [])

  function buscar(event) {
    event.preventDefault()
    ejecutarBusqueda()
  }

  return {
    loading,
    searched,
    devoluciones,
    bienNombre,
    filtros,
    avanzadaAbierta,
    setBienNombre,
    setFiltro,
    toggleAvanzada,
    buscar,
    limpiar,
    solicitarActualizacion,
    quitarDevolucion,
  }
}
