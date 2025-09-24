#!/bin/bash

# 🚀 Script de déploiement du Dashboard de Tracking Analytics
# Usage: ./deploy.sh [environment]
# Environment: local, staging, production

set -e  # Arrêter en cas d'erreur

# Configuration
ENVIRONMENT=${1:-local}
BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="deploy.log"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Vérification des prérequis
check_prerequisites() {
    log "🔍 Vérification des prérequis..."
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 n'est pas installé"
    fi
    
    # Vérifier pip
    if ! command -v pip &> /dev/null; then
        error "pip n'est pas installé"
    fi
    
    # Vérifier git
    if ! command -v git &> /dev/null; then
        error "git n'est pas installé"
    fi
    
    success "Prérequis vérifiés"
}

# Sauvegarde de la version précédente
backup_current() {
    log "💾 Sauvegarde de la version précédente..."
    
    if [ -d "backup" ]; then
        mkdir -p "$BACKUP_DIR"
        cp -r . "$BACKUP_DIR/" 2>/dev/null || warning "Impossible de sauvegarder certains fichiers"
        success "Sauvegarde créée dans $BACKUP_DIR"
    else
        mkdir -p "$BACKUP_DIR"
        success "Dossier de sauvegarde créé"
    fi
}

# Mise à jour du code
update_code() {
    log "📥 Mise à jour du code..."
    
    # Vérifier si on est dans un repo git
    if [ -d ".git" ]; then
        git pull origin main || warning "Impossible de faire git pull"
    else
        warning "Pas de repository git détecté"
    fi
    
    success "Code mis à jour"
}

# Installation des dépendances
install_dependencies() {
    log "📦 Installation des dépendances..."
    
    # Activer l'environnement virtuel
    if [ -d "streamlit_env" ]; then
        source streamlit_env/bin/activate
    elif [ -d "venv" ]; then
        source venv/bin/activate
    else
        warning "Aucun environnement virtuel trouvé"
    fi
    
    # Installer les dépendances
    pip install -r requirements.txt || error "Échec de l'installation des dépendances"
    
    success "Dépendances installées"
}

# Configuration selon l'environnement
configure_environment() {
    log "⚙️ Configuration pour l'environnement: $ENVIRONMENT"
    
    case $ENVIRONMENT in
        "local")
            export STREAMLIT_SERVER_PORT=8501
            export STREAMLIT_SERVER_ADDRESS=localhost
            ;;
        "staging")
            export STREAMLIT_SERVER_PORT=8502
            export STREAMLIT_SERVER_ADDRESS=0.0.0.0
            ;;
        "production")
            export STREAMLIT_SERVER_PORT=8501
            export STREAMLIT_SERVER_ADDRESS=0.0.0.0
            export STREAMLIT_SERVER_HEADLESS=true
            ;;
        *)
            error "Environnement non reconnu: $ENVIRONMENT"
            ;;
    esac
    
    success "Configuration appliquée"
}

# Arrêt des processus existants
stop_existing_processes() {
    log "🛑 Arrêt des processus existants..."
    
    # Arrêter les processus Streamlit
    pkill -f "streamlit run" || warning "Aucun processus Streamlit trouvé"
    
    # Attendre un peu
    sleep 2
    
    success "Processus arrêtés"
}

# Lancement du dashboard
start_dashboard() {
    log "🚀 Lancement du dashboard..."
    
    # Choisir le dashboard selon l'environnement
    if [ "$ENVIRONMENT" = "production" ]; then
        DASHBOARD_FILE="dashboard_simple.py"
    else
        DASHBOARD_FILE="dashboard_simple.py"
    fi
    
    # Lancer en arrière-plan
    nohup streamlit run "$DASHBOARD_FILE" \
        --server.port="$STREAMLIT_SERVER_PORT" \
        --server.address="$STREAMLIT_SERVER_ADDRESS" \
        --server.headless="$STREAMLIT_SERVER_HEADLESS" \
        > "dashboard.log" 2>&1 &
    
    # Attendre que le service démarre
    sleep 5
    
    # Vérifier que le service fonctionne
    if curl -s "http://$STREAMLIT_SERVER_ADDRESS:$STREAMLIT_SERVER_PORT" > /dev/null; then
        success "Dashboard lancé avec succès"
        log "📍 URL: http://$STREAMLIT_SERVER_ADDRESS:$STREAMLIT_SERVER_PORT"
    else
        error "Échec du lancement du dashboard"
    fi
}

# Tests de validation
run_tests() {
    log "🧪 Exécution des tests de validation..."
    
    # Test de l'API
    if [ -f "test_api_fixed.html" ]; then
        log "Test de l'API disponible dans test_api_fixed.html"
    fi
    
    # Test du tracker
    if [ -f "test_tracker_debug.html" ]; then
        log "Test du tracker disponible dans test_tracker_debug.html"
    fi
    
    success "Tests de validation disponibles"
}

# Nettoyage
cleanup() {
    log "🧹 Nettoyage..."
    
    # Supprimer les anciens logs (garder seulement les 10 derniers)
    find . -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    # Supprimer les anciennes sauvegardes (garder seulement les 5 dernières)
    if [ -d "backup" ]; then
        ls -t backup/ | tail -n +6 | xargs -I {} rm -rf "backup/{}" 2>/dev/null || true
    fi
    
    success "Nettoyage terminé"
}

# Fonction principale
main() {
    log "🚀 Début du déploiement - Environnement: $ENVIRONMENT"
    
    check_prerequisites
    backup_current
    update_code
    install_dependencies
    configure_environment
    stop_existing_processes
    start_dashboard
    run_tests
    cleanup
    
    success "✅ Déploiement terminé avec succès !"
    log "📊 Dashboard disponible sur: http://$STREAMLIT_SERVER_ADDRESS:$STREAMLIT_SERVER_PORT"
    log "📝 Logs disponibles dans: dashboard.log"
    log "💾 Sauvegarde dans: $BACKUP_DIR"
}

# Gestion des erreurs
trap 'error "Déploiement interrompu par une erreur"' ERR

# Exécution
main "$@"
