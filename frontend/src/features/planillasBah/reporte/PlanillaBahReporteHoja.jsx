import {
  FILAS_PLANILLA,
  GUION_FILA_VACIA,
  ANCHO_COLUMNA_FIRMA,
  anchosColumnas,
  claseCategoria,
  formatFechaEntregaReporte,
  gruposPorCategoria,
  textoCantidadImpresa,
  textoNumeroPlanilla,
  textoReporte,
} from '@features/planillasBah/reporte/planillaBahReporte'

function Dato({ label, valor, className = '' }) {
  return (
    <div className={`bah-dato ${className}`}>
      <span className="bah-dato-label">{label}</span>
      <span className="bah-dato-valor">{textoReporte(valor)}</span>
    </div>
  )
}

function FilaPlanilla({ numero, reporte, grupos }) {
  const conDatos = numero === 1

  return (
    <tr>
      <td>{numero}</td>
      <td className={conDatos ? 'bah-texto' : 'bah-guion'}>
        {conDatos ? textoReporte(reporte.direccion) : GUION_FILA_VACIA}
      </td>
      <td className={conDatos ? 'bah-texto' : 'bah-guion'}>
        {conDatos ? textoReporte(reporte.integrante_receptor_nombre) : GUION_FILA_VACIA}
      </td>
      <td className={conDatos ? 'bah-texto' : 'bah-guion'}>
        {conDatos ? textoReporte(reporte.integrante_receptor_doc_ident) : GUION_FILA_VACIA}
      </td>
      <td className={conDatos ? undefined : 'bah-guion'}>
        {conDatos ? textoReporte(reporte.nro_integrantes_familia) : GUION_FILA_VACIA}
      </td>
      {grupos.flatMap((grupo) => grupo.bienes.map(({ bien, indice }) => (
        <td key={indice}>{conDatos ? textoCantidadImpresa(bien) : ''}</td>
      )))}
      <td />
    </tr>
  )
}

export default function PlanillaBahReporteHoja({ reporte }) {
  const grupos = gruposPorCategoria(reporte.bienes)
  const anchos = anchosColumnas(grupos.reduce((total, grupo) => total + grupo.bienes.length, 0))
  const filas = Array.from({ length: FILAS_PLANILLA }, (_, indice) => indice + 1)

  return (
    <article className="bah-hoja">
      <div className="bah-titulo-fila">
        <h1 className="bah-titulo">PLANILLA DE ENTREGA DE BIENES DE AYUDA HUMANITARIA</h1>
        <p className="bah-numero">
          <span className="bah-numero-label">N°:</span>
          <span>{textoNumeroPlanilla(reporte.numero_planilla, reporte.anio_planilla)}</span>
        </p>
      </div>

      <div className="bah-cabecera">
        <Dato className="bah-span-2" label="REGIÓN:" valor={reporte.region_nombre} />
        <Dato className="bah-span-2" label="PROVINCIA:" valor={reporte.provincia_nombre} />
        <Dato className="bah-span-2" label="DISTRITO:" valor={reporte.distrito_nombre} />
        <Dato className="bah-span-2" label="LOCALIDAD:" valor={reporte.localidad} />
        <Dato className="bah-span-2" label="BARRIO:" valor={reporte.barrio_sector_urbanizacion} />
        <Dato className="bah-span-2" label="CÓDIGO SINPAD:" valor={reporte.codigo_sinpad} />
        <Dato className="bah-span-3" label="ENTREGADO POR: a) GORE:" valor={reporte.entregado_por_gore} />
        <Dato className="bah-span-3" label="b) MUNICIP. PROV:" valor={reporte.municip_prov} />
        <Dato className="bah-span-2" label="c) MUNICIP. DIST." valor={reporte.municip_dist} />
        <Dato className="bah-span-2" label="PELIGRO:" valor={reporte.tipo_peligro_nombre} />
        <Dato className="bah-span-2" label="FECHA DE ENTREGA:" valor={formatFechaEntregaReporte(reporte.planilla_fecha_entrega)} />
      </div>

      <table className="bah-tabla">
        <caption className="bah-sr">
          Planilla de entrega de bienes de ayuda humanitaria
        </caption>
        <colgroup>
          {anchos.map((ancho, indice) => (
            <col key={indice} style={{ width: ancho }} />
          ))}
          <col style={{ width: ANCHO_COLUMNA_FIRMA }} />
        </colgroup>
        <thead>
          <tr>
            <th rowSpan={2} scope="col">N°</th>
            <th className="bah-ubicacion" scope="col">UBICACIÓN</th>
            <th className="bah-jefe" colSpan={3} scope="colgroup">
              JEFE DE FAMILIA O PERSONA QUE RESPONDE
            </th>
            {grupos.map((grupo) => (
              <th
                key={`${grupo.nombre ?? 'sin-categoria'}-${grupo.bienes[0].indice}`}
                className={claseCategoria(grupo.nombre)}
                colSpan={grupo.bienes.length}
                scope="colgroup"
              >
                {textoReporte(grupo.nombre)}
              </th>
            ))}
            <th rowSpan={2} scope="col">
              <span >Firmo en señal de conformidad con lo entregado</span>
            </th>
          </tr>
          <tr>
            <th className="bah-ubicacion" scope="col">Dirección</th>
            <th className="bah-jefe" scope="col">Apellidos y Nombres</th>
            <th className="bah-jefe" scope="col">Doc. Ident.</th>
            <th className="bah-jefe" scope="col">N° de integrantes en su familia</th>
            {grupos.flatMap((grupo) => grupo.bienes.map(({ bien, indice }) => (
              <th
                key={indice}
                className={`bah-th-bien ${claseCategoria(grupo.nombre)}`}
                scope="col"
              >
                <span className="bah-vertical">{textoReporte(bien.bien_nombre)}</span>
              </th>
            )))}
          </tr>
        </thead>
        <tbody>
          {filas.map((numero) => (
            <FilaPlanilla key={numero} numero={numero} reporte={reporte} grupos={grupos} />
          ))}
        </tbody>
      </table>

      <div className="bah-cierre">   
        <p className="bah-responsable">
          Responsable de Entrega:
          <span className="bah-responsable-linea" />
        </p>
        <div className="bah-detalle">
          <p>(*) Detallar:</p>
          <p>(**) Puede consistir en lo siguiente:</p>
          <p>Menaje: Cuchara, cuchillo, plato, vaso, olla</p>
          <p>Herramientas: Pico, Pala</p>
        </div>
      </div>

      <div className="bah-firmas">
        <div>
          <p className="bah-firma-nombre" />
          <p>Alcalde Dist/Prov o Representante</p>
        </div>
        <div>
          <p className="bah-firma-nombre">{textoReporte(reporte.encargado_almacen_nombre)}</p>
          <p className="mt-0">Encargado del Almacén</p>
        </div>
        <div>
          <p className="bah-firma-nombre" />
          <p>Representante de la Comunidad</p>
        </div>
      </div>

      <p className="bah-leyenda">
        Nota: (i) La información consignada en el presente formulario tiene carácter de
        Declaración Jurada. (ii) Las personas y funcionarios que ingresen información falsa
        en este formulario serán pasibles de las acciones administrativas y penales, en el
        caso de esta última resulta de aplicación lo previsto en el artículo 438 del Código
        Penal. (iii) Toda la información solicitada en la presente Planilla es de carácter
        obligatorio y deberá ser llenada de forma clara y legible.
      </p>
    </article>
  )
}
