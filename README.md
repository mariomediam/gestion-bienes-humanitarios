# Sistema de Gestión de Bienes de Ayuda Humanitaria

Sistema de Gestión de Bienes de Ayuda Humanitaria

## Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| Frontend | React 19, Vite 8, Tailwind CSS v4, Zustand |
| Backend | Django 6, Django REST Framework |
| Base de datos | SQL Server 2008 R2 (externa) |
| Contenedores | Docker + Docker Compose |
| Servidor web | Nginx (producción), Vite dev server (desarrollo) |
| WSGI | Gunicorn (producción) |

## Arquitectura de Producción

```
Usuario (navegador)
       │
    Puerto 3100
       │
┌──────────────────────────┐
│  Frontend (Nginx)        │  Contenedor Docker
│  - React SPA             │
│  - Proxy /api/ → backend │
└──────────┬───────────────┘
           │ Red interna Docker
┌──────────────────────────┐
│  Backend (Gunicorn)      │  Contenedor Docker
│  - Django REST Framework │
│  - 4 workers             │
└──────────┬───────────────┘
           │ Red local
┌──────────────────────────┐
│  SQL Server 2008 R2      │  Servidores existentes
│  192.168.100.20 (SIAC)   │
└──────────────────────────┘
```

---

## Desarrollo Local

### Requisitos

- Docker Desktop
- Git

### Pasos

```bash
# 1. Clonar repositorio
git clone <URL_DEL_REPOSITORIO>
cd sgbh

# 2. Copiar variables de entorno
cp backend/.env.example backend/.env.dev

# 3. Configurar backend/.env.dev con los valores correctos de BD

# 4. Iniciar contenedores
docker compose up --build

# 5. Acceder
# Frontend: http://localhost:5173
# Backend:  http://localhost:8000
```

### Comandos útiles (desarrollo)

```bash
docker compose up --build          # Iniciar con rebuild
docker compose logs -f             # Ver logs en tiempo real
docker compose down                # Detener todo
docker compose exec backend python manage.py migrate  # Migraciones
```

---

## Despliegue en Producción (Servidor Nuevo)

### Requisitos del servidor

- Ubuntu 20.04+ (x86_64)
- 4 GB RAM mínimo
- Acceso de red a los servidores SQL Server (192.168.100.20, 192.168.100.51)
- Puerto 3100 disponible

### Paso 1: Instalar Docker

```bash
# Dependencias
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Clave GPG de Docker
sudo install -m 0755 -d /etc/apt/keyrings
sudo bash -c 'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg'
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Repositorio (cambiar "focal" por el codename de tu versión de Ubuntu)
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine + Compose
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Habilitar e iniciar
sudo systemctl enable docker
sudo systemctl start docker

# Verificar
docker --version
docker compose version
```

### Paso 2: Clonar el proyecto

```bash
cd /opt
sudo git clone <URL_DEL_REPOSITORIO> sgbh
cd sgbh
```

### Paso 3: Crear archivo de variables de entorno

```bash
sudo nano /opt/sgbh/backend/.env.prod
```

Contenido (ajustar según el servidor):

```env
# Django
DEBUG=False
SECRET_KEY=<GENERAR_CLAVE_SEGURA>
ALLOWED_HOSTS=192.168.100.59,localhost,127.0.0.1
USE_SSL=False

# Database - SQL Server
DB_HOST=<HOST_SQL_SERVER>
DB_PORT=1433
DB_USERNAME=<USUARIO_SQL>
DB_PASSWORD=<CONTRASEÑA_SQL>
DB_NAME=GENERAL
DB_SIAC=SIAC

# System code
SYSTEM_CODE=43

# Document storage (carpeta del host montada en el contenedor)
STORAGE_ROOT=/app/storage

# CORS
CORS_ALLOWED_ORIGINS=http://192.168.100.59:3100

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=30
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# RENIEC / PIDE
RENIEC_NUDNIUSUARIO=<DNI_USUARIO_PIDE>
RENIEC_NURUCUSUARIO=<RUC_USUARIO_PIDE>
RENIEC_PASSWORD=<CONTRASEÑA_PIDE>
RENIEC_TIMEOUT=10
```

Para generar un SECRET_KEY seguro:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Paso 4: Crear la carpeta de documentos y levantar

```bash
sudo mkdir -p /opt/sgbh/storage
cd /opt/sgbh
sudo docker compose -f docker-compose.prod.yml up -d --build
```

### Paso 5: Verificar

```bash
# Estado de contenedores
sudo docker compose -f docker-compose.prod.yml ps

# Logs
sudo docker compose -f docker-compose.prod.yml logs -f

# Probar en navegador
# http://<IP_DEL_SERVIDOR>:3100
```

---

## Actualizar Producción (después de cambios en el código)

Cada vez que hagas cambios en el código y quieras llevarlos a producción:

### Desde tu máquina de desarrollo

```bash
# 1. Hacer commit de los cambios
git add .
git commit -m "feat: descripción del cambio"

# 2. Subir al repositorio
git push
```

### En el servidor de producción

```bash
cd /opt/sgbh

# 1. Descargar los cambios
sudo git pull

# 2. Reconstruir y reiniciar contenedores
sudo docker compose -f docker-compose.prod.yml up -d --build
```

**Nota:** Si solo cambiaste código del backend (sin nuevas dependencias), puedes reconstruir solo ese servicio:

```bash
sudo docker compose -f docker-compose.prod.yml up -d --build backend
```

Si solo cambiaste el frontend:

```bash
sudo docker compose -f docker-compose.prod.yml up -d --build frontend
```

---

## Comandos Útiles (Producción)

```bash
cd /opt/sgbh

# Ver estado de contenedores
sudo docker compose -f docker-compose.prod.yml ps

# Ver logs en tiempo real
sudo docker compose -f docker-compose.prod.yml logs -f

# Ver logs de un servicio específico
sudo docker compose -f docker-compose.prod.yml logs -f backend
sudo docker compose -f docker-compose.prod.yml logs -f frontend

# Reiniciar contenedores (sin reconstruir)
sudo docker compose -f docker-compose.prod.yml restart

# Detener todo
sudo docker compose -f docker-compose.prod.yml down

# Entrar al contenedor del backend (debug)
sudo docker compose -f docker-compose.prod.yml exec backend bash

# Ejecutar migraciones
sudo docker compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Limpiar imágenes antiguas (liberar espacio en disco)
sudo docker image prune -f
```

---

## Estructura de Archivos Clave

```
sgbh/
├── docker-compose.yml          # Desarrollo
├── docker-compose.prod.yml     # Producción
├── deploy.sh                   # Script de despliegue automático
│
├── backend/
│   ├── Dockerfile              # Imagen desarrollo
│   ├── Dockerfile.prod         # Imagen producción (Gunicorn)
│   ├── entrypoint.prod.sh      # Entrypoint producción (permisos)
│   ├── .env.dev                # Variables desarrollo (no commitear)
│   ├── .env.prod               # Variables producción (no commitear)
│   ├── .env.example            # Plantilla de variables
│   └── requirements.txt
│
├── frontend/
│   ├── Dockerfile              # Imagen desarrollo
│   ├── Dockerfile.prod         # Imagen producción (Nginx)
│   ├── nginx.conf              # Configuración de Nginx
│   └── .env.example            # Plantilla de variables
│
└── AGENTS.md                   # Especificación funcional
```

---

## Solución de Problemas

### El backend no conecta a SQL Server

Verificar que el contenedor puede alcanzar los servidores de BD:

```bash
sudo docker compose -f docker-compose.prod.yml exec backend python -c "
import os, socket
host = os.environ['DB_HOST']
port = int(os.environ.get('DB_PORT', '1433'))
try:
    s = socket.create_connection((host, port), timeout=5)
    s.close()
    print(f'{host}:{port} - OK')
except Exception as e:
    print(f'{host}:{port} - ERROR: {e}')
"
```

### Error de permisos al subir archivos

Los documentos quedan en `/opt/sgbh/storage` del servidor. Verificar permisos:

```bash
sudo mkdir -p /opt/sgbh/storage
sudo docker compose -f docker-compose.prod.yml exec backend ls -la /app/storage
```

### Puerto 3100 ya en uso

Verificar qué proceso usa el puerto:

```bash
sudo ss -tlnp | grep 3100
```

Cambiar el puerto en `docker-compose.prod.yml` (línea `ports: - "3100:80"`) y en `CORS_ALLOWED_ORIGINS` de `backend/.env.prod`.

### Limpiar todo y empezar de cero

```bash
cd /opt/sgbh
sudo docker compose -f docker-compose.prod.yml down -v   # -v elimina volúmenes
sudo docker compose -f docker-compose.prod.yml up -d --build
```

**Advertencia:** El flag `-v` elimina el volumen de archivos estáticos. Los documentos de `/opt/sgbh/storage` permanecen en el disco del servidor.
