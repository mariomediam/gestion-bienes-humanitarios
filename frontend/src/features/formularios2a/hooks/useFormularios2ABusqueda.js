import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import { buildFormulario2ASearchParams } from '@features/formularios2a/searchParams'
import useFormularios2ABusquedaStore from '@store/formularios2ABusquedaStore'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export async function mostrarFormularioRecienCreado(formulario2aId) {
  const { prepararFormularioCreado, setResultados } = useFormularios2ABusquedaStore.getState()
  prepararFormularioCreado(formulario2aId)

  try {
    const rows = await sgbhApi.buscarFormularios2A({ formulario_2a_id: formulario2aId })
    setResultados(rows)
    useFormularios2ABusquedaStore.setState({ formularioCreadoId: null })
  } catch (error) {
    toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de formularios EDAN 2A'))
  }
}

export default function useFormularios2ABusqueda() {
  const [loading, setLoading] = useState(false)
  const consulta = useFormularios2ABusquedaStore((state) => state.consulta)
  const filtros = useFormularios2ABusquedaStore((state) => state.filtros)
  const avanzadaAbierta = useFormularios2ABusquedaStore((state) => state.avanzadaAbierta)
  const searched = useFormularios2ABusquedaStore((state) => state.searched)
  const formularios = useFormularios2ABusquedaStore((state) => state.formularios)
  const setConsulta = useFormularios2ABusquedaStore((state) => state.setConsulta)
  const setFiltro = useFormularios2ABusquedaStore((state) => state.setFiltro)
  const toggleAvanzada = useFormularios2ABusquedaStore((state) => state.toggleAvanzada)
  const limpiar = useFormularios2ABusquedaStore((state) => state.limpiar)
  const solicitarActualizacion = useFormularios2ABusquedaStore((state) => state.solicitarActualizacion)
  const quitarFormulario = useFormularios2ABusquedaStore((state) => state.quitarFormulario)

  async function ejecutarBusqueda() {
    const { consulta: consultaActual, filtros: filtrosActuales, setResultados } =
      useFormularios2ABusquedaStore.getState()
    setLoading(true)

    try {
      const rows = await sgbhApi.buscarFormularios2A(
        buildFormulario2ASearchParams(consultaActual, filtrosActuales),
      )
      setResultados(rows)
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de formularios EDAN 2A'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const { formularioCreadoId, searched: yaBuscado, actualizarAlRegresar } =
      useFormularios2ABusquedaStore.getState()

    if (formularioCreadoId) {
      mostrarFormularioRecienCreado(formularioCreadoId)
      return
    }

    if (!yaBuscado || !actualizarAlRegresar) return

    useFormularios2ABusquedaStore.setState({ actualizarAlRegresar: false })
    ejecutarBusqueda()
  }, [])

  function buscar(event) {
    event.preventDefault()
    ejecutarBusqueda()
  }

  return {
    loading,
    searched,
    formularios,
    consulta,
    filtros,
    avanzadaAbierta,
    setConsulta,
    setFiltro,
    toggleAvanzada,
    buscar,
    limpiar,
    solicitarActualizacion,
    quitarFormulario,
  }
}
