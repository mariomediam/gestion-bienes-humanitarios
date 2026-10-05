import ClearIcon from '@components/icons/ClearIcon'
import DistritoSelect from '@components/DistritoSelect'
import FilterIcon from '@components/icons/FilterIcon'
import SearchIcon from '@components/icons/SearchIcon'
import TipoPeligroSelect from '@features/emergencias/components/TipoPeligroSelect'

const buttonIconClassName = 'w-4 h-4'

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

export default function Formularios2ABusquedaForm({
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
        <label htmlFor="consulta-formulario-2a" className="sr-only">
          Búsqueda por nro. codigo_sinpad o barrio_sector_urbanizacion
        </label>
        <input
          id="consulta-formulario-2a"
          type="search"
          value={consulta}
          onChange={(event) => onConsultaChange(event.target.value)}
          placeholder="Buscar por nro. codigo_sinpad o barrio_sector_urbanizacion"
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
          aria-controls="filtros-avanzados-formulario-2a"
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
        <div id="filtros-avanzados-formulario-2a" className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div>
            <label htmlFor="tipo-peligro-formulario-2a" className={labelClassName}>
              Tipo de peligro
            </label>
            <TipoPeligroSelect
              inputId="tipo-peligro-formulario-2a"
              value={filtros.tipoPeligro}
              onChange={(option) => onFiltroChange('tipoPeligro', option)}
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="distrito-formulario-2a" className={labelClassName}>
              Distrito
            </label>
            <DistritoSelect
              inputId="distrito-formulario-2a"
              value={filtros.distrito}
              onChange={(option) => onFiltroChange('distrito', option)}
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="fecha-empadronamiento-desde" className={labelClassName}>
              Fecha de empadronamiento desde
            </label>
            <input
              id="fecha-empadronamiento-desde"
              type="date"
              value={filtros.fecha_desde}
              onChange={(event) => onFiltroChange('fecha_desde', event.target.value)}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="fecha-empadronamiento-hasta" className={labelClassName}>
              Fecha de empadronamiento hasta
            </label>
            <input
              id="fecha-empadronamiento-hasta"
              type="date"
              value={filtros.fecha_hasta}
              onChange={(event) => onFiltroChange('fecha_hasta', event.target.value)}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="localidad-formulario-2a" className={labelClassName}>
              Localidad
            </label>
            <input
              id="localidad-formulario-2a"
              type="text"
              value={filtros.localidad}
              onChange={(event) => onFiltroChange('localidad', event.target.value)}
              maxLength={200}
              disabled={loading}
              className={inputClassName}
            />
          </div>
        </div>
      )}
    </form>
  )
}
