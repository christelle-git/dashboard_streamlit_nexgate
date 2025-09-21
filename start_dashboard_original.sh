#!/bin/bash

# Script pour lancer le Dashboard Analytics Original

echo "🚀 Lancement du Dashboard Analytics Original..."
echo "📊 Version classique avec données de test"
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

# Lancer le dashboard original
echo "🌐 Lancement du dashboard original..."
echo "📍 URL: http://localhost:8501"
echo "📍 URL réseau: http://192.168.1.42:8501"
echo ""
echo "🔄 Le dashboard se rafraîchit automatiquement toutes les 5 secondes"
echo "⏹️  Pour arrêter: Ctrl+C"
echo ""

streamlit run dashboard_simple.py --server.port 8501 