const GRUPOS_ETARIOS = [
  ['menor_1', 'Menor a 1'],
  ['01_04', '01 a 04'],
  ['05_09', '05 a 09'],
  ['10_14', '10 a 14'],
  ['15_17', '15 a 17'],
  ['18_49', '18 a 49'],
  ['50_59', '50 a 59'],
  ['60_mas', '60 a más'],
]

const ANCHOS = [
  '3%',
  '1.7%',
  '1.7%',
  '2.1%',
  '2.1%',
  '2.1%',
  '2.2%',
  '2.1%',
  '2.2%',
  '2.2%',
  '2.2%',
  '12.8%',
  '2.4%',
  '3.2%',
  '6.2%',
  '5.2%',
  '2%',
  '2%',
  '2%',
  ...Array(16).fill('1.35%'),
  '2.4%',
  '2.6%',
  '2.6%',
  '2.3%',
  '2%',
  '2.3%',
  '2%',
  '2.8%',
]

function formatFecha(fecha) {
  if (!fecha) return ''
  const [year, month, day] = String(fecha).slice(0, 10).split('-')
  if (!year || !month || !day) return ''
  return `${day}/${month}/${year}`
}

function formatHora(hora) {
  if (!hora) return ''
  return String(hora).slice(0, 5)
}

function texto(valor) {
  if (valor === null || valor === undefined || valor === '') return ''
  return String(valor)
}

function marca(activa) {
  return activa ? 'X' : ''
}

function marcaEtaria(fila, grupo, sexo) {
  if (!fila || fila.grupo_etario !== grupo || fila.sexo !== sexo) return ''
  return '1'
}

function Dato({ label, valor, className = '' }) {
  return (
    <div className={`reporte-dato ${className}`}>
      <span className="reporte-dato-label">{label}</span>
      <span className="reporte-dato-valor">{texto(valor)}</span>
    </div>
  )
}

function Vertical({ children }) {
  return <span className="vertical">{children}</span>
}

function FilaDatos({ fila }) {
  return (
    <tr>
      <td>{texto(fila?.numero_lote)}</td>
      <td>{marca(fila?.tenencia_si)}</td>
      <td>{marca(fila?.tenencia_no)}</td>
      <td>{marca(fila?.uso_vivienda)}</td>
      <td>{marca(fila?.uso_medio_vida)}</td>
      <td>{marca(fila?.condicion_afectada)}</td>
      <td>{marca(fila?.condicion_inhabitable)}</td>
      <td>{marca(fila?.condicion_destruida)}</td>
      <td>{texto(fila?.material_techo)}</td>
      <td>{texto(fila?.material_pared)}</td>
      <td>{texto(fila?.material_piso)}</td>
      <td className="nombres">{texto(fila?.apellidos_nombres)}</td>
      <td>{texto(fila?.edad)}</td>
      <td>{texto(fila?.tipo_documento)}</td>
      <td>{texto(fila?.numero_documento)}</td>
      <td>{texto(fila?.condicion_persona)}</td>
      <td>{texto(fila?.danio_fallecido)}</td>
      <td>{texto(fila?.danio_lesionado)}</td>
      <td>{texto(fila?.danio_desaparecido)}</td>
      {GRUPOS_ETARIOS.map(([grupo]) => (
        ['M', 'F'].map((sexo) => (
          <td key={`${grupo}-${sexo}`}>{marcaEtaria(fila, grupo, sexo)}</td>
        ))
      ))}
      <td>{texto(fila?.gestante_semanas)}</td>
      <td>{texto(fila?.discapacidad)}</td>
      <td>{texto(fila?.enfermedad_cronica)}</td>
      <td>{texto(fila?.comercio_tipo)}</td>
      <td>{texto(fila?.comercio_cantidad)}</td>
      <td>{texto(fila?.turismo_tipo)}</td>
      <td>{texto(fila?.turismo_cantidad)}</td>
      <td>{texto(fila?.otros)}</td>
    </tr>
  )
}

export default function Formulario2AReporteHoja({ reporte, filas }) {
  return (
    <article className="reporte-hoja">
      <h1 className="reporte-titulo">ANEXO N° 03</h1>
      <p className="reporte-subtitulo">
        FORMULARIO DE CAMPO 2A: EMPADRONAMIENTO FAMILIAR Y MEDIOS DE VIDA
      </p>
      <p className="reporte-ambito">(Gobiernos Locales)</p>

      <div className="reporte-cabecera">
        <Dato className="span-6" label="EVALUACIÓN N°:" valor={reporte.numero_evaluacion} />
        <div className="span-3" aria-hidden="true" />
        <Dato className="reporte-col-registro" label="CÓDIGO SINPAD N°:" valor={reporte.codigo_sinpad} />
        <Dato className="span-3" label="Tipo de Peligro:" valor={reporte.tipo_peligro} />
        <Dato className="span-3" label="Fecha de Emergencia:" valor={formatFecha(reporte.fecha_emergencia)} />
        <Dato
          className="span-3"
          label="Hora de Ocurrencia estimada:"
          valor={formatHora(reporte.hora_ocurrencia_estimada)}
        />
        <Dato
          className="reporte-col-registro"
          label="Fecha del Empadronamiento:"
          valor={formatFecha(reporte.fecha_empadronamiento)}
        />
        <Dato className="span-2" label="Departamento:" valor={reporte.departamento} />
        <Dato className="span-2" label="Provincia:" valor={reporte.provincia} />
        <Dato className="span-2" label="Distrito:" valor={reporte.distrito} />
        <Dato className="span-3" label="Localidad:" valor={reporte.localidad} />
        <Dato
          className="reporte-col-registro"
          label="Hora del Empadronamiento:"
          valor={formatHora(reporte.hora_empadronamiento)}
        />
        <Dato
          className="span-4"
          label="Barrio/Sector/Urbanización:"
          valor={reporte.barrio_sector_urbanizacion}
        />
        <Dato className="span-3" label="Calle/Manzana:" valor={reporte.calle_manzana} />
        <Dato className="span-3" label="Edificio/Piso/Dpto.:" valor={reporte.edificio_piso_dpto} />
        <div className="reporte-dato span-2">
          <span className="reporte-dato-label">Número de hoja:</span>
          <span className="reporte-hoja-numero">{texto(reporte.numero_hoja)}</span>
        </div>
        <Dato className="span-3" label="Centro Poblado:" valor={reporte.centro_poblado} />
        <Dato className="span-3" label="Caserío:" valor={reporte.caserio} />
        <Dato className="span-3" label="Anexo:" valor={reporte.anexo} />
        <Dato className="span-3" label="Otros:" valor={reporte.otros_ubicacion} />
      </div>

      <table className="reporte-tabla">
        <caption className="reporte-sr">
          Formulario de campo 2A, empadronamiento familiar y medios de vida
        </caption>
        <colgroup>
          {ANCHOS.map((ancho, indice) => (
            <col key={indice} style={{ width: ancho }} />
          ))}
        </colgroup>
        <thead>
          <tr>
            <th className="viv" colSpan={11} scope="colgroup">I. INFORMACIÓN DE VIVIENDA</th>
            <th className="fam" colSpan={24} scope="colgroup">II. INFORMACIÓN POR FAMILIA</th>
            <th className="sal" colSpan={3} scope="colgroup">
              III. INFORMACIÓN ADICIONAL POR FAMILIA (Salud)
            </th>
            <th className="med" colSpan={5} scope="colgroup">IV. Medio de VIDA local</th>
          </tr>
          <tr>
            <th className="viv" rowSpan={3} scope="col">Nº Lote</th>
            <th className="viv" colSpan={2} scope="colgroup">TENENCIA</th>
            <th className="viv" colSpan={2} scope="colgroup">
              CONDICIÓN DE USO DE LA INSTALACIÓN
            </th>
            <th className="viv" colSpan={3} scope="colgroup">
              Condición de la vivienda post desastre
            </th>
            <th className="viv" colSpan={3} scope="colgroup">
              Tipo de Material de la Vivienda (Ver Tabla de Referencia)
            </th>
            <th className="fam" colSpan={4} scope="colgroup">
              JEFE (A) DE FAMILIA O PERSONA QUE RESPONDE (Empadronar al total de los miembros de la familia)
            </th>
            <th className="fam" colSpan={4} scope="colgroup">VIDA Y SALUD (indicar con números)</th>
            <th className="fam" colSpan={16} scope="colgroup">
              COMPOSICIÓN FAMILIAR POR GRUPOS ETARIOS / AÑOS (Indicar con números)
            </th>
            <th className="sal" colSpan={3} scope="colgroup">GRUPOS VULNERABLES</th>
            <th className="med" colSpan={2} scope="colgroup">COMERCIO</th>
            <th className="med" colSpan={2} scope="colgroup">TURISMO</th>
            <th className="med" rowSpan={3} scope="col">
              <Vertical>Otros tipos de actividad</Vertical>
            </th>
          </tr>
          <tr>
            <th className="viv" colSpan={2}>Propia</th>
            <th className="viv" rowSpan={2} scope="col"><Vertical>Vivienda</Vertical></th>
            <th className="viv" rowSpan={2} scope="col"><Vertical>Medios de Vida</Vertical></th>
            <th className="viv" rowSpan={2} scope="col"><Vertical>Afectada</Vertical></th>
            <th className="viv" rowSpan={2} scope="col"><Vertical>Inhabitable</Vertical></th>
            <th className="viv" rowSpan={2} scope="col"><Vertical>Destruida</Vertical></th>
            <th className="viv" rowSpan={2} scope="col"><Vertical>TECHO</Vertical></th>
            <th className="viv" rowSpan={2} scope="col"><Vertical>PAREDES</Vertical></th>
            <th className="viv" rowSpan={2} scope="col"><Vertical>PISO</Vertical></th>
            <th className="fam" rowSpan={2} scope="col">APELLIDOS, NOMBRES</th>
            <th className="fam" rowSpan={2} scope="col">EDAD</th>
            <th className="fam" colSpan={2} scope="colgroup">DOCUMENTO DE IDENTIDAD</th>
            <th className="fam" rowSpan={2} scope="col"><Vertical>Condición</Vertical></th>
            <th className="fam" colSpan={3} scope="colgroup">Daños Personales</th>
            {GRUPOS_ETARIOS.map(([grupo, etiqueta]) => (
              <th key={grupo} className="fam" colSpan={2} scope="colgroup">{etiqueta}</th>
            ))}
            <th className="sal" rowSpan={2} scope="col">
              <Vertical>Gestante (Semanas)</Vertical>
            </th>
            <th className="sal" rowSpan={2} scope="col">
              <Vertical>
                Personas con discapacidad
                <br />
                (Especificar el Número de la Tabla de Referencia)
              </Vertical>
            </th>
            <th className="sal" rowSpan={2} scope="col">
              <Vertical>
                Tipo de Enfermedad crónica
                <br />
                (Especificar el Número de la Tabla de Referencia)
              </Vertical>
            </th>
            <th className="med" rowSpan={2} scope="col">
              <Vertical>
                Tipo de actividad de comercio
                <br />
                (ver tabla de detalle)
              </Vertical>
            </th>
            <th className="med" rowSpan={2} scope="col"><Vertical>Tipo (Unid)</Vertical></th>
            <th className="med" rowSpan={2} scope="col">
              <Vertical>
                Tipo de actividad Turística
                <br />
                (ver tabla de detalle)
              </Vertical>
            </th>
            <th className="med" rowSpan={2} scope="col"><Vertical>Tipo (Unid)</Vertical></th>
          </tr>
          <tr>
            <th className="viv" scope="col">SI</th>
            <th className="viv" scope="col">NO</th>
            <th className="fam" scope="col">TIPO</th>
            <th className="fam" scope="col">NÚMERO</th>
            <th className="fam" scope="col"><Vertical>Fallecido (*)</Vertical></th>
            <th className="fam" scope="col"><Vertical>Lesionado (Herido)</Vertical></th>
            <th className="fam" scope="col"><Vertical>Desaparecido</Vertical></th>
            {GRUPOS_ETARIOS.map(([grupo]) => (
              ['M', 'F'].map((sexo) => (
                <th key={`${grupo}-${sexo}`} className="fam" scope="col">{sexo}</th>
              ))
            ))}
          </tr>
        </thead>
        <tbody>
          {filas.map((fila, indice) => (
            <FilaDatos key={fila?.apellidos_nombres ? `${fila.apellidos_nombres}-${indice}` : `vacia-${indice}`} fila={fila} />
          ))}
        </tbody>
      </table>

      <div className="reporte-notas">
        <p>(*) Sírvase indicar su ubicación.</p>
        <p>Nota: Si se observan daños en los Medios de Vida, pasar al Formulario 2B</p>
      </div>

      <p className="reporte-institucion">
        Institución:
        {' '}
        <span className="reporte-dato-valor">{texto(reporte.institucion)}</span>
      </p>

      <div className="reporte-firmas">
        <div>
          <p className="reporte-firma-nombre">{texto(reporte.evaluador_nombre)}</p>
          <p>Nombre, Apellidos y Firma del (la) Evaluador(a) EDAN PERÚ</p>
          <p className="reporte-firma-dni">D.N.I. N°</p>
        </div>
        <div>
          <p className="reporte-firma-nombre" />
          <p>Firma y Sello Jefe(a) de la Oficina de Defensa Civil o la que haga sus veces</p>
          <p className="reporte-firma-dni">D.N.I. N°</p>
        </div>
        <div>
          <p className="reporte-firma-nombre" />
          <p>Firma y Sello del Alcalde(sa)</p>
          <p className="reporte-firma-dni">D.N.I. N°</p>
        </div>
      </div>

      <p className="reporte-leyenda">
        Los funcionarios que ingresen información falsa en este y otros formularios EDAN PERÚ,
        serán sancionados de acuerdo a lo dispuesto en el Artículo 20 de la Ley N° 29664 y la
        Ley N° 27444, Ley del Procedimiento Administrativo General.
      </p>
    </article>
  )
}
