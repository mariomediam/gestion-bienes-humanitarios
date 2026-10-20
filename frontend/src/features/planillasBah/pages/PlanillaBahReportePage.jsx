import { Link, useParams } from 'react-router-dom'
import usePlanillaBahReporte from '@features/planillasBah/hooks/usePlanillaBahReporte'
import PlanillaBahReporteHoja from '@features/planillasBah/reporte/PlanillaBahReporteHoja'
import '@features/planillasBah/reporte/planillaBahReporte.css'

function LoadingState() {
  return (
    <div className="flex items-center justify-center py-24">
      <div className="text-center">
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Cargando planilla BAH...</p>
      </div>
    </div>
  )
}

export default function PlanillaBahReportePage() {
  const { planillaEntregaId } = useParams()
  const { loading, reporte } = usePlanillaBahReporte(planillaEntregaId)

  if (loading) return <LoadingState />

  if (!reporte) {
    return (
      <div className="space-y-4">
        <Link
          to="/alm-planilla-bah"
          className="inline-flex text-sm font-medium text-[#1e3064] hover:underline focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 rounded-sm"
        >
          Volver al listado
        </Link>
        <p className="text-sm text-gray-600">No se pudo obtener el reporte de la planilla BAH</p>
      </div>
    )
  }

  return (
    <div className="bah-pagina">
      <div className="bah-toolbar">
        <Link
          to="/alm-planilla-bah"
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

      <PlanillaBahReporteHoja reporte={reporte} />
    </div>
  )
}
