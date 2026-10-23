function texto(value) {
  if (value === null || value === undefined || value === '') {
    return '—'
  }

  return String(value)
}

export default function KardexBienInfo({ bien, loading }) {
  return (
    <section className="bg-white rounded-lg border border-gray-200 p-5">
      <h2 className="text-base font-semibold text-[#1e3064]">Bien</h2>
      <dl className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div>
          <dt className="text-xs font-medium text-[#1e3064]">Nombre</dt>
          <dd className="mt-1 text-sm text-gray-800">{loading ? 'Cargando...' : texto(bien?.nombre)}</dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-[#1e3064]">Categoría</dt>
          <dd className="mt-1 text-sm text-gray-800">
            {loading ? 'Cargando...' : texto(bien?.categoria_bien_nombre)}
          </dd>
        </div>
        <div>
          <dt className="text-xs font-medium text-[#1e3064]">Unidad de medida</dt>
          <dd className="mt-1 text-sm text-gray-800">
            {loading ? 'Cargando...' : texto(bien?.unidad_medida_nombre)}
          </dd>
        </div>
      </dl>
    </section>
  )
}
