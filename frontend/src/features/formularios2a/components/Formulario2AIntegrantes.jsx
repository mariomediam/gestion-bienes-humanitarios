import { useEffect } from 'react'
import Formulario2AIntegranteCard from '@features/formularios2a/components/Formulario2AIntegranteCard'
import useIntegrantesFamilia from '@features/formularios2a/hooks/useIntegrantesFamilia'

function LoadingState() {
  return (
    <div className="flex items-center justify-center rounded-lg border border-gray-200 bg-white py-8">
      <div className="text-center">
        <div className="mx-auto h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600"></div>
        <p className="mt-3 text-sm text-gray-600">Cargando integrantes...</p>
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

export default function Formulario2AIntegrantes({ familiaId, version = 0 }) {
  const { loading, consultado, integrantes, cargarIntegrantes } = useIntegrantesFamilia(familiaId)

  useEffect(() => {
    cargarIntegrantes()
  }, [cargarIntegrantes, version])

  if (loading && integrantes.length === 0) {
    return <LoadingState />
  }

  if (!consultado) {
    return <Mensaje>No se pudo obtener la búsqueda de integrantes</Mensaje>
  }

  if (integrantes.length === 0) {
    return <Mensaje>No hay integrantes registrados</Mensaje>
  }

  return (
    <ul className="space-y-4" aria-busy={loading}>
      {integrantes.map((integrante) => (
        <li key={integrante.integrante_id}>
          <Formulario2AIntegranteCard
            integrante={integrante}
            onModificado={cargarIntegrantes}
          />
        </li>
      ))}
    </ul>
  )
}
