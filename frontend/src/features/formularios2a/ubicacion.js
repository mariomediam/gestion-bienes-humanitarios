export function partesUbicacion(formulario) {
  const lugar = [formulario.distrito_nombre, formulario.barrio_sector_urbanizacion]
    .filter(Boolean)
    .join(' - ')
  const lotes = (formulario.viviendas || [])
    .map((vivienda) => vivienda.numero_lote)
    .filter(Boolean)

  return { lugar, lotes }
}

export function textoUbicacion(formulario) {
  const { lugar, lotes } = partesUbicacion(formulario)
  return [lugar, lotes.join(', ')].filter(Boolean).join(' - ')
}
