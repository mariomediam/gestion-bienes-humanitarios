import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { sgbhApi } from '@api/sgbhApi'

function getErrorMessage(error, fallback) {
  return error?.response?.data?.error || fallback
}

function paramsKardex(bienId) {
  return { bien_id: bienId }
}

export default function useKardex(bienId) {
  const [bien, setBien] = useState(null)
  const [filas, setFilas] = useState([])
  const [loadingBien, setLoadingBien] = useState(true)
  const [loadingKardex, setLoadingKardex] = useState(true)
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [filtros, setFiltros] = useState({ fechaDesde: '', fechaHasta: '' })

  useEffect(() => {
    let cancelled = false

    setFechaDesde('')
    setFechaHasta('')
    setFiltros({ fechaDesde: '', fechaHasta: '' })
    setBien(null)
    setFilas([])
    setLoadingBien(true)
    setLoadingKardex(true)

    sgbhApi.buscarBienes({ bien_id: bienId })
      .then((rows) => {
        if (cancelled) return
        setBien(Array.isArray(rows) && rows.length > 0 ? rows[0] : null)
      })
      .catch((error) => {
        if (cancelled) return
        toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda de bienes'))
        setBien(null)
      })
      .finally(() => {
        if (!cancelled) setLoadingBien(false)
      })

    sgbhApi.buscarKardex(paramsKardex(bienId))
      .then((rows) => {
        if (cancelled) return
        setFilas(Array.isArray(rows) ? rows : [])
      })
      .catch((error) => {
        if (cancelled) return
        toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda del kardex de almacén'))
      })
      .finally(() => {
        if (!cancelled) setLoadingKardex(false)
      })

    return () => {
      cancelled = true
    }
  }, [bienId])

  async function cargarKardex() {
    setLoadingKardex(true)

    try {
      const rows = await sgbhApi.buscarKardex(paramsKardex(bienId))
      setFilas(Array.isArray(rows) ? rows : [])
    } catch (error) {
      toast.error(getErrorMessage(error, 'No se pudo obtener la búsqueda del kardex de almacén'))
    } finally {
      setLoadingKardex(false)
    }
  }

  function actualizar(event) {
    event.preventDefault()
    if (fechaDesde && fechaHasta && fechaDesde > fechaHasta) {
      toast.error('El filtro fecha_desde no puede ser posterior a fecha_hasta')
      return
    }
    setFiltros({ fechaDesde, fechaHasta })
    cargarKardex()
  }

  function limpiar() {
    setFechaDesde('')
    setFechaHasta('')
    setFiltros({ fechaDesde: '', fechaHasta: '' })
    cargarKardex()
  }

  return {
    bien,
    filas,
    loadingBien,
    loadingKardex,
    fechaDesde,
    fechaHasta,
    filtros,
    setFechaDesde,
    setFechaHasta,
    actualizar,
    limpiar,
  }
}
