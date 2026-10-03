# Reglas de negocio — Planilla de Entrega de Bienes de Ayuda Humanitaria

## Regla de cardinalidad

En el sistema, una Planilla BAH corresponde a:

- una sola familia;
- una sola persona receptora perteneciente a esa familia.

La persona receptora se almacena en:

```text
S43bah_planilla_entrega.integrante_receptor_id
```

El receptor normalmente puede ser el jefe de familia, pero no debe asumirse que siempre lo será.

La cantidad de bienes registrada representa la ayuda entregada a la familia completa, aunque exista un único receptor.

## Información derivada desde el receptor

Desde `integrante_receptor_id` se obtiene, mediante relaciones:

- persona receptora;
- familia;
- total de integrantes de la familia;
- vivienda;
- Formulario 2A;
- ubicación del Formulario 2A;
- emergencia;
- código SINPAD y demás información disponible en la emergencia.

No duplicar estos datos en `S43bah_planilla_entrega` si ya son derivables.

## Planilla y almacén

La Planilla BAH no tiene una tabla propia de detalle de bienes.

La relación es:

```text
S43bah_planilla_entrega
  -> movimiento_almacen_id
    -> S43alm_movimientos
      -> S43alm_movimiento_detalle
        -> S43cat_bah_bienes
```

Los bienes impresos/consultados de una Planilla BAH deben provenir del detalle del movimiento de almacén relacionado.

Esto evita inconsistencias entre un supuesto detalle BAH y el Kardex.

## Cantidades

`S43alm_movimiento_detalle.cantidad` es `DECIMAL(18,6)`.

En una salida por Planilla BAH, la cantidad debe ser negativa porque disminuye stock.

Ejemplos conceptuales:

```text
Calamina:  -18.000000
Frazada:    -5.000000
Clavos:     -0.750000
```

Cuando sea necesario preservar la representación original de una fracción, usar `cantidad_texto`:

```text
cantidad       = -0.750000
cantidad_texto = '3/4'
```

El signo operativo se obtiene de `cantidad`; `cantidad_texto` conserva la magnitud escrita.

## Bienes devolvibles dentro de una Planilla

Un bien entregado mediante Planilla BAH puede ser definitivo o con cargo a devolución.

El detalle utiliza:

```text
es_devolvible
```

Ejemplos:

```text
Calamina -18  es_devolvible = 0
Pala      -2  es_devolvible = 1
```

No asumir que un bien es siempre devolvible o siempre definitivo solo por su código. La modalidad corresponde a la operación concreta.

## Catálogo de bienes

`S43cat_bah_bienes.visible_planilla` determina si un bien está habilitado para aparecer en el contexto de Planilla BAH.

`orden_impresion` se conserva para controlar el orden de presentación de los bienes.

## Reglas de cálculo recomendadas

Las reglas de sugerencia se almacenan en `S43cat_bah_reglas_entrega` y se relacionan con `S43cat_bah_tipos_calculo`.

Campos relevantes:

- `cantidad_base`
- `cantidad_base_texto`
- `aplica_damnificado`
- `aplica_afectado`
- `cantidad_maxima`
- `cantidad_maxima_texto`
- `observacion`

Estas reglas sirven para sugerir cantidades; no sustituyen la cantidad efectivamente entregada, que se registra en `S43alm_movimiento_detalle`.

La existencia de una regla no autoriza a inventar condiciones especiales no modeladas.

## Emisión

Una Planilla BAH puede estar vinculada a un movimiento de almacén mediante `movimiento_almacen_id`.

La lógica acordada es que un movimiento en borrador no afecta el stock; cuando la operación queda confirmada, sus detalles pasan a formar parte del stock/Kardex.

El mapeo exacto entre estados de planilla y estados de movimiento debe implementarse usando los códigos reales existentes en los catálogos. No asumir IDs numéricos.

## Bloqueo del EDAN

Cuando la Planilla BAH está emitida, el Formulario 2A relacionado no puede modificarse.

No guardar una bandera de bloqueo duplicada en EDAN; determinar el bloqueo por relaciones.

## Anulación

El esquema incluye:

- `fecha_anulacion`
- `motivo_anulacion`

No está definido en este contexto el mecanismo exacto de reversión de stock al anular una planilla emitida. Debe preguntarse antes de implementarlo si todavía no existe lógica en el repositorio.
