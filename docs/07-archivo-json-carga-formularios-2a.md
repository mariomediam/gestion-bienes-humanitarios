# Archivo JSON de carga de Formularios EDAN 2A

Documento para quien desarrolla el sistema móvil. Describe el archivo que ese sistema debe generar para que el sistema web registre Formularios de Campo EDAN 2A.

Un archivo de ejemplo, con la misma estructura, está en `backend/ejemplos/carga-formularios-2a.json`.

## Qué produce el sistema móvil

Un archivo de texto con extensión `.json`, codificado en UTF-8. Puede incluir la marca de orden de bytes (BOM) al inicio; el sistema la descarta.

El contenido es un objeto con una sola lista, `formularios`. Cada elemento de esa lista es un formulario EDAN 2A. El archivo puede traer uno o varios formularios y se carga completo: si un formulario falla, no se guarda ninguno de ese archivo.

```json
{
  "formularios": [
    {
      "fecha_empadronamiento": "2026-10-15",
      "hora_empadronamiento": "08:30",
      "localidad": "Catacaos",
      "viviendas": []
    }
  ]
}
```

La lista `formularios` es obligatoria y no puede estar vacía.

## Qué completa el sistema web

El archivo del móvil no lleva la emergencia, el distrito ni el evaluador. Al cargar el archivo, el operador del sistema web indica:

- el código SINPAD de una emergencia ya registrada;
- el distrito;
- el evaluador.

Con esos datos el sistema web completa, en cada formulario, estos campos. El móvil no debe enviarlos:

| Campo | Origen |
| --- | --- |
| `emergencia_id` | Emergencia del código SINPAD |
| `departamento_id`, `provincia_id`, `distrito_id` | Distrito elegido |
| `evaluador_id` | Evaluador elegido |
| `institucion` | Siempre `Municipalidad Provincial de Piura` |
| `estado_registro_id` | Siempre `1` (ACTIVO) |
| `rol_familiar_id` | Según el orden de los integrantes, ver más abajo |
| `c_usuari_login` | Usuario que carga el archivo |

Tampoco se envían identificadores que el sistema asigna al guardar: `formulario_2a_id`, `vivienda_id`, `familia_id`, `persona_id`, `integrante_id`, `medio_vida_id` ni `numero_orden`.

## Estructura

```text
formularios[]
  viviendas[]
    familias[]
      integrantes[]
        persona
      medios_vida[]
```

Las listas `viviendas`, `familias`, `integrantes` y `medios_vida` pueden omitirse o ir vacías. El orden dentro de cada lista se conserva: la primera vivienda queda como vivienda 1, la primera familia de esa vivienda como familia 1, y así con integrantes y medios de vida.

El primer integrante de cada familia queda como jefe de familia. Los siguientes quedan como dependientes. El móvil no envía el rol; lo define la posición en `integrantes`.

## Reglas generales de los valores

- Las fechas van en `AAAA-MM-DD`. Ejemplo: `2026-10-15`.
- Las horas van en `HH:MM` o `HH:MM:SS`, en 24 horas. Ejemplo: `08:30`.
- Los identificadores de catálogo y las cantidades son números JSON, no texto. Correcto: `1`. Incorrecto: `"1"`.
- Los valores sí/no son `true` o `false`.
- Un dato que no existe se envía como `null`. En los textos opcionales, `""` equivale a `null`.
- El sistema recorta espacios al inicio y al final de los textos.
- La comparación de nombres y de números de documento no distingue mayúsculas de minúsculas.
- Un identificador de catálogo tiene que existir en las tablas de este documento. Si no existe, se rechaza todo el archivo.

Los mensajes de error indican la posición, empezando en 1. Ejemplo: `Formulario 2, vivienda 1, familia 1, integrante 2: ...`.

## Formulario

| Campo | Obligatorio | Tipo | Límite | Si no hay dato |
| --- | --- | --- | --- | --- |
| `fecha_empadronamiento` | Sí | Fecha `AAAA-MM-DD` |  |  |
| `hora_empadronamiento` | No | Hora `HH:MM` o `HH:MM:SS` |  | `null` |
| `localidad` | No | Texto | 200 | `null` |
| `barrio_sector_urbanizacion` | No | Texto | 250 | `null` |
| `centro_poblado` | No | Texto | 200 | `null` |
| `caserio` | No | Texto | 200 | `null` |
| `anexo` | No | Texto | 200 | `null` |
| `calle_manzana` | No | Texto | 250 | `null` |
| `edificio_piso_dpto` | No | Texto | 250 | `null` |
| `otros_ubicacion` | No | Texto | 250 | `null` |
| `numero_hoja` | No | Entero mayor que cero |  | `1` |
| `total_hojas` | No | Entero mayor que cero |  | `null` |
| `viviendas` | No | Lista |  | Lista vacía |

Si `total_hojas` tiene valor, debe ser mayor o igual que `numero_hoja`.

## Vivienda

| Campo | Obligatorio | Tipo | Límite | Si no hay dato |
| --- | --- | --- | --- | --- |
| `numero_lote` | Sí | Texto | 50 |  |
| `tenencia_propia` | No | `true` o `false` |  | `null` |
| `tipo_uso_instalacion_id` | Sí | Entero de catálogo |  |  |
| `condicion_vivienda_id` | No | Entero de catálogo |  | `null` |
| `material_techo_id` | No | Entero de catálogo |  | `null` |
| `material_pared_id` | No | Entero de catálogo |  | `null` |
| `material_piso_id` | No | Entero de catálogo |  | `null` |
| `familias` | No | Lista |  | Lista vacía |

`tenencia_propia` en `true` significa tenencia propia. `false` significa que no lo es. `null` significa que no se registró.

## Familia

La familia no tiene campos propios. Solo agrupa integrantes y medios de vida.

```json
{
  "integrantes": [],
  "medios_vida": []
}
```

## Integrante

| Campo | Obligatorio | Tipo | Límite | Si no hay dato |
| --- | --- | --- | --- | --- |
| `persona` | Sí | Objeto |  |  |
| `edad` | Sí | Entero | 0 a 130 |  |
| `condicion_persona_id` | Sí | Entero de catálogo |  |  |
| `tipo_danio_personal_id` | No | Entero de catálogo |  | `null` |
| `grado_lesion_id` | No | Entero de catálogo |  | `null` |
| `gestante_semanas` | No | Entero | 1 a 45 | `null` |
| `tipo_discapacidad_id` | No | Entero de catálogo |  | `null` |
| `enfermedad_cronica_id` | No | Entero de catálogo |  | `null` |

`grado_lesion_id` solo puede tener valor cuando `tipo_danio_personal_id` es `1` (Lesionado). En cualquier otro caso, incluido cuando no hay daño personal, `grado_lesion_id` debe ser `null`.

`edad` es la edad declarada en el empadronamiento. El sistema no la calcula a partir de `fecha_nacimiento`.

La misma persona no puede repetirse dentro de una familia. Tampoco puede figurar dos veces como integrante de la misma emergencia (el mismo código SINPAD), aunque esté en otro formulario del archivo o ya exista en el sistema.

## Persona

La persona viaja dentro del integrante. No se envía `persona_id`.

| Campo | Obligatorio | Tipo | Límite | Si no hay dato |
| --- | --- | --- | --- | --- |
| `tipo_documento_id` | Condicional | Entero de catálogo |  | `null` |
| `numero_documento` | Condicional | Texto | 20 | `null` |
| `apellido_paterno` | Sí | Texto | 50 |  |
| `apellido_materno` | Sí | Texto | 50 |  |
| `nombres` | Sí | Texto | 150 |  |
| `fecha_nacimiento` | No | Fecha `AAAA-MM-DD` |  | `null` |
| `sexo` | Sí | Un carácter |  |  |
| `telefono` | No | Texto | 50 | `""` |
| `correo` | No | Texto | 50 | `""` |
| `esta_activo` | No | `true` o `false` |  | `true` |

`sexo` usa estos valores:

| Valor | Significado |
| --- | --- |
| `M` | Masculino |
| `F` | Femenino |
| `D` | Desconocido |

`tipo_documento_id` y `numero_documento` van juntos. O ambos tienen valor, o ambos van en `null`. No se acepta tipo sin número, ni número sin tipo.

`telefono` y `correo` vacíos se guardan como texto vacío, no como `null`. El resto de textos opcionales vacíos se guardan como `null`.

En un alta desde el móvil, enviar `esta_activo` en `true`.

### Cómo se reconoce una persona que ya existe

Antes de crear una persona, el sistema busca si ya está registrada. Si la reutiliza, no modifica el registro existente: se conservan teléfono, correo, sexo y demás datos ya guardados. El integrante nuevo apunta a esa persona.

Con documento:

1. Busca por `tipo_documento_id` y `numero_documento`.
2. Si hay más de una coincidencia, rechaza el archivo.
3. Si hay una coincidencia, compara apellido paterno, apellido materno y nombres. Si coinciden, reutiliza esa persona. Si no coinciden, rechaza el archivo. El mensaje incluye el nombre enviado y el nombre guardado.
4. La fecha de nacimiento no interviene en esta comparación.

Sin documento:

1. Busca por apellido paterno, apellido materno, nombres y `fecha_nacimiento`.
2. Una fecha en `null` solo coincide con otra fecha en `null`.
3. Si hay más de una coincidencia, rechaza el archivo.
4. Si hay una coincidencia, reutiliza esa persona.

Si no hay coincidencia, crea la persona. Esa alta también se rechaza cuando ya existe el mismo documento o la misma combinación de apellidos, nombres y fecha de nacimiento.

Para que la reutilización funcione, el móvil debe enviar los nombres iguales a los ya registrados, sin importar mayúsculas ni espacios laterales.

## Medio de vida

| Campo | Obligatorio | Tipo | Límite | Si no hay dato |
| --- | --- | --- | --- | --- |
| `tipo_medio_vida_id` | Sí | Entero de catálogo |  |  |
| `cantidad` | Sí | Entero mayor que cero |  |  |
| `observacion` | No | Texto | 500 | `null` |

Una familia no puede repetir el mismo `tipo_medio_vida_id`. `observacion` es un texto libre; no sustituye al catálogo.

## Catálogos

### Tipo de documento (`tipo_documento_id`)

| Id | Código | Nombre |
| --- | --- | --- |
| 1 | DNI | Documento Nacional de Identidad - DNI |
| 2 | PASAPORTE | Pasaporte |
| 3 | CARNET_EXTRANJERIA | Carnet de Extranjería |
| 4 | OTRO | Otro documento |

### Tipo de uso de la instalación (`tipo_uso_instalacion_id`)

| Id | Código | Nombre |
| --- | --- | --- |
| 1 | VIVIENDA | Vivienda |
| 2 | MEDIO_VIDA | Medio de vida |

### Condición de la vivienda (`condicion_vivienda_id`)

| Id | Código | Nombre |
| --- | --- | --- |
| 1 | AFECTADA | Afectada |
| 2 | INHABITABLE | Inhabitable |
| 3 | DESTRUIDA | Destruida |

### Material de techo (`material_techo_id`)

| Id | Nombre |
| --- | --- |
| 1 | Concreto armado |
| 2 | Madera |
| 3 | Tejas |
| 4 | Plancha de calamina |
| 5 | Caña o estera con torta de barro |
| 6 | Estera |
| 7 | Paja, hojas de palmera |
| 8 | Otro material |

### Material de pared (`material_pared_id`)

| Id | Nombre |
| --- | --- |
| 1 | Ladrillo o bloque de cemento |
| 2 | Piedra o sillar con cal o cemento |
| 3 | Adobe o tapial |
| 4 | Quincha (caña con barro) |
| 5 | Piedra con barro (pirca) |
| 6 | Madera |
| 7 | Estera |
| 8 | Otro material |

### Material de piso (`material_piso_id`)

| Id | Nombre |
| --- | --- |
| 1 | Parquet o madera pulida |
| 2 | Láminas asfálticas, vinilos o similares |
| 3 | Loseta, terrazos, cerámicos |
| 4 | Madera |
| 5 | Cemento |
| 6 | Tierra |
| 7 | Otro material |

### Condición de la persona (`condicion_persona_id`)

| Id | Código | Nombre |
| --- | --- | --- |
| 1 | DAMNIFICADO | Damnificado |
| 2 | AFECTADO | Afectado |

### Tipo de daño personal (`tipo_danio_personal_id`)

| Id | Código | Nombre |
| --- | --- | --- |
| 1 | LESIONADO | Lesionado (Herido) |
| 2 | DESAPARECIDO | Desaparecido |
| 3 | FALLECIDO | Fallecido |

### Grado de lesión (`grado_lesion_id`)

Solo cuando `tipo_danio_personal_id` es `1`.

| Id | Código | Nombre |
| --- | --- | --- |
| 1 | G | Grave |
| 2 | M | Moderado |
| 3 | L | Leve |

### Tipo de discapacidad (`tipo_discapacidad_id`)

| Id | Nombre |
| --- | --- |
| 1 | Moverse o caminar |
| 2 | Ver |
| 3 | Oír |
| 4 | Hablar |
| 5 | Mental |
| 6 | Otro tipo de discapacidad |

### Enfermedad crónica (`enfermedad_cronica_id`)

| Id | Nombre |
| --- | --- |
| 1 | Anemia |
| 2 | Arritmias cardiacas |
| 3 | Asma bronquial |
| 4 | Desnutrición |
| 5 | Diabetes |
| 6 | Dislipemias o dislipidemias (colesterol, triglicéridos) |
| 7 | Enfermedades inmunológicas (artritis, artrosis, lupus) |
| 8 | Enfermedades psiquiátricas graves |
| 9 | Epilepsia |
| 10 | Esquizofrenia |
| 11 | Glaucoma |
| 12 | Hepatitis |
| 13 | Hipertensión arterial |
| 14 | Hipertiroidismo - hipotiroidismo |
| 15 | Hipertrofia prostática benigna |
| 16 | Hiperuricemia gota |
| 17 | Insuficiencia cardiaca |
| 18 | Insuficiencia coronaria |
| 19 | Insuficiencia renal crónica |
| 20 | Neuropatías desmielinizantes |
| 21 | Osteoporosis y descalcificación en general |
| 22 | Parkinson (síndrome y enfermedad) |
| 23 | Tuberculosis - TBC |
| 24 | Virus de la inmunodeficiencia humana - VIH |
| 25 | Otras |

### Tipo de medio de vida (`tipo_medio_vida_id`)

El móvil envía `tipo_medio_vida_id`. No envía la categoría: el sistema la obtiene del tipo.

| Id | Categoría | Nombre |
| --- | --- | --- |
| 1 | Comercio | Tienda/Bodega |
| 2 | Comercio | Restaurante |
| 3 | Comercio | Taller |
| 4 | Comercio | Zapatería |
| 5 | Turismo | Servicios turísticos de recreación |
| 6 | Turismo | Hospedaje |
| 7 | Turismo | Empresas de transporte turístico |
| 8 | Turismo | Hoteles |
| 9 | Otros | Panaderías |
| 10 | Otros | Ferreterías |
| 11 | Otros | Consultorios |
| 12 | Otros | Boticas o farmacias |
| 13 | Otros | Bazares |
| 14 | Otros | Tiendas de venta de telas |
| 15 | Otros | Puestos de mercado |
| 16 | Otros | Comercio ambulatorio |
| 17 | Otros | Comercio en general |

### Rol familiar

El móvil no envía este catálogo. Queda aquí para saber qué produce el orden de `integrantes`.

| Posición en `integrantes` | Id | Código | Nombre |
| --- | --- | --- | --- |
| Primero | 1 | J | Jefe de familia |
| Segundo en adelante | 2 | D | Dependiente |

## Ejemplo mínimo

Una vivienda con una familia. El primer integrante es el jefe de familia. El segundo es dependiente. El medio de vida `1` es Tienda/Bodega.

```json
{
  "formularios": [
    {
      "fecha_empadronamiento": "2026-10-15",
      "hora_empadronamiento": "08:30",
      "localidad": "Catacaos",
      "barrio_sector_urbanizacion": "Buenos Aires",
      "centro_poblado": null,
      "caserio": null,
      "anexo": null,
      "calle_manzana": "Mz. A lote 4",
      "edificio_piso_dpto": null,
      "otros_ubicacion": null,
      "numero_hoja": 1,
      "total_hojas": 1,
      "viviendas": [
        {
          "numero_lote": "04",
          "tenencia_propia": true,
          "tipo_uso_instalacion_id": 1,
          "condicion_vivienda_id": 1,
          "material_techo_id": 4,
          "material_pared_id": 3,
          "material_piso_id": 6,
          "familias": [
            {
              "integrantes": [
                {
                  "persona": {
                    "tipo_documento_id": 1,
                    "numero_documento": "45678901",
                    "apellido_paterno": "García",
                    "apellido_materno": "Ramos",
                    "nombres": "Ana María",
                    "fecha_nacimiento": "1988-04-12",
                    "sexo": "F",
                    "telefono": "969111222",
                    "correo": "",
                    "esta_activo": true
                  },
                  "edad": 38,
                  "condicion_persona_id": 1,
                  "tipo_danio_personal_id": 1,
                  "grado_lesion_id": 3,
                  "gestante_semanas": null,
                  "tipo_discapacidad_id": null,
                  "enfermedad_cronica_id": null
                },
                {
                  "persona": {
                    "tipo_documento_id": null,
                    "numero_documento": null,
                    "apellido_paterno": "García",
                    "apellido_materno": "Ramos",
                    "nombres": "Luis",
                    "fecha_nacimiento": "2016-09-03",
                    "sexo": "M",
                    "telefono": "",
                    "correo": "",
                    "esta_activo": true
                  },
                  "edad": 10,
                  "condicion_persona_id": 1,
                  "tipo_danio_personal_id": null,
                  "grado_lesion_id": null,
                  "gestante_semanas": null,
                  "tipo_discapacidad_id": null,
                  "enfermedad_cronica_id": null
                }
              ],
              "medios_vida": [
                {
                  "tipo_medio_vida_id": 1,
                  "cantidad": 1,
                  "observacion": "Tienda de abarrotes"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

En el primer integrante, `tipo_danio_personal_id` `1` es Lesionado y `grado_lesion_id` `3` es Leve. En la vivienda, el techo `4` es plancha de calamina, la pared `3` es adobe o tapial y el piso `6` es tierra.

## Situaciones que rechazan el archivo

- El archivo no es JSON, no es un objeto o `formularios` está vacío.
- Falta un campo obligatorio, el tipo no corresponde o se supera la longitud.
- Un identificador de catálogo no existe.
- `total_hojas` es menor que `numero_hoja`.
- Hay grado de lesión sin que el daño personal sea Lesionado (`1`).
- `gestante_semanas` está fuera del rango 1 a 45, o `edad` está fuera del rango 0 a 130.
- El documento y el tipo de documento no van juntos.
- La persona ya existe con ese documento, pero los apellidos o los nombres no coinciden.
- Hay más de una persona con el mismo documento, o más de una sin documento con los mismos apellidos, nombres y fecha de nacimiento.
- La misma persona aparece dos veces en la familia o ya es integrante de esa emergencia.
- La familia repite el mismo tipo de medio de vida.

El código SINPAD, el distrito y el evaluador no forman parte del archivo. Si al cargar el archivo el operador indica un SINPAD inexistente o que corresponde a más de una emergencia, la carga también se rechaza y no se guarda nada.
