import { useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import Formulario2ACabeceraCard from '@features/formularios2a/components/Formulario2ACabeceraCard'
import Formulario2AViviendas from '@features/formularios2a/components/Formulario2AViviendas'
import useFormulario2ADetalle from '@features/formularios2a/hooks/useFormulario2ADetalle'
import useViviendasFormulario2A from '@features/formularios2a/hooks/useViviendasFormulario2A'

function LoadingState() {
  return (
    <div className="flex items-center justify-center py-24">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Cargando formulario EDAN 2A...</p>
      </div>
    </div>
  )
}

export default function Formulario2ADetallePage() {
  const { formulario2aId } = useParams()
  const { loading, formulario, reemplazarFormulario } = useFormulario2ADetalle(formulario2aId)
  const {
    loading: cargandoViviendas,
    consultado,
    viviendas,
    cargarViviendas,
  } = useViviendasFormulario2A(formulario2aId)

  useEffect(() => {
    cargarViviendas()
  }, [cargarViviendas])

  return (
    <div className="space-y-6">
      <Link
        to="/formularios-2A"
        className="inline-flex text-sm font-medium text-[#1e3064] hover:underline focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 rounded-sm"
      >
        Volver al listado
      </Link>

      {loading && <LoadingState />}
      {!loading && formulario && (
        <>
          <Formulario2ACabeceraCard formulario={formulario} onSaved={reemplazarFormulario} />
          <Formulario2AViviendas
            loading={cargandoViviendas}
            consultado={consultado}
            viviendas={viviendas}
          />
        </>
      )}
    </div>
  )
}
