import { Link, useParams } from 'react-router-dom'
import Formulario2AReporteHoja from '@features/formularios2a/reporte/Formulario2AReporteHoja'
import useFormulario2AReporte from '@features/formularios2a/hooks/useFormulario2AReporte'
import '@features/formularios2a/reporte/formulario2aReporte.css'

const FILAS_POR_HOJA = 12

function paginasDe(filas) {
  const origen = Array.isArray(filas) ? filas : []
  if (origen.length === 0) {
    return [Array(FILAS_POR_HOJA).fill(null)]
  }

  const paginas = []
  for (let inicio = 0; inicio < origen.length; inicio += FILAS_POR_HOJA) {
    const pagina = origen.slice(inicio, inicio + FILAS_POR_HOJA)
    while (pagina.length < FILAS_POR_HOJA) pagina.push(null)
    paginas.push(pagina)
  }
  return paginas
}

function LoadingState() {
  return (
    <div className="flex items-center justify-center py-24">
      <div className="text-center">
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Cargando formulario EDAN 2A...</p>
      </div>
    </div>
  )
}

export default function Formulario2AReportePage() {
  const { formulario2aId } = useParams()
  const { loading, reporte } = useFormulario2AReporte(formulario2aId)

  if (loading) return <LoadingState />

  if (!reporte) {
    return (
      <div className="space-y-4">
        <Link
          to="/formularios-2A"
          className="inline-flex text-sm font-medium text-[#1e3064] hover:underline focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 rounded-sm"
        >
          Volver al listado
        </Link>
        <p className="text-sm text-gray-600">No se pudo obtener el reporte del formulario EDAN 2A</p>
      </div>
    )
  }

  const paginas = paginasDe(reporte.filas)

  return (
    <div className="reporte-pagina">
      <div className="reporte-toolbar">
        <Link
          to="/formularios-2A"
          className="inline-flex text-sm font-medium text-[#1e3064] hover:underline focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 rounded-sm"
        >
          Volver al listado
        </Link>
        <button
          type="button"
          onClick={() => window.print()}
          className="inline-flex items-center whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
        >
          Imprimir
        </button>
      </div>

      {paginas.map((filas, indice) => (
        <Formulario2AReporteHoja key={indice} reporte={reporte} filas={filas} />
      ))}
    </div>
  )
}
