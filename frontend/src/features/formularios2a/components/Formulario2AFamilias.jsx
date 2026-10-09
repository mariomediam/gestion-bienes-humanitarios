import { useEffect } from 'react'
import Formulario2AFamiliaCard from '@features/formularios2a/components/Formulario2AFamiliaCard'
import useFamiliasVivienda from '@features/formularios2a/hooks/useFamiliasVivienda'

function LoadingState() {
  return (
    <div className="flex items-center justify-center rounded-lg border border-gray-200 bg-white py-8">
      <div className="text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600"></div>
        <p className="mt-3 text-sm text-gray-600">Cargando familias...</p>
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

export default function Formulario2AFamilias({ viviendaId, version = 0 }) {
  const { loading, consultado, familias, cargarFamilias } = useFamiliasVivienda(viviendaId)

  useEffect(() => {
    cargarFamilias()
  }, [cargarFamilias, version])

  if (loading && familias.length === 0) {
    return <LoadingState />
  }

  if (!consultado) {
    return <Mensaje>No se pudo obtener la búsqueda de familias</Mensaje>
  }

  if (familias.length === 0) {
    return <Mensaje>No hay familias registradas</Mensaje>
  }

  return (
    <ul className="space-y-4" aria-busy={loading}>
      {familias.map((familia) => (
        <li key={familia.familia_id}>
          <Formulario2AFamiliaCard familia={familia} onEliminada={cargarFamilias} />
        </li>
      ))}
    </ul>
  )
}
