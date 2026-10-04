import ClearIcon from '@components/icons/ClearIcon'
import FilterIcon from '@components/icons/FilterIcon'
import SearchIcon from '@components/icons/SearchIcon'
import TipoPeligroSelect from '@features/emergencias/components/TipoPeligroSelect'

const buttonIconClassName = 'w-4 h-4'

const inputClassName =
  'w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:border-transparent disabled:bg-gray-50 disabled:text-gray-500'

const labelClassName = 'block text-xs font-medium text-[#1e3064] mb-1'

export default function EmergenciasBusquedaForm({
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
        <label htmlFor="consulta-emergencia" className="sr-only">
          Búsqueda por nro. SINPAD o barrio_sector_urbanizacion
        </label>
        <input
          id="consulta-emergencia"
          type="search"
          value={consulta}
          onChange={(event) => onConsultaChange(event.target.value)}
          placeholder="Buscar por nro. SINPAD o barrio_sector_urbanizacion"
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
          aria-controls="filtros-avanzados-emergencia"
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
        <div id="filtros-avanzados-emergencia" className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <div>
            <label htmlFor="numero-evaluacion" className={labelClassName}>
              Número de evaluación
            </label>
            <input
              id="numero-evaluacion"
              type="text"
              value={filtros.numero_evaluacion}
              onChange={(event) => onFiltroChange('numero_evaluacion', event.target.value)}
              maxLength={50}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="tipo-peligro" className={labelClassName}>
              Tipo de peligro
            </label>
            <TipoPeligroSelect
              inputId="tipo-peligro"
              value={filtros.tipoPeligro}
              onChange={(option) => onFiltroChange('tipoPeligro', option)}
              disabled={loading}
            />
          </div>

          <div>
            <label htmlFor="fecha-desde" className={labelClassName}>
              Fecha desde
            </label>
            <input
              id="fecha-desde"
              type="date"
              value={filtros.fecha_desde}
              onChange={(event) => onFiltroChange('fecha_desde', event.target.value)}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="fecha-hasta" className={labelClassName}>
              Fecha hasta
            </label>
            <input
              id="fecha-hasta"
              type="date"
              value={filtros.fecha_hasta}
              onChange={(event) => onFiltroChange('fecha_hasta', event.target.value)}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="localidad" className={labelClassName}>
              Localidad
            </label>
            <input
              id="localidad"
              type="text"
              value={filtros.localidad}
              onChange={(event) => onFiltroChange('localidad', event.target.value)}
              maxLength={200}
              disabled={loading}
              className={inputClassName}
            />
          </div>

          <div>
            <label htmlFor="distrito-nombre" className={labelClassName}>
              Distrito
            </label>
            <input
              id="distrito-nombre"
              type="text"
              value={filtros.distrito_nombre}
              onChange={(event) => onFiltroChange('distrito_nombre', event.target.value)}
              maxLength={50}
              disabled={loading}
              className={inputClassName}
            />
          </div>
        </div>
      )}
    </form>
  )
}
