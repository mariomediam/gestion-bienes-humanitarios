# Decisiones no definidas — no asumir

Este documento enumera aspectos que no están suficientemente definidos en el contexto entregado. Cursor debe preguntar antes de tomar una decisión que afecte estos puntos.

## Arquitectura de aplicación

No está definido de forma definitiva en esta documentación:

- framework de backend;
- framework de frontend;
- ORM o acceso a datos;
- API REST/GraphQL u otro estilo;
- autenticación/autorización;
- despliegue;
- estructura de carpetas de la aplicación.

Usar el stack existente si el repositorio ya lo contiene. Si el proyecto comienza vacío, preguntar.

## Catálogos

El DDL definitivo crea las tablas de catálogo, pero no incluye sus datos iniciales.

No asumir IDs ni códigos para:

- estados de registro EDAN;
- estados de Planilla BAH;
- estados de movimiento de almacén;
- tipos de movimiento;
- tipos de cálculo;
- roles familiares;
- condiciones de persona;
- tipos de daño;
- grados de lesión;
- demás catálogos.

Consultar la base o scripts de datos existentes.

## Estado y transiciones

No está documentado completamente:

- qué transiciones de estado están permitidas en EDAN;
- qué transiciones de estado están permitidas en Planilla BAH;
- qué transiciones de estado están permitidas en movimientos de almacén;
- quién puede realizar cada transición.

## Anulaciones y reversión


- si una Planilla BAH anulada desbloquea el Formulario 2A;

No está definido de manera final:

- si la anulación de una planilla genera un movimiento inverso o cambia el estado del movimiento existente;
- cómo se auditan reversiones de movimientos confirmados.

Preguntar antes de implementar.

## Stock negativo

No está definido si se permite confirmar una salida que deje stock negativo. Preguntar antes de implementar la validación.

## Transferencias entre almacenes

El modelo permite varios almacenes y movimientos con origen, pero no se ha definido el flujo completo de una transferencia entre almacenes ni si requiere dos movimientos enlazados. Preguntar antes de implementar.

## Bienes serializados

Se conversó conceptualmente sobre bienes como motobombas, pero el esquema definitivo no contiene serial, marca, modelo ni identificación individual de activos.

No implementar control serializado sin autorización.

## Datos de destinatario

`S43alm_movimientos` contiene `destinatario` como texto. No crear automáticamente una entidad normalizada de destinatarios sin requerimiento.

## Reglas especiales de ayuda

`S43cat_bah_reglas_entrega` no contiene una estructura de condiciones especiales geográficas o climáticas. Las observaciones no deben transformarse automáticamente en reglas programáticas sin confirmación.

## Fecha prevista de devolución

El esquema definitivo de `S43alm_movimientos` no contiene `fecha_prevista_devolucion`. No agregarla por inferencia.

## Auditoría adicional

No agregar campos de usuario, IP, dispositivo, historial o tablas de auditoría adicionales salvo requerimiento expreso o existencia previa en el proyecto.
