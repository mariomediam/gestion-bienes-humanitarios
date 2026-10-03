# Reglas de negocio — Almacén

## Principio central

Todo cambio de stock se representa mediante:

```text
S43alm_movimientos
  -> S43alm_movimiento_detalle
```

No mantener un segundo detalle paralelo para Planillas BAH.

## Signo de la cantidad

Regla acordada:

```text
cantidad > 0  => ingreso al almacén
cantidad < 0  => salida del almacén
```

`cantidad = 0` está prohibido por constraint.

La naturaleza configurada en `S43cat_alm_tipos_movimiento.naturaleza` es:

- `E`: entrada.
- `S`: salida.
- `M`: mixto.

La base de datos no contiene un CHECK que compare automáticamente la naturaleza del encabezado con el signo de cada detalle. Esa validación debe realizarse al confirmar el movimiento.

## Estado de movimiento y stock

Regla funcional acordada:

- Un movimiento en borrador no afecta stock.
- Un movimiento confirmado sí afecta stock.
- El tratamiento exacto de un movimiento anulado sobre el stock no está definido en este contexto y no debe asumirse.

Los códigos/IDs concretos del catálogo `S43cat_alm_estados_movimiento` deben leerse de la base; no asumir valores fijos.

El stock de un bien se obtiene conceptualmente sumando las cantidades de sus detalles pertenecientes a movimientos válidos/confirmados del almacén correspondiente.

No crear por defecto una columna `stock_actual` editable manualmente.

## Stock inicial

El inicio de existencias se registra como un movimiento de entrada, no modificando directamente un saldo.

## Entradas y salidas comunes

El catálogo `S43cat_alm_tipos_movimiento` define los tipos reales disponibles. El DDL no contiene sus filas, por lo que no se deben inventar códigos.

Conceptualmente el sistema contempla operaciones como:

- stock inicial;
- compra;
- donación;
- transferencia de entrada/salida;
- entrega BAH;
- entrega directa;
- préstamo;
- devolución;
- consumo;
- merma;
- ajuste positivo/negativo;
- transformación.

Antes de usar un código concreto, verificar que exista en el catálogo real.

## Préstamos

### Salida

El préstamo se registra como un movimiento normal de salida:

```text
cantidad negativa
es_devolvible = 1
```

### Devolución

El reingreso se registra como un nuevo movimiento de entrada y debe indicar a qué préstamo corresponde mediante:

```text
S43alm_movimientos.movimiento_origen_id
```

Regla aceptada: cada movimiento de devolución referencia un solo préstamo original. Un préstamo puede tener múltiples devoluciones parciales.

Ejemplo conceptual:

```text
Préstamo 100
Motobomba -2

Devolución 120
movimiento_origen_id = 100
Motobomba +1

Devolución 140
movimiento_origen_id = 100
Motobomba +1
```

Validaciones requeridas al confirmar una devolución:

1. El movimiento origen debe existir.
2. Debe ser una operación de la que corresponda devolución según las reglas del sistema.
3. El bien devuelto debe existir entre los detalles devolvibles del movimiento origen.
4. La suma devuelta no puede superar la cantidad originalmente entregada como devolvible.
5. El pendiente de devolución debe calcularse; no duplicarlo en una columna salvo requerimiento posterior.

## Bienes parcialmente devolvibles

La restricción única permite que un mismo bien aparezca como máximo una vez por modalidad dentro del mismo movimiento:

```text
movimiento_id + bien_id + es_devolvible
```

Esto permite, por ejemplo, que en una misma operación existan:

```text
Pala -5  es_devolvible = 0
Pala -2  es_devolvible = 1
```

## Transformaciones

Una transformación se registra en un único movimiento de naturaleza mixta.

Dentro del mismo movimiento:

- insumos consumidos: cantidades negativas;
- bienes obtenidos: cantidades positivas.

Ejemplo:

```text
Producto A  -10
Producto B   -5
Producto C  +20
```

Validación funcional recomendada y acordada para reconocer una transformación válida:

- debe existir al menos un detalle negativo;
- debe existir al menos un detalle positivo.

No crear dos movimientos separados de entrada/salida para una misma transformación salvo cambio explícito de diseño.

## Mermas

Una merma debe registrarse como una salida de stock. No modificar directamente el saldo.

La causa puede registrarse en `observacion` u otro dato ya existente según el flujo implementado. No agregar nuevas columnas de motivo sin confirmación.

## Ajustes

Las diferencias encontradas mediante inventario se registran como movimientos positivos o negativos, según corresponda, en lugar de editar el stock.

## Fracciones

Para cantidades fraccionarias usar:

```text
cantidad DECIMAL(18,6)
cantidad_texto VARCHAR(30) NULL
```

Ejemplo de salida de 3/4 kg:

```text
cantidad       = -0.750000
cantidad_texto = '3/4'
```

Para cálculo usar `cantidad`. Para presentación puede usarse `cantidad_texto` cuando exista.

## Encargado de almacén

Cada movimiento tiene `encargado_almacen_id`, FK a `S43bah_personal`.

La aplicación debe validar/filtrar que el personal seleccionado tenga:

```text
es_encargado_almacen = 1
```

La FK por sí sola no valida ese flag.

## Fecha de confirmación

`fecha_confirmacion` registra cuándo el movimiento dejó de ser borrador y fue confirmado, si la aplicación utiliza esa transición.

No confundir con `fecha_movimiento`, que representa la fecha operativa del movimiento.

## Integridad al confirmar

La confirmación de un movimiento debe ser una operación atómica. Antes de confirmar, validar al menos:

- que existan detalles;
- que ningún detalle tenga cantidad 0;
- que el signo sea compatible con la naturaleza del tipo de movimiento, excepto naturaleza `M`;
- que las salidas no generen un stock inválido según la política definida;
- reglas de devolución cuando exista `movimiento_origen_id`;
- reglas de transformación cuando corresponda.

La política exacta sobre permitir o no stock negativo no está definida en este contexto; preguntar si el repositorio no la establece.
