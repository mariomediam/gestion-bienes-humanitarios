export function buildPersonaSearchParams(texto) {
  const valor = texto.trim()
  if (!valor) return {}
  if (/^\d+$/.test(valor)) return { numero_documento: valor }
  return { nombre_completo: valor }
}
