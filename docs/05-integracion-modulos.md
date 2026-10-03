# Integración entre EDAN, BAH y Almacén

## Flujo principal

```text
Emergencia
   |
   v
Formulario EDAN 2A
   |
   v
Vivienda
   |
   v
Familia
   |
   v
Integrante receptor
   |
   v
Planilla BAH
   |
   v
Movimiento de almacén
   |
   v
Detalle de movimiento
   |
   v
Bienes
```

## De Planilla BAH hacia EDAN

`S43bah_planilla_entrega.integrante_receptor_id` referencia a `S43edan_formulario_2a_integrantes`.

A partir de esa FK se obtiene:

```text
integrante
 -> familia
 -> vivienda
 -> formulario 2A
 -> emergencia
```

No agregar a la Planilla BAH campos redundantes para `familia_id`, `formulario_2a_id`, `emergencia_id`, ubicación, código SINPAD o total de integrantes mientras estos puedan obtenerse de la cadena existente.

## De Planilla BAH hacia almacén

`S43bah_planilla_entrega.movimiento_almacen_id` referencia a `S43alm_movimientos`.

Los bienes de la planilla se consultan desde `S43alm_movimiento_detalle`.

No crear de nuevo `S43bah_planilla_entrega_detalle`.

## Una sola fuente de verdad para cantidades

La cantidad efectivamente entregada o devuelta existe una sola vez en:

```text
S43alm_movimiento_detalle.cantidad
```

Cuando exista fracción escrita, su representación se conserva en:

```text
S43alm_movimiento_detalle.cantidad_texto
```

Los reportes, impresión de planillas y Kardex deben partir del mismo detalle.

## Reglas sugeridas vs. entrega real

Las cantidades recomendadas se consultan en:

```text
S43cat_bah_reglas_entrega
```

Las cantidades reales se registran en:

```text
S43alm_movimiento_detalle
```

No sobrescribir una cantidad real de almacén con una regla calculada.

## Personal

`S43bah_personal` sirve para dos funciones:

```text
es_evaluador_edan
es_encargado_almacen
```

Relaciones:

```text
S43edan_formulario_2a.evaluador_id
 -> S43bah_personal.personal_id

S43alm_movimientos.encargado_almacen_id
 -> S43bah_personal.personal_id
```

La capa de aplicación debe verificar el flag correspondiente al contexto.

## Bloqueo del Formulario 2A

La existencia de una Planilla BAH emitida vinculada a un integrante de una familia del Formulario 2A impide modificar ese Formulario 2A.

La verificación debe recorrer las relaciones, no consultar una bandera duplicada.

## Consistencia transaccional

Cuando una acción funcional implique cambios coordinados entre Planilla BAH y almacén, realizar la operación dentro de una transacción consistente.

Ejemplos:

- emitir/confirmar planilla y movimiento;
- anular una operación con impacto de stock;
- registrar devolución contra préstamo.

La estrategia exacta de reversión ante anulación todavía no está documentada; no inventarla.
