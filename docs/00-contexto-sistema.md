# Contexto del sistema

## Objetivo

El sistema administra información relacionada con emergencias y ayuda humanitaria. El alcance funcional definido hasta el momento comprende:

- Registro de emergencias.
- Registro del Formulario de Campo 2A: Empadronamiento Familiar y Medios de Vida.
- Registro de personas, viviendas, familias, integrantes y medios de vida vinculados al Formulario 2A.
- Registro del personal que puede actuar como evaluador EDAN y/o encargado de almacén.
- Cálculo/sugerencia de bienes de ayuda humanitaria según reglas configuradas.
- Registro de la Planilla de Entrega de Bienes de Ayuda Humanitaria.
- Gestión de almacenes, entradas, salidas, préstamos, devoluciones, mermas, ajustes y transformaciones.
- Control de stock mediante movimientos de almacén.
- Reportes derivados de la información registrada.

## Módulos funcionales

### EDAN

La emergencia es el evento principal. A una emergencia se asocian formularios EDAN 2A. El Formulario 2A registra ubicación, evaluador, viviendas, familias, integrantes y medios de vida.

### Bienes de Ayuda Humanitaria (BAH)

Existe un catálogo de bienes, categorías, unidades de medida y reglas de entrega. La Planilla BAH representa la entrega a una sola familia mediante un integrante receptor.

### Almacén

Todo cambio de existencias se representa mediante un movimiento de almacén y sus detalles. No existe una tabla de detalle BAH separada de los movimientos de almacén.

## Principios de diseño acordados

1. Evitar duplicación de información que pueda obtenerse por relaciones.
2. Mantener una sola fuente de verdad para las cantidades que entran o salen del almacén.
3. Usar el signo de `cantidad` para representar el efecto de un detalle sobre el stock.
4. Permitir trazabilidad de devoluciones mediante relación con el movimiento de origen.
5. Mantener las transformaciones dentro de un único movimiento con entradas y salidas.
6. Mantener valores numéricos para cálculo y valores textuales opcionales para representar fracciones exactas.
7. No agregar reglas no confirmadas por el usuario.

## Fuentes funcionales

El diseño se ha elaborado considerando los documentos del proyecto relacionados con:

- Guía para utilización de los formularios para la Evaluación de Daños y Análisis de Necesidades.
- Formatos oficiales de EDAN y Planilla de Entrega de Bienes de Ayuda Humanitaria.
- Requerimiento del sistema.

Cuando una regla normativa no esté representada explícitamente en el modelo o en estos documentos de contexto, debe confirmarse antes de implementarse.
