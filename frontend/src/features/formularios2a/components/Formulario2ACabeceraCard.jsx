import { useState } from 'react'
import PencilIcon from '@components/icons/PencilIcon'
import Formulario2AFormModal from '@features/formularios2a/components/Formulario2AFormModal'
import { formatFechaHora } from '@utils/dates'

function texto(value) {
  if (value === null || value === undefined || value === '') return '—'
  return value
}

function unir(partes, separador = ' ') {
  const textos = partes.filter((parte) => parte !== null && parte !== undefined && parte !== '')
  if (textos.length === 0) return '—'
  return textos.join(separador)
}

function Campo({ label, value }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs font-medium text-gray-800">{label}</dt>
      <dd className="mt-0 mb-1 text-sm text-[#1e3064] wrap-break-word">{value}</dd>
    </div>
  )
}

export default function Formulario2ACabeceraCard({ formulario, onSaved }) {
  const [edicionAbierta, setEdicionAbierta] = useState(false)

  function handleSaved(saved) {
    setEdicionAbierta(false)
    onSaved?.(saved)
  }

  return (
    <section className="bg-white rounded-lg border border-gray-200">
      <div className="flex items-center justify-between gap-4 px-5 py-4 border-b border-gray-200">
        <h1 className="text-base font-semibold text-[#1e3064]">Datos del formulario EDAN 2A</h1>
        <button
          type="button"
          onClick={() => setEdicionAbierta(true)}
          className="inline-flex shrink-0 items-center gap-2 whitespace-nowrap px-4 py-2 text-sm font-medium text-[#1e3064] bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors"
        >
          <PencilIcon className="w-4 h-4" />
          Modificar
        </button>
      </div>

      <dl className="grid grid-cols-1 gap-x-6 gap-y-10 px-5 py-4 sm:grid-cols-2 md:grid-cols-2">
        <Campo
          label="Código SINPAD y tipo de peligro"
          value={unir([formulario.codigo_sinpad, formulario.nombre_tipo_peligro])}
        />
        <Campo
          label="Fecha y hora de empadronamiento"
          value={formatFechaHora(formulario.fecha_empadronamiento, formulario.hora_empadronamiento)}
        />
        <Campo label="Distrito" value={texto(formulario.distrito_nombre)} />
        <Campo label="Localidad" value={texto(formulario.localidad)} />
        <Campo label="Barrio, sector o urbanización" value={texto(formulario.barrio_sector_urbanizacion)} />
        <Campo label="Centro poblado" value={texto(formulario.centro_poblado)} />
        <Campo label="Caserío" value={texto(formulario.caserio)} />
        <Campo label="Anexo" value={texto(formulario.anexo)} />
        <Campo label="Calle o manzana" value={texto(formulario.calle_manzana)} />
        <Campo label="Edificio, piso o departamento" value={texto(formulario.edificio_piso_dpto)} />
        <Campo label="Otros datos de ubicación" value={texto(formulario.otros_ubicacion)} />
        <Campo
          label="Número de hoja y total de hojas"
          value={unir([formulario.numero_hoja, formulario.total_hojas], ' / ')}
        />
        <Campo label="Evaluador" value={texto(formulario.evaluador_nombre)} />
      </dl>

      <Formulario2AFormModal
        key={edicionAbierta ? formulario.formulario_2a_id : 'cerrado'}
        isOpen={edicionAbierta}
        formulario={edicionAbierta ? formulario : null}
        codigoSinpad={formulario.codigo_sinpad ?? ''}
        onClose={() => setEdicionAbierta(false)}
        onSaved={handleSaved}
      />
    </section>
  )
}
