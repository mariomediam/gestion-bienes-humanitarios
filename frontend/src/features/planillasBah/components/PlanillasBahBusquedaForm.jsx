import ClearIcon from '@components/icons/ClearIcon'
import FilterIcon from '@components/icons/FilterIcon'
import SearchIcon from '@components/icons/SearchIcon'

const buttonIconClassName = 'w-4 h-4'

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

export default function PlanillasBahBusquedaForm({
  consulta,
  onConsultaChange,
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
        <label htmlFor="consulta-planilla-bah" className="sr-only">
          Búsqueda por nombre del bien o número de planilla
        </label>
        <input
          id="consulta-planilla-bah"
          type="search"
          value={consulta}
          onChange={(event) => onConsultaChange(event.target.value)}
          placeholder="Buscar por nombre del bien o número de planilla"
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
          aria-controls="filtros-avanzados-planilla-bah"
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
        <div id="filtros-avanzados-planilla-bah" className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div>
            <label htmlFor="anio-planilla-bah" className={labelClassName}>
              Año de planilla
            </label>
            <input
              id="anio-planilla-bah"
              type="text"
              inputMode="numeric"
              value={filtros.anio_planilla}
              onChange={(event) => onFiltroChange('anio_planilla', event.target.value)}
              maxLength={10}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="codigo-sinpad-planilla-bah" className={labelClassName}>
              Código SINPAD
            </label>
            <input
              id="codigo-sinpad-planilla-bah"
              type="text"
              value={filtros.codigo_sinpad}
              onChange={(event) => onFiltroChange('codigo_sinpad', event.target.value)}
              maxLength={30}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="barrio-planilla-bah" className={labelClassName}>
              Barrio/Sector/Urbanización
            </label>
            <input
              id="barrio-planilla-bah"
              type="text"
              value={filtros.barrio_sector_urbanizacion}
              onChange={(event) => onFiltroChange('barrio_sector_urbanizacion', event.target.value)}
              maxLength={250}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="documento-referencia-planilla-bah" className={labelClassName}>
              Documento de referencia
            </label>
            <input
              id="documento-referencia-planilla-bah"
              type="text"
              value={filtros.documento_referencia}
              onChange={(event) => onFiltroChange('documento_referencia', event.target.value)}
              maxLength={100}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="fecha-entrega-desde" className={labelClassName}>
              Fecha de entrega desde
            </label>
            <input
              id="fecha-entrega-desde"
              type="date"
              value={filtros.fecha_desde}
              onChange={(event) => onFiltroChange('fecha_desde', event.target.value)}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="fecha-entrega-hasta" className={labelClassName}>
              Fecha de entrega hasta
            </label>
            <input
              id="fecha-entrega-hasta"
              type="date"
              value={filtros.fecha_hasta}
              onChange={(event) => onFiltroChange('fecha_hasta', event.target.value)}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div className="md:col-span-2">
            <label htmlFor="receptor-planilla-bah" className={labelClassName}>
              Nombre del receptor
            </label>
            <input
              id="receptor-planilla-bah"
              type="text"
              value={filtros.integrante_receptor_nombre}
              onChange={(event) => onFiltroChange('integrante_receptor_nombre', event.target.value)}
              maxLength={252}
              disabled={loading}
              className={inputClassName}
            />
          </div>
        </div>
      )}
    </form>
  )
}
