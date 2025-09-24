#!/bin/bash

# Script pour lancer le Dashboard Analytics V6 - Version Simplifiée (Corrigé)

echo "🚀 Lancement du Dashboard Analytics V6 - Version Simplifiée..."
echo "📍 Version avec séparation IP et GPS - Gestion robuste des données"
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "streamlit_env" ]; then
    echo "❌ Environnement virtuel 'streamlit_env' non trouvé"
    echo "💡 Créez-le avec : python3 -m venv streamlit_env"
    exit 1
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source streamlit_env/bin/activate

# Vérifier les dépendances
echo "📦 Vérification des dépendances..."
pip install streamlit pandas plotly requests

# Arrêter les dashboards existants
echo "🛑 Arrêt des dashboards existants..."
pkill -f "streamlit run" 2>/dev/null
sleep 2

# Lancer le dashboard V6 simplifié
echo "🌐 Lancement du dashboard V6 simplifié..."
echo "📍 URL: http://localhost:8501"
echo "📍 URL réseau: http://192.168.1.42:8501"
echo ""
echo "🔄 Le dashboard se rafraîchit automatiquement"
echo "⏹️  Pour arrêter: Ctrl+C"
echo ""

streamlit run dashboard_v6_simple.py --server.port 8501 