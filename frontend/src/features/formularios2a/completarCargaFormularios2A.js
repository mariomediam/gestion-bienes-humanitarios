export const INSTITUCION = 'Municipalidad Provincial de Piura'
export const ESTADO_REGISTRO_ID = 1
export const ROL_PRIMER_INTEGRANTE = 1
export const ROL_RESTO_INTEGRANTES = 2

export function rolFamiliarId(indice) {
  return indice === 0 ? ROL_PRIMER_INTEGRANTE : ROL_RESTO_INTEGRANTES
}

function asignarRolFamiliar(integrantes) {
  if (!Array.isArray(integrantes)) return integrantes
  return integrantes.map((integrante, indice) => ({
    ...integrante,
    rol_familiar_id: rolFamiliarId(indice),
  }))
}

export function completarArchivo(datos, { emergenciaId, distrito, evaluadorId }) {
  if (!Array.isArray(datos?.formularios)) return datos

  return {
    ...datos,
    formularios: datos.formularios.map((formulario) => {
      if (!formulario || typeof formulario !== 'object' || Array.isArray(formulario)) {
        return formulario
      }
      const viviendas = Array.isArray(formulario.viviendas)
        ? formulario.viviendas.map((vivienda) => {
          if (!vivienda || typeof vivienda !== 'object' || Array.isArray(vivienda)) {
            return vivienda
          }
          const familias = Array.isArray(vivienda.familias)
            ? vivienda.familias.map((familia) => {
              if (!familia || typeof familia !== 'object' || Array.isArray(familia)) {
                return familia
              }
              return {
                ...familia,
                integrantes: asignarRolFamiliar(familia.integrantes),
              }
            })
            : vivienda.familias
          return { ...vivienda, familias }
        })
        : formulario.viviendas

      return {
        ...formulario,
        emergencia_id: emergenciaId,
        departamento_id: distrito.departamento_id,
        provincia_id: distrito.provincia_id,
        distrito_id: distrito.distrito_id,
        institucion: INSTITUCION,
        evaluador_id: evaluadorId,
        estado_registro_id: ESTADO_REGISTRO_ID,
        viviendas,
      }
    }),
  }
}
