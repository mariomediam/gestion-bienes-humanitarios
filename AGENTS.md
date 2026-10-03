# Instrucciones del proyecto

Este proyecto implementa un sistema para la gestión de Evaluación de Daños y Análisis de Necesidades (EDAN), la Planilla de Entrega de Bienes de Ayuda Humanitaria (BAH) y el control de almacén de bienes.

## Regla principal

No inventar reglas de negocio, campos, estados, relaciones, catálogos, tecnologías ni flujos que no estén definidos en la documentación del proyecto o en el código existente.

Si una decisión necesaria no está documentada, detener la implementación de esa parte y pedir aclaración al usuario.

## Fuentes de verdad

Antes de modificar código relacionado con el dominio, revisar en este orden:

1. `database/schema-SIAC-S43.sql`: esquema SQL definitivo entregado por el usuario.
2. `docs/01-modelo-base-datos.md`: mapa del modelo y relaciones principales.
3. `docs/02-reglas-negocio-edan.md`: reglas del Formulario EDAN 2A.
4. `docs/03-reglas-negocio-bah.md`: reglas de la Planilla BAH.
5. `docs/04-reglas-negocio-almacen.md`: reglas de almacén, préstamos, devoluciones y transformaciones.
6. `docs/05-integracion-modulos.md`: relaciones entre EDAN, BAH y almacén.
7. `docs/06-decisiones-no-definidas.md`: aspectos que no deben suponerse.

En caso de contradicción entre documentación generada y `database/schema-SIAC-S43.sql`, prevalece el esquema SQL definitivo para nombres, tipos de datos, nulabilidad, PK, FK, UNIQUE, DEFAULT y CHECK.

## Base de datos

* Motor: Microsoft SQL Server 2008 R2.
* Base de datos: `SIAC`.
* Las tablas de este módulo utilizan el prefijo `S43`.
* No renombrar tablas o columnas existentes sin autorización expresa.
* No agregar columnas para duplicar información que ya pueda obtenerse de relaciones existentes, salvo requerimiento explícito.
* No eliminar ni sustituir restricciones del esquema sin autorización.
* No asumir valores numéricos de catálogos. Consultar los catálogos por su código o por los datos existentes.

## Reglas críticas

* La Planilla BAH corresponde a una sola familia y a un solo integrante receptor.
* Los bienes de una Planilla BAH se almacenan en `S43alm\_movimiento\_detalle`; no existe una tabla de detalle BAH separada.
* `S43bah\_planilla\_entrega.movimiento\_almacen\_id` relaciona la planilla con el movimiento de almacén.
* En almacén, una cantidad positiva representa ingreso y una cantidad negativa representa salida.
* Los movimientos en borrador no deben afectar el stock. El stock operativo se deriva de movimientos confirmados.
* Una devolución de préstamo debe referenciar al movimiento original mediante `movimiento\_origen\_id`.
* Una transformación se registra como un único movimiento: bienes consumidos con cantidad negativa y bienes obtenidos con cantidad positiva.
* Las cantidades fraccionarias usan `DECIMAL(18,6)` y, cuando sea necesario conservar la fracción original, el campo textual correspondiente (`cantidad\_texto`, `cantidad\_base\_texto`, etc.).
* Una vez emitida la Planilla BAH correspondiente, el Formulario EDAN 2A relacionado no debe poder modificarse. El bloqueo se determina por relaciones; no se agrega una bandera de bloqueo al formulario.

## Desarrollo

* Mantener la lógica de negocio separada de la presentación.
* Centralizar validaciones críticas para evitar que distintos puntos de entrada apliquen reglas diferentes.
* Las operaciones que afecten varias tablas relacionadas deben ser atómicas.
* No confiar solo en la interfaz para reglas de integridad; validar también en la capa de negocio y/o en procedimientos de base de datos según la arquitectura existente.
* No crear una tabla de stock editable manualmente sin aprobación. El modelo actual se basa en movimientos.


## Tecnologías de aplicación

## Frontend

- JavaScript
- React

Responsabilidades principales:

- interfaz de usuario;
- formularios;
- navegación;
- validaciones de presentación;
- consumo de la API REST;
- visualización de información;
- manejo de estados de interfaz.

## Backend

- Python
- Django
- Django REST Framework

Responsabilidades principales:

- API REST;
- reglas de negocio;
- validaciones;
- autenticación e integración de usuarios;
- autorización;
- persistencia;
- auditoría;
- generación de reportes;
- gestión de archivos;
- integraciones institucionales.

## Base de datos

- Microsoft SQL Server 2008 R2.

La aplicación debe mantenerse preparada para una migración futura a una versión moderna de SQL Server.

### Regla importante

No utilizar características exclusivas de versiones recientes de SQL Server sin verificar previamente su compatibilidad con SQL Server 2008 R2.

Cuando sea posible:

- utilizar el ORM de Django;
- encapsular consultas SQL específicas;
- evitar dependencia innecesaria de funciones propietarias;

## Servidor

La aplicación será desplegada en infraestructura de la Municipalidad Provincial de Piura.

El frontend y backend estarán alojados en un servidor de aplicaciones.

La base de datos puede encontrarse en un servidor independiente.

Los documentos digitales serán almacenados en el sistema de archivos del servidor o en la ubicación institucional que posteriormente sea definida.

---

# 5. Autenticación y usuarios

El sistema utilizará el mecanismo institucional existente de gestión de usuarios.

No debe implementarse un sistema paralelo de usuarios si la funcionalidad ya existe institucionalmente.

La aplicación tendrá una pantalla propia de acceso, pero deberá integrarse con el Sistema Integrado de Gestión de Usuarios mediante los mecanismos institucionales disponibles.

Los permisos deben manejarse por usuario, perfil, formulario y operación.

Las operaciones pueden incluir:

- consultar;
- agregar;
- modificar;
- validar;
- inactivar;
- visualizar documentos;
- descargar documentos;
- imprimir;
- exportar;
- administrar catálogos.

La autorización siempre debe verificarse también en el backend.

Ocultar un botón en React NO constituye una medida de seguridad suficiente.

---

# Almacenamiento de archivos del sistema

Los archivos deben almacenarse fuera de la base de datos.

La base de datos debe guardar únicamente información como:

- identificador;
- entidad relacionada;
- tipo de documento;
- nombre original;
- nombre almacenado;
- ruta o identificador;
- extensión;
- tamaño;
- fecha de carga;
- usuario;
- descripción;
- estado.

No almacenar archivos en campos Base64 dentro de SQL Server salvo requerimiento técnico expresamente aprobado.

Los archivos no deben quedar públicamente accesibles por una URL directa sin autorización.

La ubicación raíz de los documentos debe definirse mediante configuración.

---

# Protección de información

Nunca:

- registrar contraseñas en texto plano;
- colocar credenciales en código fuente;
- subir secretos al repositorio;
- mostrar stack traces al usuario;
- exponer rutas internas de archivos;
- permitir descargas sin verificar permisos;
- enviar al frontend información sensible que no necesita.

Utilizar variables de entorno o mecanismos institucionales para:

- credenciales;
- cadenas de conexión;
- tokens;
- endpoints;
- claves;
- rutas.

---

# 31. Validación de entradas

Validar tanto en frontend como backend:

- campos obligatorios;
- longitud;
- formato;
- tipos;
- relaciones;
- archivos;
- permisos;
- reglas de negocio.

Las validaciones del frontend mejoran la experiencia de usuario.

Las validaciones del backend garantizan la integridad del sistema.

---

# 32. Accesibilidad

La interfaz debe seguir buenas prácticas de accesibilidad.

Priorizar:

- HTML semántico;
- labels asociados correctamente;
- navegación mediante teclado;
- foco visible;
- contraste adecuado;
- mensajes de error claros;
- textos descriptivos;
- atributos `alt`;
- no utilizar únicamente colores para representar estados;
- tamaños de controles adecuados;
- componentes reutilizables y accesibles.

No utilizar ARIA innecesariamente cuando HTML semántico resuelva correctamente el problema.

---

# 33. Arquitectura

Mantener separación clara entre:

```text
Frontend
    ↓
API REST
    ↓
Reglas de negocio
    ↓
Acceso a datos
    ↓
SQL Server
```

Las integraciones externas deben mantenerse desacopladas:

```text
Backend
 ├── Base de datos
 ├── RENIEC
 ├── Sistema institucional de usuarios
 └── Repositorio documental
```

Evitar acoplamientos directos entre componentes que dificulten mantenimiento o migración.

---

# 34. Organización del backend

No colocar toda la lógica en las views de Django.

Cuando una operación contenga reglas de negocio relevantes, utilizar una estructura equivalente a:

```text
View / ViewSet
      ↓
Serializer
      ↓
Service / lógica de negocio
      ↓
Model / Repository
      ↓
Database
```

La estructura exacta debe respetar primero la organización existente del proyecto.

No crear nuevas capas únicamente por seguir un patrón si no aportan valor.

---

# 35. Organización del frontend

Los componentes React deben mantenerse:

- pequeños;
- reutilizables;
- claros;
- enfocados en una responsabilidad.

Evitar componentes monolíticos que contengan:

- consultas;
- formularios;
- validaciones;
- tablas;
- modales;
- lógica de negocio;

todo en el mismo archivo.

Extraer componentes y hooks cuando exista reutilización o complejidad real.

No fragmentar innecesariamente componentes simples.

---

# 36. API REST

Mantener endpoints coherentes y previsibles.

Ejemplos conceptuales:

```text
/api/personas/
/api/emergencias/
/api/planillas-bah/
/api/catalogos/
/api/reportes/
```

Antes de crear un endpoint nuevo, comprobar si una funcionalidad equivalente ya existe.

Evitar endpoints duplicados que hagan prácticamente lo mismo.

---

# 37. Manejo de errores

Los errores enviados al frontend deben ser comprensibles y estructurados.

Ejemplo conceptual:

```json
{
  "error": true,
  "message": "No se pudo validar la persona.",
  "details": {}
}
```

No exponer al usuario:

- stack traces;
- SQL;
- rutas del servidor;
- secretos;
- estructuras internas innecesarias.

---

# 38. Configuración centralizada

No introducir valores fijos innecesarios en el código fuente.

Configurar externamente:

- URLs de servicios;
- rutas de archivos;
- límites de carga;
- formatos permitidos;
- parámetros institucionales;
- tiempos de espera;
- credenciales;
- características habilitadas.

Cuando un valor pueda cambiar sin recompilar la aplicación, preferir configuración.

---

# 40. Compatibilidad con SQL Server 2008 R2

Antes de generar:

- consultas;
- funciones;
- índices;
- restricciones;

comprobar su compatibilidad con SQL Server 2008 R2.

Evitar depender innecesariamente de funcionalidades introducidas en versiones posteriores.

El sistema debe facilitar una futura migración a una versión moderna de SQL Server.

---

# 41. Integridad referencial

Mantener correctamente:

- claves primarias;
- claves foráneas;
- restricciones;
- índices;
- unicidad;
- relaciones.

Evitar registros huérfanos.

Cuando exista una baja lógica, analizar antes de utilizar `CASCADE DELETE`.

No eliminar información histórica por cascada sin revisar el impacto funcional.

---

# 42. Convenciones generales

Mantener:

- nombres descriptivos;
- consistencia de nomenclatura;
- separación de responsabilidades;
- reutilización razonable;
- funciones pequeñas;
- comentarios únicamente cuando aporten contexto;
- configuraciones fuera del código cuando corresponda.

Evitar:

- código duplicado;
- nombres ambiguos;
- variables globales innecesarias;
- consultas SQL dispersas;
- reglas de negocio repetidas;
- valores mágicos;
- componentes excesivamente grandes.

---

# 43. Regla para cambios en base de datos

Antes de modificar una tabla o modelo:

1. identificar dónde se utiliza;
2. revisar relaciones;
3. revisar serializers;
4. revisar endpoints;
5. revisar formularios;
6. revisar reportes;
7. revisar migraciones;
8. revisar posibles datos existentes.

No renombrar ni eliminar columnas existentes sin evaluar previamente el impacto.

Cuando sea posible, mantener compatibilidad con datos históricos.

---

# 44. Regla para modificar funcionalidades existentes

Antes de cambiar una funcionalidad:

1. revisar el código actual;
2. identificar la regla de negocio;
3. identificar los componentes relacionados;
4. identificar endpoints;
5. identificar modelos;
6. identificar permisos;
7. identificar pruebas;
8. realizar el cambio mínimo necesario.

No reescribir módulos completos cuando una modificación localizada sea suficiente.

---

# 45. Uso de librerías

Antes de agregar una dependencia:

1. comprobar si el proyecto ya dispone de una solución equivalente;
2. evaluar compatibilidad con las versiones actuales;
3. evaluar mantenimiento de la librería;
4. evaluar impacto en producción;
5. comprobar compatibilidad con la infraestructura institucional.

No introducir una librería para resolver un problema trivial que pueda solucionarse de manera sencilla con las dependencias existentes.

---

# 46. Pruebas

Las funcionalidades críticas deben ser comprobadas mediante pruebas.

Priorizar pruebas para:

- reglas de negocio;
- validaciones;
- permisos;
- estados;
- duplicidades;
- historial;
- documentos;
- reportes;
- integraciones.

Los Términos de Referencia requieren pruebas:

- unitarias;
- integrales;
- de sistema.

Cuando se corrija un error importante, agregar una prueba que permita detectar nuevamente el mismo problema cuando sea razonable.

---

# 50. Principios para Cursor AI

Al trabajar en este proyecto:

### HACER

- revisar primero el código existente;
- respetar la arquitectura actual;
- reutilizar componentes existentes;
- reutilizar servicios existentes;
- verificar permisos;
- preservar información histórica;
- utilizar baja lógica cuando corresponda;
- implementar reglas críticas en backend;
- comprobar compatibilidad con SQL Server 2008 R2;
- mantener el código sencillo;
- realizar cambios pequeños y verificables.

### NO HACER

- inventar reglas de negocio;
- eliminar información histórica;
- cambiar nombres de tablas arbitrariamente;
- crear nuevas autenticaciones;
- duplicar endpoints;
- hardcodear catálogos;
- exponer archivos públicamente;
- introducir credenciales en código;
- agregar dependencias innecesarias;
- reescribir módulos sin necesidad;
- utilizar características incompatibles con SQL Server 2008 R2.

---

# 51. Ante una ambigüedad

Si una solicitud requiere tomar una decisión funcional que no se desprende claramente del código, de este documento o de los requerimientos existentes:

1. identificar la ambigüedad;
2. explicar brevemente las alternativas;
3. preguntar antes de implementar una decisión que pueda afectar:
   - datos;
   - estados;
   - permisos;
   - historial;
   - arquitectura;
   - integraciones.

No inventar comportamiento institucional.

---

# 52. Prioridades del proyecto

Cuando existan varias alternativas técnicamente válidas, priorizar:

1. integridad de la información;
2. cumplimiento de las reglas de negocio;
3. seguridad y confidencialidad;
4. trazabilidad;
5. compatibilidad con infraestructura municipal;
6. mantenibilidad;
7. accesibilidad;
8. experiencia de usuario;
9. rendimiento;
10. estética.

---

# 53. Resumen operativo para el agente

Antes de realizar cualquier cambio importante, recordar:

```text
El sistema gestiona la  Evaluación de Daños y Análisis de Necesidades (EDAN), la Planilla de Entrega de Bienes de Ayuda Humanitaria (BAH) y el control de almacén de bienes.

No eliminar históricos.

Los documentos se almacenan fuera de SQL Server.

La seguridad se controla en backend.

Los permisos institucionales deben respetarse.

RENIEC es una integración auxiliar, no una dependencia absoluta.

SQL Server 2008 R2 sigue siendo un requisito actual.

Ante una regla de negocio no definida: preguntar, no inventar.
```