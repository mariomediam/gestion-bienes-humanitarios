#!/bin/bash
set -e

# ============================================================
# Script de despliegue - Sistema de gestión de bienes humanitarios
# Servidor: Ubuntu 20.04 LTS (192.168.100.59)
# ============================================================

APP_DIR="/opt/sgbh"
COMPOSE_FILE="docker-compose.prod.yml"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ---- Verificar que se ejecuta como root ----
if [ "$EUID" -ne 0 ]; then
    log_error "Este script debe ejecutarse como root (sudo)"
    exit 1
fi

# ---- Verificar Docker ----
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker no está instalado. Ejecuta primero:"
        echo ""
        echo "  # Instalar dependencias"
        echo "  apt-get update"
        echo "  apt-get install -y ca-certificates curl gnupg lsb-release"
        echo ""
        echo "  # Agregar clave GPG de Docker"
        echo "  install -m 0755 -d /etc/apt/keyrings"
        echo "  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg"
        echo "  chmod a+r /etc/apt/keyrings/docker.gpg"
        echo ""
        echo "  # Agregar repositorio de Docker"
        echo "  echo \"deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu focal stable\" > /etc/apt/sources.list.d/docker.list"
        echo ""
        echo "  # Instalar Docker Engine + Compose"
        echo "  apt-get update"
        echo "  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin"
        echo ""
        echo "  # Iniciar Docker"
        echo "  systemctl enable docker"
        echo "  systemctl start docker"
        echo ""
        exit 1
    fi

    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose plugin no está instalado"
        echo "  apt-get install -y docker-compose-plugin"
        exit 1
    fi

    log_info "Docker $(docker --version | awk '{print $3}') detectado"
    log_info "Docker Compose $(docker compose version --short) detectado"
}

# ---- Verificar que el proyecto existe ----
check_project() {
    if [ ! -f "$APP_DIR/$COMPOSE_FILE" ]; then
        log_error "No se encontró $COMPOSE_FILE en $APP_DIR"
        echo "  Asegúrate de copiar el proyecto a $APP_DIR"
        exit 1
    fi

    if [ ! -f "$APP_DIR/backend/.env.prod" ]; then
        log_error "No se encontró backend/.env.prod"
        echo "  Copia backend/.env.example a backend/.env.prod y configura los valores"
        exit 1
    fi
    log_info "Proyecto encontrado en $APP_DIR"
}

# ---- Despliegue ----
deploy() {
    cd "$APP_DIR"

    log_info "Deteniendo contenedores anteriores (si existen)..."
    docker compose -f "$COMPOSE_FILE" down 2>/dev/null || true

    log_info "Construyendo imágenes..."
    docker compose -f "$COMPOSE_FILE" build --no-cache

    log_info "Iniciando contenedores..."
    docker compose -f "$COMPOSE_FILE" up -d

    log_info "Esperando a que el backend esté listo..."
    sleep 10

    log_info "Ejecutando migraciones..."
    docker compose -f "$COMPOSE_FILE" exec -T backend python manage.py migrate --noinput 2>/dev/null || log_warn "Migraciones omitidas (puede ser normal con SQL Server externo)"

    log_info "Verificando estado de los contenedores..."
    docker compose -f "$COMPOSE_FILE" ps
}

# ---- Verificación post-despliegue ----
verify() {
    echo ""
    log_info "=== Verificación post-despliegue ==="

    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3080 | grep -q "200"; then
        log_info "Frontend: OK (http://192.168.100.59:3080)"
    else
        log_warn "Frontend: Verificar manualmente en http://192.168.100.59:3080"
    fi

    echo ""
    log_info "=== Comandos útiles ==="
    echo "  Ver logs:        docker compose -f $COMPOSE_FILE logs -f"
    echo "  Ver logs backend: docker compose -f $COMPOSE_FILE logs -f backend"
    echo "  Reiniciar:       docker compose -f $COMPOSE_FILE restart"
    echo "  Detener:         docker compose -f $COMPOSE_FILE down"
    echo "  Estado:          docker compose -f $COMPOSE_FILE ps"
    echo ""
    log_info "Sistema disponible en: http://192.168.100.59:3080"
}

# ---- Main ----
echo "============================================"
echo " Despliegue - Sistema de gestión de bienes humanitarios"
echo "============================================"
echo ""

check_docker
check_project
deploy
verify
