import ClearIcon from '@components/icons/ClearIcon'
import SearchIcon from '@components/icons/SearchIcon'
import BienMovimientoSelect from '@features/movimientos/components/BienMovimientoSelect'

const buttonIconClassName = 'w-4 h-4'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

export default function StockActualBusquedaForm({ bien, onBienChange, onSubmit, onLimpiar, loading }) {
  return (
    <form onSubmit={onSubmit} className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
      <div>
        <label htmlFor="bien-stock-actual" className={labelClassName}>
          Bien
        </label>
        <BienMovimientoSelect
          inputId="bien-stock-actual"
          value={bien}
          onChange={onBienChange}
          disabled={loading}
        />
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-white bg-[#1e3064] rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <SearchIcon className={buttonIconClassName} />
          {loading ? 'Buscando...' : 'Buscar'}
        </button>
        <button
          type="button"
          onClick={onLimpiar}
          disabled={loading}
          className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ClearIcon className={buttonIconClassName} />
          Limpiar
        </button>
      </div>
    </form>
  )
}
