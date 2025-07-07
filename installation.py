# installation.py - Script d'installation automatique
import subprocess
import sys
import os
import shutil

def install_dependencies():
    """Installe toutes les dépendances nécessaires"""
    print("📦 Installation des dépendances...")
    
    try:
        # Vérifier si pip est disponible
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ pip n'est pas disponible. Veuillez installer pip d'abord.")
        return False
    
    dependencies = [
        "streamlit==1.28.0",
        "pandas==2.1.0", 
        "plotly==5.15.0",
        "folium==0.14.0",
        "streamlit-folium==0.13.0",
        "flask==2.3.3",
        "flask-cors==4.0.0",
        "requests==2.31.0",
        "python-dotenv==1.0.0"
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation de {dep}: {e}")
            return False
    
    print("✅ Toutes les dépendances sont installées!")
    return True

def create_project_structure():
    """Crée la structure de fichiers du projet"""
    print("📁 Création de la structure du projet...")
    
    # Créer les dossiers nécessaires
    folders = ["templates", "static", "data", "logs"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    # Créer le fichier .env pour les variables d'environnement
    if not os.path.exists(".env"):
        env_content = """# Configuration du système d'analytics
WEBSITE_URL=https://christellelusso.nexgate.ch
API_PORT=5000
SECRET_KEY=votre-cle-secrete-unique-changez-moi
DEBUG=True

# Configuration de la base de données
DATABASE_PATH=advanced_analytics.db

# Configuration du tracking
TRACKING_ENDPOINT=/api/track
GEOLOCATION_ENABLED=True
SESSION_TIMEOUT=1800

# Configuration du dashboard
DASHBOARD_PORT=8501
DASHBOARD_TITLE="Analytics Avancé - Christelle Lusso"
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Fichier .env créé!")
    else:
        print("ℹ️ Fichier .env existe déjà")
    
    print("✅ Structure du projet créée!")

def init_database():
    """Initialise la base de données"""
    print("🗄️ Initialisation de la base de données...")
    
    import sqlite3
    from datetime import datetime
    
    conn = sqlite3.connect('advanced_analytics.db')
    cursor = conn.cursor()
    
    # Créer toutes les tables
    tables = [
        '''CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            user_ip TEXT,
            user_agent TEXT,
            start_time DATETIME,
            end_time DATETIME,
            duration_seconds INTEGER,
            country TEXT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            timezone TEXT,
            language TEXT,
            screen_resolution TEXT,
            referrer TEXT,
            total_clicks INTEGER DEFAULT 0,
            pages_visited INTEGER DEFAULT 0,
            date DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''',
        
        '''CREATE TABLE IF NOT EXISTS detailed_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            element_id TEXT,
            element_type TEXT,
            element_class TEXT,
            element_text TEXT,
            page TEXT,
            file_clicked TEXT,
            file_extension TEXT,
            timestamp DATETIME,
            sequence_order INTEGER,
            x_coordinate INTEGER,
            y_coordinate INTEGER,
            date DATE
        )''',
        
        '''CREATE TABLE IF NOT EXISTS user_journeys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            journey_path TEXT,
            journey_data TEXT,
            total_clicks INTEGER,
            session_duration INTEGER,
            date DATE
        )''',
        
        '''CREATE TABLE IF NOT EXISTS custom_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            event_name TEXT,
            event_data TEXT,
            page TEXT,
            timestamp DATETIME,
            date DATE
        )''',
        
        '''CREATE TABLE IF NOT EXISTS file_downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            file_url TEXT,
            file_name TEXT,
            file_extension TEXT,
            element_text TEXT,
            page TEXT,
            timestamp DATETIME,
            sequence_order INTEGER,
            date DATE
        )'''
    ]
    
    for table in tables:
        cursor.execute(table)
    
    conn.commit()
    conn.close()
    
    print("✅ Base de données initialisée!")

def create_launch_scripts():
    """Crée les scripts de lancement"""
    print("🚀 Création des scripts de lancement...")
    
    # Script pour lancer l'API
    api_script = """#!/bin/bash
echo "🚀 Démarrage de l'API Analytics..."
python api_backend.py
"""
    
    # Script pour lancer le dashboard
    dashboard_script = """#!/bin/bash
echo "📊 Démarrage du Dashboard Streamlit..."
streamlit run dashboard.py --server.port 8501
"""
    
    # Script pour lancer les deux
    full_script = """#!/bin/bash
echo "🎯 Démarrage complet du système d'analytics..."
echo "Démarrage de l'API en arrière-plan..."
python api_backend.py &
API_PID=$!
echo "API démarrée avec PID: $API_PID"

echo "Attente de 3 secondes..."
sleep 3

echo "Démarrage du dashboard Streamlit..."
streamlit run dashboard.py --server.port 8501

# Arrêt de l'API quand Streamlit se ferme
kill $API_PID
"""
    
    with open("start_api.sh", "w") as f:
        f.write(api_script)
    
    with open("start_dashboard.sh", "w") as f:
        f.write(dashboard_script)
    
    with open("start_all.sh", "w") as f:
        f.write(full_script)
    
    # Rendre les scripts exécutables sur Unix
    try:
        os.chmod("start_api.sh", 0o755)
        os.chmod("start_dashboard.sh", 0o755)
        os.chmod("start_all.sh", 0o755)
    except:
        pass  # Windows n'a pas besoin de chmod
    
    print("✅ Scripts de lancement créés!")

def main():
    """Installation complète du système"""
    print("🎯 Installation du système d'analytics avancé")
    print("=" * 50)
    
    # Installation des dépendances
    if not install_dependencies():
        print("❌ Échec de l'installation des dépendances")
        return
    
    # Création de la structure
    create_project_structure()
    
    # Initialisation de la base de données
    init_database()
    
    # Création des scripts de lancement
    create_launch_scripts()
    
    print("\n" + "=" * 50)
    print("✅ Installation terminée avec succès!")
    print("\n🚀 Pour démarrer le système:")
    print("1. API Backend: python api_backend.py")
    print("2. Dashboard: streamlit run dashboard.py")
    print("3. Ou utilisez: ./start_all.sh (Linux/Mac)")
    print("\n📖 Consultez le README.md pour plus d'informations")
    
    try:
        #install_dependencies()
        create_project_structure()
        init_database()
        create_launch_scripts()
        
        print("\n🎉 Installation terminée avec succès!")
        print("\n📝 Prochaines étapes:")
        print("1. Éditez le fichier config.py et changez WEBSITE_URL")
        print("2. Ajoutez le code JavaScript à votre site web")
        print("3. Lancez l'API: python api_backend.py")
        print("4. Lancez le dashboard: streamlit run dashboard.py")
        print("5. Ou lancez tout: ./start_all.sh")
        
        print("\n🔧 Configuration requise:")
        print("- Modifiez WEBSITE_URL dans config.py")
        print("- Ajoutez vos domaines dans ALLOWED_ORIGINS")
        print("- Copiez le code JavaScript dans votre site")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()