import ClearIcon from '@components/icons/ClearIcon'
import FechaFiltroInput from '@components/FechaFiltroInput'
import SearchIcon from '@components/icons/SearchIcon'
import TipoMovimientoSelect from '@features/movimientos/components/TipoMovimientoSelect'

const buttonIconClassName = 'w-4 h-4'

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

export default function DevolucionOrigenBusquedaForm({
  filtros,
  onFiltroChange,
  onSubmit,
  onLimpiar,
  loading,
}) {
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="fecha-origen-desde" className={labelClassName}>
            Fecha desde
          </label>
          <FechaFiltroInput
            id="fecha-origen-desde"
            value={filtros.fecha_desde}
            onChange={(value) => onFiltroChange('fecha_desde', value)}
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="fecha-origen-hasta" className={labelClassName}>
            Fecha hasta
          </label>
          <FechaFiltroInput
            id="fecha-origen-hasta"
            value={filtros.fecha_hasta}
            onChange={(value) => onFiltroChange('fecha_hasta', value)}
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="documento-referencia-origen" className={labelClassName}>
            Documento de referencia
          </label>
          <input
            id="documento-referencia-origen"
            type="text"
            value={filtros.documento_referencia}
            onChange={(event) => onFiltroChange('documento_referencia', event.target.value)}
            maxLength={100}
            disabled={loading}
            className={inputClassName}
          />
        </div>

        <div>
          <label htmlFor="numero-planilla-origen" className={labelClassName}>
            Número de planilla
          </label>
          <input
            id="numero-planilla-origen"
            type="text"
            inputMode="numeric"
            value={filtros.numero_planilla}
            onChange={(event) => onFiltroChange('numero_planilla', event.target.value)}
            disabled={loading}
            className={inputClassName}
          />
        </div>

        <div className="md:col-span-2">
          <label htmlFor="tipo-movimiento-origen" className={labelClassName}>
            Tipo de movimiento
          </label>
          <TipoMovimientoSelect
            id="tipo-movimiento-origen"
            value={filtros.tipo_movimiento_id}
            onChange={(tipoMovimientoId) => onFiltroChange('tipo_movimiento_id', tipoMovimientoId)}
            disabled={loading}
            naturaleza="S"
          />
        </div>
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
