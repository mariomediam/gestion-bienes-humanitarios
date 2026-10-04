import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'
import { getFechaUnMesAnterior } from '@utils/dates'

const EMPTY_TOTALES = {
  emergencias: null,
  formularios2a: null,
  planillasBah: null,
  integrantes: null,
}

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

export default function useDashboard() {
  const [fechaDesde] = useState(() => getFechaUnMesAnterior())
  const [loading, setLoading] = useState(true)
  const [totales, setTotales] = useState(EMPTY_TOTALES)
  const [tiposPeligro, setTiposPeligro] = useState([])
  const [emergencias, setEmergencias] = useState([])

  useEffect(() => {
    let cancelled = false

    async function load() {
      setLoading(true)

      const [
        emergenciasTotal,
        formulariosTotal,
        planillasTotal,
        integrantesTotal,
        tipos,
        listado,
      ] = await Promise.allSettled([
        sgbhApi.getTotalEmergencias(),
        sgbhApi.getTotalFormularios2A(),
        sgbhApi.getTotalPlanillasBah(),
        sgbhApi.getTotalIntegrantes(),
        sgbhApi.getTotalPorTipoPeligro(),
        sgbhApi.getEmergencias({ fecha_desde: fechaDesde }),
      ])

      if (cancelled) return

      const nextTotales = { ...EMPTY_TOTALES }

      if (emergenciasTotal.status === 'fulfilled') {
        nextTotales.emergencias = emergenciasTotal.value.total
      } else {
        toast.error(getErrorMessage(emergenciasTotal.reason, 'No se pudo obtener el total de emergencias'))
      }

      if (formulariosTotal.status === 'fulfilled') {
        nextTotales.formularios2a = formulariosTotal.value.total
      } else {
        toast.error(getErrorMessage(formulariosTotal.reason, 'No se pudo obtener el total de formularios EDAN 2A'))
      }

      if (planillasTotal.status === 'fulfilled') {
        nextTotales.planillasBah = planillasTotal.value.total
      } else {
        toast.error(getErrorMessage(planillasTotal.reason, 'No se pudo obtener el total de planillas BAH'))
      }

      if (integrantesTotal.status === 'fulfilled') {
        nextTotales.integrantes = integrantesTotal.value.total
      } else {
        toast.error(getErrorMessage(integrantesTotal.reason, 'No se pudo obtener el total de integrantes'))
      }

      if (tipos.status === 'fulfilled') {
        setTiposPeligro(tipos.value)
      } else {
        setTiposPeligro([])
        toast.error(getErrorMessage(tipos.reason, 'No se pudo obtener el total de emergencias por tipo de peligro'))
      }

      if (listado.status === 'fulfilled') {
        setEmergencias(listado.value)
      } else {
        setEmergencias([])
        toast.error(getErrorMessage(listado.reason, 'No se pudo obtener el listado de emergencias'))
      }

      setTotales(nextTotales)
      setLoading(false)
    }

    load()

    return () => {
      cancelled = true
    }
  }, [fechaDesde])

  return { loading, totales, tiposPeligro, emergencias }
}
