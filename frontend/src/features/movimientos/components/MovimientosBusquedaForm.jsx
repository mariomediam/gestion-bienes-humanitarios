import ClearIcon from '@components/icons/ClearIcon'
import FilterIcon from '@components/icons/FilterIcon'
import SearchIcon from '@components/icons/SearchIcon'
import TipoMovimientoSelect from '@features/movimientos/components/TipoMovimientoSelect'

const buttonIconClassName = 'w-4 h-4'

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

export default function MovimientosBusquedaForm({
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
        <label htmlFor="bien-nombre-movimiento" className="sr-only">
          Búsqueda por nombre del bien
        </label>
        <input
          id="bien-nombre-movimiento"
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
          aria-controls="filtros-avanzados-movimiento"
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
        <div id="filtros-avanzados-movimiento" className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div>
            <label htmlFor="fecha-movimiento-desde" className={labelClassName}>
              Fecha desde
            </label>
            <input
              id="fecha-movimiento-desde"
              type="date"
              value={filtros.fecha_desde}
              onChange={(event) => onFiltroChange('fecha_desde', event.target.value)}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="fecha-movimiento-hasta" className={labelClassName}>
              Fecha hasta
            </label>
            <input
              id="fecha-movimiento-hasta"
              type="date"
              value={filtros.fecha_hasta}
              onChange={(event) => onFiltroChange('fecha_hasta', event.target.value)}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="tipo-movimiento" className={labelClassName}>
              Tipo de movimiento
            </label>
            <TipoMovimientoSelect
              id="tipo-movimiento"
              value={filtros.tipo_movimiento_id}
              onChange={(tipoMovimientoId) => onFiltroChange('tipo_movimiento_id', tipoMovimientoId)}
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="documento-referencia-movimiento" className={labelClassName}>
              Documento de referencia
            </label>
            <input
              id="documento-referencia-movimiento"
              type="text"
              value={filtros.documento_referencia}
              onChange={(event) => onFiltroChange('documento_referencia', event.target.value)}
              maxLength={100}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="destinatario-movimiento" className={labelClassName}>
              Destinatario
            </label>
            <input
              id="destinatario-movimiento"
              type="text"
              value={filtros.destinatario}
              onChange={(event) => onFiltroChange('destinatario', event.target.value)}
              maxLength={250}
              disabled={loading}
              className={inputClassName}
            />
          </div>
        </div>
      )}
    </form>
  )
}
