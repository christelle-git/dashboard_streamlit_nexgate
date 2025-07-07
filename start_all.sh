#!/bin/bash

echo "🎯 Démarrage du système d'analytics avancé..."
echo

echo "🚀 Démarrage de l'API en arrière-plan..."
python api_backend.py &
API_PID=$!
echo "API démarrée avec PID: $API_PID"

echo "Attente de 3 secondes..."
sleep 3

echo "📊 Démarrage du dashboard Streamlit..."
streamlit run dashboard.py --server.port 8501

# Arrêt de l'API quand Streamlit se ferme
echo "Arrêt de l'API..."
kill $API_PID

echo
echo "✅ Système arrêté." 