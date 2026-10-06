import Formulario2AViviendaCard from '@features/formularios2a/components/Formulario2AViviendaCard'

function LoadingState() {
  return (
    <div className="flex items-center justify-center rounded-lg border border-gray-200 bg-white py-16">
      <div className="text-center">
        <div className="mx-auto h-10 w-10 animate-spin rounded-full border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Cargando viviendas...</p>
      </div>
    </div>
  )
}

function Mensaje({ children }) {
  return (
    <section className="rounded-lg border border-gray-200 bg-white px-5 py-6 text-center text-sm text-gray-500">
      {children}
    </section>
  )
}

export default function Formulario2AViviendas({ loading, consultado, viviendas }) {
  if (loading && viviendas.length === 0) {
    return <LoadingState />
  }

  if (!consultado) {
    return <Mensaje>No se pudo obtener la búsqueda de viviendas</Mensaje>
  }

  if (viviendas.length === 0) {
    return <Mensaje>No hay viviendas registradas</Mensaje>
  }

  return (
    <ul className="space-y-4" aria-busy={loading}>
      {viviendas.map((vivienda) => (
        <li key={vivienda.vivienda_id}>
          <Formulario2AViviendaCard vivienda={vivienda} />
        </li>
      ))}
    </ul>
  )
}
