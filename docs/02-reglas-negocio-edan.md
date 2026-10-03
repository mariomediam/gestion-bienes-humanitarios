# Reglas de negocio — EDAN Formulario 2A

## Alcance

Este documento describe las reglas confirmadas para el registro del Formulario de Campo 2A y su relación con el resto del sistema.

## Estructura del registro

La cadena principal del modelo es:

```text
Emergencia
  -> Formulario 2A
    -> Vivienda
      -> Familia
        -> Integrantes
        -> Medios de vida
```

La tabla de vivienda mantiene el nombre definitivo `S43edan_formulario_2a_viviendas`.

## Emergencia

Cada Formulario 2A pertenece a una emergencia mediante `emergencia_id`.

No duplicar en tablas dependientes datos que ya se puedan obtener a través de esta relación.

## Ubicación

El Formulario 2A almacena directamente:

- departamento,
- provincia,
- distrito,
- localidad,
- barrio/sector/urbanización,
- centro poblado,
- caserío,
- anexo,
- calle/manzana,
- edificio/piso/departamento,
- otros datos de ubicación.

No replicar estos datos en la Planilla BAH si pueden recuperarse desde el integrante receptor y su Formulario 2A.

## Viviendas y familias

Una vivienda puede tener familias asociadas mediante `S43edan_formulario_2a_familias.vivienda_id`.

Los integrantes pertenecen a una familia. Una persona no puede repetirse dos veces dentro de la misma familia por la restricción única `familia_id + persona_id`.

## Integrantes

La información de salud del integrante está incorporada en `S43edan_formulario_2a_integrantes`; no existe una tabla separada de salud en el esquema definitivo.

Campos de salud incluidos:

- `gestante_semanas`
- `tipo_discapacidad_id`
- `enfermedad_cronica_id`

También se registran condición de la persona, tipo de daño personal y grado de lesión cuando corresponda.

## Evaluador EDAN

El evaluador se selecciona desde `S43bah_personal`.

Un registro puede ser seleccionado como evaluador cuando corresponde funcionalmente al flag:

```text
es_evaluador_edan = 1
```

La FK física de la base solo garantiza que `evaluador_id` exista en `S43bah_personal`; la aplicación debe filtrar/validar el rol correcto.

## Estado del Formulario 2A

El estado se registra mediante `estado_registro_id` y el catálogo `S43cat_estados_registro`.

Los códigos/IDs concretos de dicho catálogo no están definidos en el DDL de referencia. No asumirlos en código.

## Bloqueo por Planilla BAH

Regla crítica:

> Una vez emitida una Planilla de Entrega de Bienes de Ayuda Humanitaria asociada a una familia del Formulario 2A, el Formulario 2A relacionado no debe poder modificarse.

No existe ni debe agregarse por defecto una columna de tipo `bloqueado_bah` en `S43edan_formulario_2a`.

El bloqueo se determina por relaciones:

```text
Formulario 2A
 -> Vivienda
 -> Familia
 -> Integrante
 -> Planilla BAH (integrante_receptor_id)
```

La validación debe considerar el estado real de la planilla para determinar si ya está emitida. No asumir IDs numéricos; consultar el catálogo real de estados de planilla.

## Eliminaciones y modificaciones

No permitir que una operación sobre EDAN destruya la trazabilidad de una Planilla BAH ya emitida o de un movimiento de almacén relacionado.

No agregar `ON DELETE CASCADE` sobre relaciones críticas sin autorización expresa.

## Datos no definidos en este contexto

No están definidos aquí:

- flujo completo de transiciones de estado del Formulario 2A;
- permisos por rol de usuario;
- mecanismo de autenticación;
- comportamiento exacto ante anulación de una Planilla BAH respecto al desbloqueo del Formulario 2A.

Preguntar antes de implementar cualquiera de estas decisiones.
