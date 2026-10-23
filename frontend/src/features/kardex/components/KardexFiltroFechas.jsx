import FechaFiltroInput from '@components/FechaFiltroInput'
import ClearIcon from '@components/icons/ClearIcon'
import SearchIcon from '@components/icons/SearchIcon'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

export default function KardexFiltroFechas({
  fechaDesde,
  fechaHasta,
  onFechaDesdeChange,
  onFechaHastaChange,
  onSubmit,
  onLimpiar,
  loading,
}) {
  return (
    <form onSubmit={onSubmit} className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="kardex-fecha-desde" className={labelClassName}>
            Fecha desde
          </label>
          <FechaFiltroInput
            id="kardex-fecha-desde"
            value={fechaDesde}
            onChange={onFechaDesdeChange}
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="kardex-fecha-hasta" className={labelClassName}>
            Fecha hasta
          </label>
          <FechaFiltroInput
            id="kardex-fecha-hasta"
            value={fechaHasta}
            onChange={onFechaHastaChange}
            disabled={loading}
          />
        </div>
      </div>

      <div className="kardex-no-imprimir flex flex-wrap gap-2">
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <SearchIcon className="w-4 h-4" />
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
        <button
          type="button"
          onClick={onLimpiar}
          disabled={loading}
          className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ClearIcon className="w-4 h-4" />
          Limpiar
        </button>
      </div>
    </form>
  )
}
