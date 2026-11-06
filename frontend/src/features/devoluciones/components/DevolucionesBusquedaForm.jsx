import FechaFiltroInput from '@components/FechaFiltroInput'
import ClearIcon from '@components/icons/ClearIcon'
import FilterIcon from '@components/icons/FilterIcon'
import SearchIcon from '@components/icons/SearchIcon'

const buttonIconClassName = 'w-4 h-4'

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

export default function DevolucionesBusquedaForm({
  bienNombre,
  onBienNombreChange,
  filtros,
  onFiltroChange,
  avanzadaAbierta,
  onToggleAvanzada,
  onSubmit,
  onLimpiar,
  loading,
}) {
  return (
    <form onSubmit={onSubmit} className="bg-white rounded-lg border border-gray-200 p-5 space-y-4">
      <div>
        <label htmlFor="bien-nombre-devolucion" className="sr-only">
          Búsqueda por nombre del bien
        </label>
        <input
          id="bien-nombre-devolucion"
          type="search"
          value={bienNombre}
          onChange={(event) => onBienNombreChange(event.target.value)}
          placeholder="Buscar por nombre del bien"
          maxLength={250}
          disabled={loading}
          className={inputClassName}
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
          onClick={onToggleAvanzada}
          aria-expanded={avanzadaAbierta}
          aria-controls="filtros-avanzados-devolucion"
          disabled={loading}
          className="inline-flex items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <FilterIcon className={buttonIconClassName} />
          Búsqueda avanzada
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

      {avanzadaAbierta && (
        <div id="filtros-avanzados-devolucion" className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div>
            <label htmlFor="fecha-devolucion-desde" className={labelClassName}>
              Fecha desde
            </label>
            <FechaFiltroInput
              id="fecha-devolucion-desde"
              value={filtros.fecha_desde}
              onChange={(value) => onFiltroChange('fecha_desde', value)}
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="fecha-devolucion-hasta" className={labelClassName}>
              Fecha hasta
            </label>
            <FechaFiltroInput
              id="fecha-devolucion-hasta"
              value={filtros.fecha_hasta}
              onChange={(value) => onFiltroChange('fecha_hasta', value)}
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="documento-referencia-devolucion" className={labelClassName}>
              Documento de referencia
            </label>
            <input
              id="documento-referencia-devolucion"
              type="text"
              value={filtros.documento_referencia}
              onChange={(event) => onFiltroChange('documento_referencia', event.target.value)}
              maxLength={100}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="numero-planilla-devolucion" className={labelClassName}>
              Número de planilla
            </label>
            <input
              id="numero-planilla-devolucion"
              type="text"
              inputMode="numeric"
              value={filtros.numero_planilla}
              onChange={(event) => onFiltroChange('numero_planilla', event.target.value)}
              disabled={loading}
              className={inputClassName}
            />
          </div>
        </div>
      )}
    </form>
  )
}
