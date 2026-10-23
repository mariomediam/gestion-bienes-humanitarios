import { Link, useParams } from 'react-router-dom'
import ExcelIcon from '@components/icons/ExcelIcon'
import KardexBienInfo from '@features/kardex/components/KardexBienInfo'
import KardexFiltroFechas from '@features/kardex/components/KardexFiltroFechas'
import KardexResultados from '@features/kardex/components/KardexResultados'
import { filasPresentacion } from '@features/kardex/columnasKardex'
import { exportKardexExcel } from '@features/kardex/exportKardexExcel'
import useKardex from '@features/kardex/hooks/useKardex'
import '@features/kardex/kardex.css'

export default function KardexPage() {
  const { bienId } = useParams()
  const {
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
  } = useKardex(bienId)

  const presentacion = filasPresentacion(filas, filtros)
  const hayResultados = presentacion.length > 0

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link
            to="/alm-stock-actual"
            className="kardex-no-imprimir inline-flex text-sm font-medium text-[#1e3064] hover:underline focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 rounded-sm"
          >
            Volver al listado
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-[#1e3064]">Kardex</h1>
        </div>

        {hayResultados && (
          <div className="kardex-no-imprimir flex flex-wrap gap-2">
            <button
              type="button"
              onClick={() => window.print()}
              className="inline-flex items-center whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
            >
              Imprimir
            </button>
            <button
              type="button"
              onClick={() => exportKardexExcel(filas, filtros)}
              className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
            >
              <ExcelIcon className="w-4 h-4" />
              Exportar a Excel
            </button>
          </div>
        )}
      </div>

      <KardexBienInfo bien={bien} loading={loadingBien} />

      <KardexFiltroFechas
        fechaDesde={fechaDesde}
        fechaHasta={fechaHasta}
        onFechaDesdeChange={setFechaDesde}
        onFechaHastaChange={setFechaHasta}
        onSubmit={actualizar}
        onLimpiar={limpiar}
        loading={loadingKardex}
      />

      <KardexResultados
        filas={filas}
        loading={loadingKardex}
        fechaDesde={filtros.fechaDesde}
        fechaHasta={filtros.fechaHasta}
      />
    </div>
  )
}
