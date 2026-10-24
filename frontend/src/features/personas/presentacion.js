import { OPCIONES_SEXO } from '@features/formularios2a/components/PersonaFormModal'

function unirPartes(partes) {
  return partes
    .filter((parte) => parte !== null && parte !== undefined && String(parte).trim() !== '')
    .join(' ')
}

export function textoNombrePersona(persona) {
  return unirPartes([persona.apellido_paterno, persona.apellido_materno, persona.nombres])
}

export function textoDocumentoPersona(persona) {
  return unirPartes([persona.nombre_tipo_documento, persona.numero_documento])
}

export function textoFechaNacimiento(value) {
  if (!value) return ''
  const iso = String(value).slice(0, 10)
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso)
  if (!match) return iso
  return `${match[3]}/${match[2]}/${match[1]}`
}

export function textoSexo(value) {
  if (!value) return ''
  const opcion = OPCIONES_SEXO.find((item) => item.value === value)
  return opcion ? opcion.label : value
}

export function textoActivo(value) {
  return value ? 'Sí' : 'No'
}

export function textoCelda(value) {
  if (value === null || value === undefined || value === '') return '—'
  return String(value)
}
