import { useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import { buildFormulario2ASearchParams } from '@features/formularios2a/searchParams'
import useFormularios2ABusquedaStore from '@store/formularios2ABusquedaStore'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
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

  async function buscar(event) {
    event.preventDefault()
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
  }
}
