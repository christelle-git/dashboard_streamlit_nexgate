# config_setup.py - Configuration du système d'analytics
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    """Configuration centralisée du système d'analytics"""
    
    # URL de votre site web
    WEBSITE_URL = os.getenv("WEBSITE_URL", "https://christellelusso.nexgate.ch")
    
    # Domaines autorisés pour CORS
    ALLOWED_ORIGINS = [
        WEBSITE_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501",
        "http://127.0.0.1:8501"
    ]
    
    # Configuration de la base de données
    DATABASE_PATH = os.getenv("DATABASE_PATH", "advanced_analytics.db")
    
    # Port pour l'API
    API_PORT = int(os.getenv("API_PORT", 5000))
    
    # Clé secrète pour sécuriser l'API
    SECRET_KEY = os.getenv("SECRET_KEY", "votre-cle-secrete-unique-changez-moi")
    
    # Configuration du dashboard
    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8501))
    DASHBOARD_TITLE = os.getenv("DASHBOARD_TITLE", "Analytics Avancé - Christelle Lusso")
    
    # Configuration du tracking
    TRACKING_ENDPOINT = os.getenv("TRACKING_ENDPOINT", "/api/track")
    GEOLOCATION_ENABLED = os.getenv("GEOLOCATION_ENABLED", "True").lower() == "true"
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 1800))
    
    # Configuration géolocalisation (optionnel)
    IPAPI_KEY = os.getenv("IPAPI_KEY", "")
    
    # Mode debug
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

def validate_config():
    """Valide la configuration et affiche des avertissements si nécessaire"""
    warnings = []
    
    if Config.SECRET_KEY == "votre-cle-secrete-unique-changez-moi":
        warnings.append("⚠️ Changez la clé secrète dans le fichier .env")
    
    if not Config.WEBSITE_URL.startswith(("http://", "https://")):
        warnings.append("⚠️ L'URL du site web doit commencer par http:// ou https://")
    
    if warnings:
        print("Configuration - Avertissements:")
        for warning in warnings:
            print(f"  {warning}")
        print()
    
    return len(warnings) == 0

if __name__ == "__main__":
    print("🔧 Configuration du système d'analytics")
    print("=" * 40)
    print(f"Site web: {Config.WEBSITE_URL}")
    print(f"API Port: {Config.API_PORT}")
    print(f"Dashboard Port: {Config.DASHBOARD_PORT}")
    print(f"Base de données: {Config.DATABASE_PATH}")
    print(f"Géolocalisation: {'Activée' if Config.GEOLOCATION_ENABLED else 'Désactivée'}")
    print(f"Mode Debug: {'Activé' if Config.DEBUG else 'Désactivé'}")
    print()
    
    if validate_config():
        print("✅ Configuration valide!")
    else:
        print("⚠️ Veuillez corriger les avertissements ci-dessus")
