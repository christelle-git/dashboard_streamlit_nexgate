#!/bin/bash

echo "🎯 Démarrage du système d'analytics avancé..."
echo

# Activation de l'environnement virtuel analytics
echo "🔧 Activation de l'environnement virtuel analytics..."
source analytics_env/bin/activate

echo "🚀 Démarrage de l'API en arrière-plan..."
API_PORT=5001 python api_backend.py &
API_PID=$!
echo "API démarrée avec PID: $API_PID"

echo "Attente de 3 secondes..."
sleep 3

# Activation de l'environnement virtuel streamlit
echo "🔧 Activation de l'environnement virtuel streamlit..."
source streamlit_env/bin/activate

echo "📊 Démarrage du dashboard Streamlit..."
streamlit run dashboard.py --server.port 8503

# Arrêt de l'API quand Streamlit se ferme
echo "Arrêt de l'API..."
kill $API_PID

echo
echo "✅ Système arrêté." 