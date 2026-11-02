import { formatFechaHora } from '@utils/dates'
import { rolFamiliarId } from '@features/formularios2a/completarCargaFormularios2A'
import {
  textoCelda,
  textoDocumentoPersona,
  textoFechaNacimiento,
  textoNombrePersona,
  textoSexo,
} from '@features/personas/presentacion'

function texto(value) {
  if (value === null || value === undefined || value === '') return '—'
  return value
}

function unir(partes, separador = ' ') {
  const textos = partes.filter((parte) => parte !== null && parte !== undefined && parte !== '')
  if (textos.length === 0) return '—'
  return textos.join(separador)
}

function tenencia(value) {
  if (value === null || value === undefined) return '—'
  return value ? 'Sí' : 'No'
}

function lista(value) {
  return Array.isArray(value) ? value : []
}

function nombreCatalogo(mapa, id) {
  if (id === null || id === undefined || id === '') return '—'
  const fila = mapa?.get(id) ?? mapa?.get(Number(id))
  if (!fila?.nombre) return String(id)
  return fila.nombre
}

function Campo({ label, value }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs font-medium text-gray-800">{label}</dt>
      <dd className="mt-0 mb-1 text-sm text-[#1e3064] wrap-break-word">{value}</dd>
    </div>
  )
}

function tituloConDetalle(titulo, detalle) {
  if (detalle === null || detalle === undefined || detalle === '') return titulo
  return `${titulo} (${detalle})`
}

function PersonaPreview({ persona, catalogos }) {
  const datos = persona && typeof persona === 'object' ? persona : {}
  const tipoDocumento = datos.tipo_documento_id === null || datos.tipo_documento_id === undefined || datos.tipo_documento_id === ''
    ? ''
    : nombreCatalogo(catalogos.tiposDocumento, datos.tipo_documento_id)
  const documento = textoDocumentoPersona({
    nombre_tipo_documento: tipoDocumento,
    numero_documento: datos.numero_documento,
  })

  return (
    <div>
      <h5 className="text-sm font-semibold text-[#1e3064]">Persona</h5>
      <dl className="mt-3 grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
        <Campo label="Nombre" value={texto(textoNombrePersona(datos))} />
        <Campo label="Documento" value={textoCelda(documento)} />
        <Campo label="Fecha de nacimiento" value={textoCelda(textoFechaNacimiento(datos.fecha_nacimiento))} />
        <Campo label="Sexo" value={textoCelda(textoSexo(datos.sexo))} />
        <Campo label="Teléfono" value={texto(datos.telefono)} />
        <Campo label="Correo" value={texto(datos.correo)} />
      </dl>
    </div>
  )
}

function IntegrantePreview({ integrante, indice, catalogos }) {
  const rolId = rolFamiliarId(indice)
  const nombre = textoNombrePersona(integrante.persona || {})

  return (
    <section className="min-w-0 rounded-lg border border-gray-200 bg-white">
      <h4 className="border-b border-gray-200 px-5 py-4 text-sm font-semibold text-[#1e3064] wrap-break-word">
        {tituloConDetalle(`Integrante ${indice + 1}`, nombre)}
      </h4>
      <div className="space-y-4 px-5 py-4">
        <PersonaPreview persona={integrante.persona} catalogos={catalogos} />
        <div>
          <h5 className="text-sm font-semibold text-[#1e3064]">Datos del integrante</h5>
          <dl className="mt-3 grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
            <Campo label="Rol familiar" value={nombreCatalogo(catalogos.roles, rolId)} />
            <Campo label="Edad" value={texto(integrante.edad)} />
            <Campo
              label="Condición de persona"
              value={nombreCatalogo(catalogos.condicionesPersona, integrante.condicion_persona_id)}
            />
            <Campo
              label="Tipo de daño personal"
              value={nombreCatalogo(catalogos.tiposDanio, integrante.tipo_danio_personal_id)}
            />
            <Campo
              label="Grado de lesión"
              value={nombreCatalogo(catalogos.gradosLesion, integrante.grado_lesion_id)}
            />
            <Campo label="Semanas de gestación" value={texto(integrante.gestante_semanas)} />
            <Campo
              label="Tipo de discapacidad"
              value={nombreCatalogo(catalogos.tiposDiscapacidad, integrante.tipo_discapacidad_id)}
            />
            <Campo
              label="Enfermedad crónica"
              value={nombreCatalogo(catalogos.enfermedades, integrante.enfermedad_cronica_id)}
            />
          </dl>
        </div>
      </div>
    </section>
  )
}

function MedioVidaPreview({ medioVida, catalogos }) {
  const tipo = catalogos.tiposMedioVida?.get(medioVida.tipo_medio_vida_id)
    ?? catalogos.tiposMedioVida?.get(Number(medioVida.tipo_medio_vida_id))
  const categoriaId = tipo?.categoria_medio_vida_id

  return (
    <section className="min-w-0 rounded-lg border border-gray-200 bg-white">
      <h4 className="border-b border-gray-200 px-5 py-4 text-sm font-semibold text-[#1e3064] wrap-break-word">
        {tituloConDetalle('Medio de vida', tipo?.nombre)}
      </h4>
      <dl className="grid grid-cols-1 gap-x-6 gap-y-2 px-5 py-4 sm:grid-cols-2">
        <Campo
          label="Categoría de medio de vida"
          value={nombreCatalogo(catalogos.categoriasMedioVida, categoriaId)}
        />
        <Campo
          label="Tipo de medio de vida"
          value={nombreCatalogo(catalogos.tiposMedioVida, medioVida.tipo_medio_vida_id)}
        />
        <Campo label="Cantidad" value={texto(medioVida.cantidad)} />
        <Campo label="Observación" value={texto(medioVida.observacion)} />
      </dl>
    </section>
  )
}

function FamiliaPreview({ familia, indice, catalogos }) {
  return (
    <section className="min-w-0 rounded-lg border border-gray-200 bg-gray-50">
      <h3 className="border-b border-gray-200 px-5 py-4 text-sm font-semibold text-[#1e3064]">
        Familia {indice + 1}
      </h3>
      <div className="space-y-4 p-4">
        {lista(familia.integrantes).map((integrante, indiceIntegrante) => (
          <IntegrantePreview
            key={`integrante-${indiceIntegrante}`}
            integrante={integrante}
            indice={indiceIntegrante}
            catalogos={catalogos}
          />
        ))}
        {lista(familia.medios_vida).map((medioVida, indiceMedio) => (
          <MedioVidaPreview
            key={`medio-${indiceMedio}`}
            medioVida={medioVida}
            catalogos={catalogos}
          />
        ))}
      </div>
    </section>
  )
}

function ViviendaPreview({ vivienda, indice, catalogos }) {
  return (
    <section className="min-w-0 rounded-lg border border-gray-200">
      <h3 className="border-b border-gray-200 px-5 py-4 text-base font-semibold text-[#1e3064] wrap-break-word">
        {tituloConDetalle(`Vivienda ${indice + 1}`, vivienda.numero_lote)}
      </h3>
      <div className="space-y-4 p-4">
        <div className="rounded-lg border border-gray-200">
          <h4 className="border-b border-gray-200 px-5 py-3 text-sm font-semibold text-[#1e3064]">
            Datos de la vivienda
          </h4>
          <dl className="grid grid-cols-1 gap-x-6 gap-y-2 px-5 py-4 sm:grid-cols-2">
            <Campo label="Número de lote" value={texto(vivienda.numero_lote)} />
            <Campo label="Tenencia propia" value={tenencia(vivienda.tenencia_propia)} />
            <Campo
              label="Tipo de uso de instalación"
              value={nombreCatalogo(catalogos.tiposUso, vivienda.tipo_uso_instalacion_id)}
            />
            <Campo
              label="Condición de vivienda"
              value={nombreCatalogo(catalogos.condicionesVivienda, vivienda.condicion_vivienda_id)}
            />
            <Campo
              label="Material de techo"
              value={nombreCatalogo(catalogos.materialesTecho, vivienda.material_techo_id)}
            />
            <Campo
              label="Material de pared"
              value={nombreCatalogo(catalogos.materialesPared, vivienda.material_pared_id)}
            />
            <Campo
              label="Material de piso"
              value={nombreCatalogo(catalogos.materialesPiso, vivienda.material_piso_id)}
            />
          </dl>
        </div>
        {lista(vivienda.familias).map((familia, indiceFamilia) => (
          <FamiliaPreview
            key={`familia-${indiceFamilia}`}
            familia={familia}
            indice={indiceFamilia}
            catalogos={catalogos}
          />
        ))}
      </div>
    </section>
  )
}

export default function Formulario2ACargaPreview({ formulario, indice, catalogos }) {
  const datos = formulario && typeof formulario === 'object' ? formulario : {}

  return (
    <section className="bg-white rounded-lg border border-gray-200">
      <h2 className="border-b border-gray-200 px-5 py-4 text-base font-semibold text-[#1e3064] wrap-break-word">
        {tituloConDetalle(`Formulario ${indice + 1}`, datos.localidad)}
      </h2>
      <dl className="grid grid-cols-1 gap-x-6 gap-y-2 px-5 py-4 sm:grid-cols-2">
        <Campo
          label="Fecha y hora de empadronamiento"
          value={formatFechaHora(datos.fecha_empadronamiento, datos.hora_empadronamiento)}
        />
        <Campo label="Localidad" value={texto(datos.localidad)} />
        <Campo label="Barrio, sector o urbanización" value={texto(datos.barrio_sector_urbanizacion)} />
        <Campo label="Centro poblado" value={texto(datos.centro_poblado)} />
        <Campo label="Caserío" value={texto(datos.caserio)} />
        <Campo label="Anexo" value={texto(datos.anexo)} />
        <Campo label="Calle o manzana" value={texto(datos.calle_manzana)} />
        <Campo label="Edificio, piso o departamento" value={texto(datos.edificio_piso_dpto)} />
        <Campo label="Otros datos de ubicación" value={texto(datos.otros_ubicacion)} />
        <Campo
          label="Número de hoja y total de hojas"
          value={unir([datos.numero_hoja, datos.total_hojas], ' / ')}
        />
      </dl>
      <div className="space-y-4 px-5 pb-5">
        {lista(datos.viviendas).map((vivienda, indiceVivienda) => (
          <ViviendaPreview
            key={`vivienda-${indiceVivienda}`}
            vivienda={vivienda}
            indice={indiceVivienda}
            catalogos={catalogos}
          />
        ))}
      </div>
    </section>
  )
}
