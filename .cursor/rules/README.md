# Reglas de Cursor AI

Este directorio contiene las reglas que Cursor AI seguirá automáticamente al trabajar en este proyecto.

## 📋 Archivos de reglas

### Reglas globales (siempre activas)
- **general-standards.mdc**: Estándares generales del proyecto (stack, idioma, convenciones)
- **git-conventions.mdc**: Convenciones de Git y commits

### Reglas específicas por archivo
- **react-conventions.mdc**: Se activa con archivos `frontend/**/*.{jsx,js}`
  - Imports con alias `@`
  - Zustand para estado global
  - Tailwind CSS para estilos
  - Sonner para alertas

- **django-conventions.mdc**: Se activa con archivos `backend/**/*.py`
  - django-environ para variables
  - Try-catch en TODOS los métodos
  - Permisos explícitos
  - Pytest con 80% cobertura

- **sonner-notifications.mdc**: Se activa con archivos `frontend/**/*.{jsx,js}`
  - Setup y configuración de Sonner
  - Ejemplos de uso
  - Integración con Zustand

## 🎯 Cómo funcionan

1. **Reglas globales**: Se aplican en todas las conversaciones
2. **Reglas específicas**: Se activan cuando abres archivos que coinciden con el patrón `globs`
3. Cursor AI lee estas reglas automáticamente

## ✅ Puntos clave

### Frontend
- ✅ Alias `@` en imports (NO `../../`)
- ✅ Zustand para estado global (NO Context API)
- ✅ Sonner para alertas (NO `alert()`)
- ✅ Solo Tailwind CSS

### Backend
- ✅ Try-catch en TODOS los métodos de views
- ✅ django-environ para variables
- ✅ Pytest con 80% cobertura mínima
- ✅ Permisos explícitos en views

### General
- ✅ Código en inglés, mensajes en español
- ✅ NO commitear archivos `.env`
- ✅ Commits descriptivos en español




## Contexto funcional y técnico del sistema

 El contexto lo puedes encontrar en `/docs`.

- `00-contexto-sistema.md`: alcance funcional y conceptos principales.
- `01-modelo-base-datos.md`: tablas y relaciones del esquema definitivo.
- `02-reglas-negocio-edan.md`: reglas del Formulario EDAN 2A.
- `03-reglas-negocio-bah.md`: reglas de la Planilla de Entrega de BAH.
- `04-reglas-negocio-almacen.md`: reglas del módulo de almacén.
- `05-integracion-modulos.md`: interacción EDAN → BAH → almacén.
- `06-decisiones-no-definidas.md`: decisiones que Cursor no debe asumir.

El esquema exacto de base de datos está en `/database/schema-SIAC-S43.sql`.