# Modelo de base de datos definitivo

## Fuente de verdad

El esquema definitivo está en `database/schema-SIAC-S43.sql` y corresponde a SQL Server 2008 R2, base `SIAC`.

Este documento resume el modelo para facilitar su interpretación. Si existe una diferencia con el script SQL, prevalece el script.

## Convención

Todas las tablas del módulo utilizan el prefijo `S43`.

## 1. Almacén

### `S43alm_almacenes`

Representa los almacenes físicos/lógicos.

Campos:

- `almacen_id` INT IDENTITY, PK.
- `codigo` VARCHAR(30), único.
- `nombre` NVARCHAR(150).
- `ubicacion` NVARCHAR(300), nullable.
- `esta_activo` BIT.
- `fecha_creacion` DATETIME.

### `S43alm_movimientos`

Cabecera de cualquier operación que pueda afectar existencias.

Campos:

- `movimiento_id` INT IDENTITY, PK.
- `almacen_id` INT, FK a `S43alm_almacenes`.
- `tipo_movimiento_id` SMALLINT, FK a `S43cat_alm_tipos_movimiento`.
- `estado_movimiento_id` SMALLINT, FK a `S43cat_alm_estados_movimiento`.
- `movimiento_origen_id` INT NULL, FK autorreferenciada a `S43alm_movimientos`.
- `fecha_movimiento` DATETIME.
- `documento_referencia` NVARCHAR(100) NULL.
- `fecha_documento` DATE NULL.
- `destinatario` NVARCHAR(250) NULL.
- `observacion` NVARCHAR(1000) NULL.
- `fecha_confirmacion` DATETIME NULL.
- `encargado_almacen_id` SMALLINT, FK a `S43bah_personal`.
- `c_usuari_login` CHAR(20).
- `fecha_creacion` DATETIME.
- `fecha_modificacion` DATETIME NULL.

Restricción relevante: `movimiento_origen_id` no puede apuntar al mismo `movimiento_id`.

### `S43alm_movimiento_detalle`

Única tabla de detalle de bienes que entran o salen del almacén. También contiene los bienes de una Planilla BAH.

Campos:

- `movimiento_detalle_id` INT IDENTITY, PK.
- `movimiento_id` INT, FK a `S43alm_movimientos`.
- `bien_id` INT, FK a `S43cat_bah_bienes`.
- `cantidad` DECIMAL(18,6), no puede ser 0.
- `cantidad_texto` VARCHAR(30) NULL.
- `es_devolvible` BIT.
- `observacion` NVARCHAR(500) NULL.
- `fecha_creacion` DATETIME.

Restricciones relevantes:

- `cantidad <> 0`.
- Un detalle con cantidad positiva no puede marcarse como devolvible.
- Combinación única: `movimiento_id + bien_id + es_devolvible`.

## 2. Personal

### `S43bah_personal`

Catálogo único para el personal relevante al módulo.

Campos:

- `personal_id` SMALLINT IDENTITY, PK.
- `apellido_paterno` NVARCHAR(50).
- `apellido_materno` NVARCHAR(50).
- `nombres` NVARCHAR(150).
- `es_evaluador_edan` BIT.
- `es_encargado_almacen` BIT.
- `esta_activo` BIT.
- `fecha_creacion` DATETIME.
- `fecha_modificacion` DATETIME NULL.

Regla física de BD: al menos uno de los flags `es_evaluador_edan` o `es_encargado_almacen` debe ser 1.

## 3. Planilla BAH

### `S43bah_planilla_entrega`

Cabecera de una Planilla de Entrega de Bienes de Ayuda Humanitaria.

Campos:

- `planilla_entrega_id` INT IDENTITY, PK.
- `numero_planilla` INT.
- `anio_planilla` INT.
- `integrante_receptor_id` INT, FK a `S43edan_formulario_2a_integrantes`.
- `fecha_entrega` DATE.
- `estado_planilla_id` SMALLINT, FK a `S43cat_bah_estados_planilla`.
- `observacion` NVARCHAR(1000) NULL.
- `fecha_emision` DATETIME NULL.
- `fecha_anulacion` DATETIME NULL.
- `motivo_anulacion` NVARCHAR(500) NULL.
- `c_usuari_login` CHAR(20).
- `fecha_creacion` DATETIME.
- `fecha_modificacion` DATETIME NULL.
- `movimiento_almacen_id` INT NULL, FK a `S43alm_movimientos`.

No existe `S43bah_planilla_entrega_detalle`. Los bienes de la planilla se obtienen a través del movimiento de almacén vinculado.

## 4. Catálogos BAH

### `S43cat_bah_categorias_bienes`

- `categoria_bien_id` SMALLINT, PK.
- `codigo` VARCHAR(30), único.
- `nombre` NVARCHAR(100).
- `orden` SMALLINT > 0.
- `esta_activo` BIT.

### `S43cat_bah_unidades_medida`

- `unidad_medida_id` SMALLINT, PK.
- `codigo` VARCHAR(20), único.
- `nombre` NVARCHAR(100).
- `abreviatura` NVARCHAR(20) NULL.
- `esta_activo` BIT.

### `S43cat_bah_bienes`

- `bien_id` INT IDENTITY, PK.
- `categoria_bien_id` SMALLINT, FK a `S43cat_bah_categorias_bienes`.
- `unidad_medida_id` SMALLINT, FK a `S43cat_bah_unidades_medida`.
- `codigo` VARCHAR(50), único.
- `nombre` NVARCHAR(250).
- `descripcion` NVARCHAR(500) NULL.
- `orden_impresion` SMALLINT NULL; si tiene valor debe ser > 0.
- `esta_activo` BIT.
- `visible_planilla` BIT.

### `S43cat_bah_estados_planilla`

- `estado_planilla_id` SMALLINT, PK.
- `codigo` VARCHAR(30), único.
- `nombre` NVARCHAR(100).
- `esta_activo` BIT.

### `S43cat_bah_tipos_calculo`

- `tipo_calculo_id` SMALLINT, PK.
- `codigo` VARCHAR(30), único.
- `nombre` NVARCHAR(150).
- `descripcion` NVARCHAR(500) NULL.
- `esta_activo` BIT.

### `S43cat_bah_reglas_entrega`

Reglas configurables para sugerir cantidades de bienes.

- `regla_entrega_id` INT IDENTITY, PK.
- `bien_id` INT, FK a `S43cat_bah_bienes`.
- `tipo_calculo_id` SMALLINT, FK a `S43cat_bah_tipos_calculo`.
- `cantidad_base` DECIMAL(18,6), > 0.
- `cantidad_base_texto` VARCHAR(30) NULL.
- `aplica_damnificado` BIT.
- `aplica_afectado` BIT.
- `cantidad_maxima` DECIMAL(18,6) NULL; si tiene valor debe ser > 0.
- `cantidad_maxima_texto` VARCHAR(30) NULL.
- `observacion` NVARCHAR(500) NULL.
- `esta_activo` BIT.
- `fecha_creacion` DATETIME.
- `fecha_modificacion` DATETIME NULL.

Regla física de BD: al menos uno de `aplica_damnificado` o `aplica_afectado` debe ser 1.

## 5. Catálogos de almacén

### `S43cat_alm_estados_movimiento`

- `estado_movimiento_id` SMALLINT, PK.
- `codigo` VARCHAR(30), único.
- `nombre` NVARCHAR(100).
- `esta_activo` BIT.

### `S43cat_alm_tipos_movimiento`

- `tipo_movimiento_id` SMALLINT, PK.
- `codigo` VARCHAR(50), único.
- `nombre` NVARCHAR(150).
- `naturaleza` CHAR(1), restringida a `E`, `S` o `M`.
- `requiere_movimiento_origen` BIT.
- `esta_activo` BIT.

Los valores concretos de los catálogos no se incluyen en el DDL recibido; no asumir IDs ni códigos que no existan en la base real.

## 6. Emergencias y Formulario EDAN 2A

### `S43edan_emergencias`

- `emergencia_id` INT IDENTITY, PK.
- `numero_evaluacion` VARCHAR(50).
- `codigo_sinpad` VARCHAR(30) NULL.
- `tipo_peligro_id` INT, FK a `S43cat_tipos_peligro`.
- `fecha_emergencia` DATE.
- `hora_ocurrencia_estimada` TIME(0) NULL.
- `esta_activo` BIT.
- `c_usuari_login` CHAR(20).
- `fecha_creacion` DATETIME.
- `fecha_modificacion` DATETIME NULL.

### `S43edan_formulario_2a`

- `formulario_2a_id` INT IDENTITY, PK.
- `emergencia_id` INT, FK a `S43edan_emergencias`.
- `departamento_id` CHAR(2).
- `provincia_id` CHAR(2).
- `distrito_id` CHAR(2).
- `fecha_empadronamiento` DATE.
- `hora_empadronamiento` TIME(0) NULL.
- `localidad` NVARCHAR(200) NULL.
- `barrio_sector_urbanizacion` NVARCHAR(250) NULL.
- `centro_poblado` NVARCHAR(200) NULL.
- `caserio` NVARCHAR(200) NULL.
- `anexo` NVARCHAR(200) NULL.
- `calle_manzana` NVARCHAR(250) NULL.
- `edificio_piso_dpto` NVARCHAR(250) NULL.
- `otros_ubicacion` NVARCHAR(250) NULL.
- `numero_hoja` SMALLINT > 0.
- `total_hojas` SMALLINT NULL, si tiene valor debe ser >= `numero_hoja`.
- `institucion` NVARCHAR(250) NULL.
- `evaluador_id` SMALLINT, FK a `S43bah_personal`.
- `estado_registro_id` SMALLINT, FK a `S43cat_estados_registro`.
- `c_usuari_login` CHAR(20).
- `fecha_creacion` DATETIME.
- `fecha_modificacion` DATETIME NULL.

### `S43edan_formulario_2a_viviendas`

- `vivienda_id` INT IDENTITY, PK.
- `formulario_2a_id` INT, FK a `S43edan_formulario_2a`.
- `numero_orden` SMALLINT > 0.
- `numero_lote` NVARCHAR(50) NULL.
- `tenencia_propia` BIT NULL.
- `tipo_uso_instalacion_id` SMALLINT, FK a `S43cat_tipos_uso_instalacion`.
- `condicion_vivienda_id` SMALLINT NULL, FK a `S43cat_condiciones_vivienda`.
- `material_techo_id` SMALLINT NULL, FK a `S43cat_materiales_techo`.
- `material_pared_id` SMALLINT NULL, FK a `S43cat_materiales_pared`.
- `material_piso_id` SMALLINT NULL, FK a `S43cat_materiales_piso`.
- `fecha_creacion` DATETIME.

Único: `formulario_2a_id + numero_orden`.

### `S43edan_formulario_2a_familias`

- `familia_id` INT IDENTITY, PK.
- `vivienda_id` INT, FK a `S43edan_formulario_2a_viviendas`.
- `numero_orden` SMALLINT > 0.
- `fecha_creacion` DATETIME.

Único: `vivienda_id + numero_orden`.

### `S43edan_formulario_2a_integrantes`

- `integrante_id` INT IDENTITY, PK.
- `familia_id` INT, FK a `S43edan_formulario_2a_familias`.
- `persona_id` INT, FK a `S43personas`.
- `rol_familiar_id` SMALLINT, FK a `S43cat_roles_familiares`.
- `numero_orden` SMALLINT.
- `edad` SMALLINT, entre 0 y 130.
- `condicion_persona_id` SMALLINT, FK a `S43cat_condiciones_persona`.
- `tipo_danio_personal_id` SMALLINT NULL, FK a `S43cat_tipos_danio_personal`.
- `grado_lesion_id` SMALLINT NULL, FK a `S43cat_grados_lesion`.
- `gestante_semanas` SMALLINT NULL, entre 1 y 45 cuando tiene valor.
- `tipo_discapacidad_id` SMALLINT NULL, FK a `S43cat_tipos_discapacidad`.
- `enfermedad_cronica_id` SMALLINT NULL, FK a `S43cat_enfermedades_cronicas`.
- `fecha_creacion` DATETIME.

Únicos:

- `familia_id + numero_orden`.
- `familia_id + persona_id`.

Regla física: `grado_lesion_id` solo puede tener valor cuando `tipo_danio_personal_id = 1`. No interpretar el significado del ID 1 fuera de este constraint sin consultar el catálogo real.

### `S43edan_formulario_2a_medios_vida`

- `medio_vida_id` INT IDENTITY, PK.
- `familia_id` INT, FK a `S43edan_formulario_2a_familias`.
- `tipo_medio_vida_id` SMALLINT, FK a `S43cat_tipos_medios_vida`.
- `cantidad` INT > 0.
- `observacion` NVARCHAR(500) NULL.
- `fecha_creacion` DATETIME.

Único: `familia_id + tipo_medio_vida_id`.

## 7. Personas

### `S43personas`

- `persona_id` INT IDENTITY, PK.
- `tipo_documento_id` SMALLINT NULL, FK a `S43cat_tipos_documento`.
- `numero_documento` VARCHAR(20) NULL.
- `apellido_paterno` NVARCHAR(50).
- `apellido_materno` NVARCHAR(50).
- `nombres` NVARCHAR(150).
- `fecha_nacimiento` DATE.
- `sexo` CHAR(1).
- `telefono` NVARCHAR(50).
- `correo` NVARCHAR(50).
- `esta_activo` BIT.
- `fecha_creacion` DATETIME.
- `c_usuari_login` CHAR(20).
- `fecha_modificacion` DATETIME NULL.

Regla física: `tipo_documento_id` y `numero_documento` deben ser ambos NULL o ambos no NULL.

## 8. Otros catálogos EDAN

El esquema contiene además:

- `S43cat_categorias_medios_vida`
- `S43cat_condiciones_persona`
- `S43cat_condiciones_vivienda`
- `S43cat_enfermedades_cronicas`
- `S43cat_estados_registro`
- `S43cat_grados_lesion`
- `S43cat_materiales_pared`
- `S43cat_materiales_piso`
- `S43cat_materiales_techo`
- `S43cat_roles_familiares`
- `S43cat_tipos_danio_personal`
- `S43cat_tipos_discapacidad`
- `S43cat_tipos_documento`
- `S43cat_tipos_medios_vida`
- `S43cat_tipos_peligro`
- `S43cat_tipos_uso_instalacion`

No sustituir estos catálogos por enums codificados en la aplicación sin una decisión explícita.

## 9. Relaciones principales

```text
S43edan_emergencias
        |
        v
S43edan_formulario_2a
        |
        v
S43edan_formulario_2a_viviendas
        |
        v
S43edan_formulario_2a_familias
        |
        v
S43edan_formulario_2a_integrantes ----> S43personas
        |
        v
S43bah_planilla_entrega
        |
        | movimiento_almacen_id
        v
S43alm_movimientos
        |
        v
S43alm_movimiento_detalle ----> S43cat_bah_bienes
```

Personal:

```text
S43bah_personal
   |                         |
   | evaluador_id            | encargado_almacen_id
   v                         v
S43edan_formulario_2a   S43alm_movimientos
```
