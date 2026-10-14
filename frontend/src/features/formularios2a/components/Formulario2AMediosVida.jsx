import { useEffect } from 'react'
import Formulario2AMedioVidaCard from '@features/formularios2a/components/Formulario2AMedioVidaCard'
import useMediosVidaFamilia from '@features/formularios2a/hooks/useMediosVidaFamilia'

function LoadingState() {
  return (
    <div className="flex items-center justify-center rounded-lg border border-gray-200 bg-white py-8">
      <div className="text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600"></div>
        <p className="mt-3 text-sm text-gray-600">Cargando medios de vida...</p>
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

export default function Formulario2AMediosVida({ familiaId, version = 0 }) {
  const { loading, consultado, mediosVida, cargarMediosVida } = useMediosVidaFamilia(familiaId)

  useEffect(() => {
    cargarMediosVida()
  }, [cargarMediosVida, version])

  if (loading && mediosVida.length === 0) {
    return <LoadingState />
  }

  if (!consultado) {
    return <Mensaje>No se pudo obtener la búsqueda de medios de vida</Mensaje>
  }

  if (mediosVida.length === 0) {
    return <Mensaje>No hay medios de vida registrados</Mensaje>
  }

  return (
    <ul className="space-y-4" aria-busy={loading}>
      {mediosVida.map((medioVida) => (
        <li key={medioVida.medio_vida_id}>
          <Formulario2AMedioVidaCard
            medioVida={medioVida}
            onModificado={cargarMediosVida}
          />
        </li>
      ))}
    </ul>
  )
}
