import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import { buildPlanillaBahSearchParams } from '@features/planillasBah/searchParams'
import usePlanillasBahBusquedaStore from '@store/planillasBahBusquedaStore'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function usePlanillasBahBusqueda() {
  const [loading, setLoading] = useState(false)
  const consulta = usePlanillasBahBusquedaStore((state) => state.consulta)
  const filtros = usePlanillasBahBusquedaStore((state) => state.filtros)
  const avanzadaAbierta = usePlanillasBahBusquedaStore((state) => state.avanzadaAbierta)
  const searched = usePlanillasBahBusquedaStore((state) => state.searched)
  const planillas = usePlanillasBahBusquedaStore((state) => state.planillas)
  const setConsulta = usePlanillasBahBusquedaStore((state) => state.setConsulta)
  const setFiltro = usePlanillasBahBusquedaStore((state) => state.setFiltro)
  const toggleAvanzada = usePlanillasBahBusquedaStore((state) => state.toggleAvanzada)
  const limpiar = usePlanillasBahBusquedaStore((state) => state.limpiar)
  const solicitarActualizacion = usePlanillasBahBusquedaStore((state) => state.solicitarActualizacion)
  const quitarPlanilla = usePlanillasBahBusquedaStore((state) => state.quitarPlanilla)

  async function ejecutarBusqueda() {
    const { consulta: consultaActual, filtros: filtrosActuales, setResultados } =
      usePlanillasBahBusquedaStore.getState()
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarPlanillasBah(
        buildPlanillaBahSearchParams(consultaActual, filtrosActuales),
      )
      setResultados(rows)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de planillas BAH'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const { searched: yaBuscado, actualizarAlRegresar } = usePlanillasBahBusquedaStore.getState()

    if (!yaBuscado || !actualizarAlRegresar) return

    usePlanillasBahBusquedaStore.setState({ actualizarAlRegresar: false })
    ejecutarBusqueda()
  }, [])

  function buscar(event) {
    event.preventDefault()
    ejecutarBusqueda()
  }

  return {
    loading,
    searched,
    planillas,
    consulta,
    filtros,
    avanzadaAbierta,
    setConsulta,
    setFiltro,
    toggleAvanzada,
    buscar,
    limpiar,
    solicitarActualizacion,
    quitarPlanilla,
  }
}
