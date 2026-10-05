const HEADER_COLUMNS = [
  { key: 'emergencia_id', label: 'Id de emergencia' },
  { key: 'numero_evaluacion', label: 'Número de evaluación' },
  { key: 'codigo_sinpad', label: 'Código SINPAD' },
  { key: 'tipo_peligro_id', label: 'Id tipo de peligro' },
  { key: 'nombre_tipo_peligro', label: 'Tipo de peligro' },
  { key: 'fecha_emergencia', label: 'Fecha de emergencia', kind: 'date' },
  { key: 'hora_ocurrencia_estimada', label: 'Hora estimada', kind: 'time' },
  { key: 'esta_activo', label: 'Activo', kind: 'boolean' },
  { key: 'c_usuari_login', label: 'Usuario' },
  { key: 'fecha_creacion', label: 'Fecha de creación', kind: 'datetime' },
  { key: 'fecha_modificacion', label: 'Fecha de modificación', kind: 'datetime' },
]

const XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

function escapeXml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function formatDate(value) {
  const [year, month, day] = String(value).slice(0, 10).split('-')
  if (!year || !month || !day) return String(value)
  return `${day}/${month}/${year}`
}

function formatDateTime(value) {
  const text = String(value)
  const date = formatDate(text)
  const time = text.length > 10 ? text.slice(11, 16) : ''
  return time ? `${date} ${time}` : date
}

function cellText(emergencia, column) {
  const value = emergencia[column.key]
  if (value === null || value === undefined || value === '') return ''

  if (column.kind === 'boolean') return value ? 'Sí' : 'No'
  if (column.kind === 'date') return formatDate(value)
  if (column.kind === 'time') return String(value).slice(0, 5)
  if (column.kind === 'datetime') return formatDateTime(value)

  return String(value).trim()
}

function columnName(index) {
  let name = ''
  let current = index + 1
  while (current > 0) {
    const remainder = (current - 1) % 26
    name = String.fromCharCode(65 + remainder) + name
    current = Math.floor((current - 1) / 26)
  }
  return name
}

function worksheetXml(emergencias) {
  const rows = [HEADER_COLUMNS.map((column) => column.label)]
  emergencias.forEach((emergencia) => {
    rows.push(HEADER_COLUMNS.map((column) => cellText(emergencia, column)))
  })

  const xmlRows = rows.map((row, rowIndex) => {
    const cells = row.map((text, columnIndex) => {
      const ref = `${columnName(columnIndex)}${rowIndex + 1}`
      return `<c r="${ref}" t="inlineStr"><is><t>${escapeXml(text)}</t></is></c>`
    }).join('')
    return `<row r="${rowIndex + 1}">${cells}</row>`
  }).join('')

  return [
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
    '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
    `<sheetData>${xmlRows}</sheetData>`,
    '</worksheet>',
  ].join('')
}

function crc32(bytes) {
  let crc = 0xffffffff
  for (let index = 0; index < bytes.length; index += 1) {
    crc ^= bytes[index]
    for (let bit = 0; bit < 8; bit += 1) {
      crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0)
    }
  }
  return (crc ^ 0xffffffff) >>> 0
}

function dosDateTime(date) {
  const time = (date.getHours() << 11) | (date.getMinutes() << 5) | (date.getSeconds() >> 1)
  const day = ((date.getFullYear() - 1980) << 9) | ((date.getMonth() + 1) << 5) | date.getDate()
  return { time, day }
}

function zipStore(files) {
  const encoder = new TextEncoder()
  const { time, day } = dosDateTime(new Date())
  const locals = []
  const centrals = []
  let offset = 0

  files.forEach((file) => {
    const name = encoder.encode(file.name)
    const data = encoder.encode(file.data)
    const crc = crc32(data)
    const local = new Uint8Array(30 + name.length + data.length)
    const localView = new DataView(local.buffer)
    localView.setUint32(0, 0x04034b50, true)
    localView.setUint16(4, 20, true)
    localView.setUint16(8, 0, true)
    localView.setUint16(10, time, true)
    localView.setUint16(12, day, true)
    localView.setUint32(14, crc, true)
    localView.setUint32(18, data.length, true)
    localView.setUint32(22, data.length, true)
    localView.setUint16(26, name.length, true)
    local.set(name, 30)
    local.set(data, 30 + name.length)
    locals.push(local)

    const central = new Uint8Array(46 + name.length)
    const centralView = new DataView(central.buffer)
    centralView.setUint32(0, 0x02014b50, true)
    centralView.setUint16(4, 20, true)
    centralView.setUint16(6, 20, true)
    centralView.setUint16(10, 0, true)
    centralView.setUint16(12, time, true)
    centralView.setUint16(14, day, true)
    centralView.setUint32(16, crc, true)
    centralView.setUint32(20, data.length, true)
    centralView.setUint32(24, data.length, true)
    centralView.setUint16(28, name.length, true)
    centralView.setUint32(42, offset, true)
    central.set(name, 46)
    centrals.push(central)
    offset += local.length
  })

  const centralSize = centrals.reduce((sum, part) => sum + part.length, 0)
  const end = new Uint8Array(22)
  const endView = new DataView(end.buffer)
  endView.setUint32(0, 0x06054b50, true)
  endView.setUint16(8, files.length, true)
  endView.setUint16(10, files.length, true)
  endView.setUint32(12, centralSize, true)
  endView.setUint32(16, offset, true)

  const output = new Uint8Array(offset + centralSize + end.length)
  let cursor = 0
  locals.forEach((part) => {
    output.set(part, cursor)
    cursor += part.length
  })
  centrals.forEach((part) => {
    output.set(part, cursor)
    cursor += part.length
  })
  output.set(end, cursor)
  return output
}

export function buildEmergenciasXlsx(emergencias) {
  const sheet = worksheetXml(emergencias)
  return zipStore([
    {
      name: '[Content_Types].xml',
      data: [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>',
        '</Types>',
      ].join(''),
    },
    {
      name: '_rels/.rels',
      data: [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>',
        '</Relationships>',
      ].join(''),
    },
    {
      name: 'xl/workbook.xml',
      data: [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
        '<sheets><sheet name="Emergencias" sheetId="1" r:id="rId1"/></sheets>',
        '</workbook>',
      ].join(''),
    },
    {
      name: 'xl/_rels/workbook.xml.rels',
      data: [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>',
        '</Relationships>',
      ].join(''),
    },
    {
      name: 'xl/worksheets/sheet1.xml',
      data: sheet,
    },
  ])
}

export function exportEmergenciasExcel(emergencias) {
  const bytes = buildEmergenciasXlsx(emergencias)
  const blob = new Blob([bytes], { type: XLSX_MIME })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'emergencias.xlsx'
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}
