# Documentación de contexto para Cursor

Este directorio contiene el contexto funcional y técnico del módulo S43 del sistema SIAC.

## Documentos

- `00-contexto-sistema.md`: alcance funcional y conceptos principales.
- `01-modelo-base-datos.md`: tablas y relaciones del esquema definitivo.
- `02-reglas-negocio-edan.md`: reglas del Formulario EDAN 2A.
- `03-reglas-negocio-bah.md`: reglas de la Planilla de Entrega de BAH.
- `04-reglas-negocio-almacen.md`: reglas del módulo de almacén.
- `05-integracion-modulos.md`: interacción EDAN → BAH → almacén.
- `06-decisiones-no-definidas.md`: decisiones que Cursor no debe asumir.

El esquema exacto de base de datos está en `../database/schema-SIAC-S43.sql`.
