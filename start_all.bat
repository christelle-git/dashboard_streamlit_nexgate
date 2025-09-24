@echo off
echo 🎯 Démarrage du système d'analytics avancé...
echo.

echo 🚀 Démarrage de l'API en arrière-plan...
start /B python api_backend.py

echo Attente de 3 secondes...
timeout /t 3 /nobreak > nul

echo 📊 Démarrage du dashboard Streamlit...
streamlit run dashboard.py --server.port 8501

echo.
echo ✅ Système arrêté.
pause 