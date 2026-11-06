export function agruparDevoluciones(rows) {
  const devoluciones = []
  const porMovimiento = new Map()

  for (const row of rows || []) {
    let devolucion = porMovimiento.get(row.movimiento_id)

    if (!devolucion) {
      devolucion = {
        ...row,
        detalles: [],
      }
      porMovimiento.set(row.movimiento_id, devolucion)
      devoluciones.push(devolucion)
    }

    if (row.movimiento_detalle_id == null) continue

    const yaEsta = devolucion.detalles.some(
      (detalle) => detalle.movimiento_detalle_id === row.movimiento_detalle_id,
    )
    if (yaEsta) continue

    devolucion.detalles.push({
      movimiento_detalle_id: row.movimiento_detalle_id,
      bien_nombre: row.bien_nombre,
      unidad_medida_abreviatura: row.unidad_medida_abreviatura,
      cantidad: row.cantidad,
      cantidad_texto: row.cantidad_texto,
    })
  }

  return devoluciones
}
