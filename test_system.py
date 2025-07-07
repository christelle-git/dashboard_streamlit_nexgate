#!/usr/bin/env python3
"""
Script de test pour vérifier le système d'analytics
"""

import sys
import os
import sqlite3
import requests
import json
from datetime import datetime

def test_configuration():
    """Teste la configuration du système"""
    print("🔧 Test de la configuration...")
    
    try:
        from config_setup import Config, validate_config
        print(f"✅ Configuration chargée")
        print(f"   Site web: {Config.WEBSITE_URL}")
        print(f"   API Port: {Config.API_PORT}")
        print(f"   Dashboard Port: {Config.DASHBOARD_PORT}")
        
        if validate_config():
            print("✅ Configuration valide")
        else:
            print("⚠️ Configuration avec avertissements")
        
        return True
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")
        return False

def test_database():
    """Teste la base de données"""
    print("\n🗄️ Test de la base de données...")
    
    try:
        from config_setup import Config
        from api_backend import init_database
        
        # Initialiser la base de données
        init_database()
        
        # Vérifier que les tables existent
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        tables = ['user_sessions', 'detailed_clicks', 'user_journeys', 'custom_events', 'file_downloads']
        
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                print(f"✅ Table {table} existe")
            else:
                print(f"❌ Table {table} manquante")
                return False
        
        conn.close()
        print("✅ Base de données fonctionnelle")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de base de données: {e}")
        return False

def test_api():
    """Teste l'API backend"""
    print("\n🚀 Test de l'API backend...")
    
    try:
        from config_setup import Config
        
        # Test de l'endpoint de santé
        health_url = f"http://localhost:{Config.API_PORT}/api/health"
        
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                print("✅ API accessible")
                return True
            else:
                print(f"⚠️ API répond avec le code {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("⚠️ API non accessible (probablement pas démarrée)")
            print("   Pour démarrer l'API: python api_backend.py")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de test API: {e}")
        return False

def test_dashboard():
    """Teste le dashboard Streamlit"""
    print("\n📊 Test du dashboard...")
    
    try:
        # Test d'import des modules du dashboard
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        import folium
        from streamlit_folium import folium_static
        
        print("✅ Modules du dashboard importés")
        
        # Test de la fonction de récupération des données
        from dashboard import get_analytics_data
        
        try:
            sessions_df, clicks_df, journeys_df = get_analytics_data()
            print("✅ Fonction de récupération des données fonctionnelle")
            return True
        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération des données: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Module manquant: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur de test dashboard: {e}")
        return False

def test_tracking_script():
    """Teste le script de tracking JavaScript"""
    print("\n📱 Test du script de tracking...")
    
    try:
        if os.path.exists('advanced_tracking.js'):
            with open('advanced_tracking.js', 'r') as f:
                content = f.read()
            
            # Vérifier les éléments essentiels
            required_elements = [
                'class AdvancedTracker',
                'generateSessionId',
                'setupEventListeners',
                'sendData'
            ]
            
            for element in required_elements:
                if element in content:
                    print(f"✅ {element} présent")
                else:
                    print(f"❌ {element} manquant")
                    return False
            
            print("✅ Script de tracking valide")
            return True
        else:
            print("❌ Fichier advanced_tracking.js manquant")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de test du script de tracking: {e}")
        return False

def generate_test_data():
    """Génère des données de test"""
    print("\n📝 Génération de données de test...")
    
    try:
        from config_setup import Config
        from api_backend import init_database
        import sqlite3
        from datetime import datetime, timedelta
        import random
        
        # Initialiser la base de données
        init_database()
        
        conn = sqlite3.connect(Config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Données de test pour les sessions
        test_sessions = [
            ('test_session_1', '192.168.1.1', 'Mozilla/5.0', '2024-01-15 10:00:00', 'Suisse', 'Genève', 46.2044, 6.1432),
            ('test_session_2', '192.168.1.2', 'Chrome/120.0', '2024-01-15 11:00:00', 'France', 'Paris', 48.8566, 2.3522),
            ('test_session_3', '192.168.1.3', 'Safari/17.0', '2024-01-15 12:00:00', 'Canada', 'Montréal', 45.5017, -73.5673),
        ]
        
        for session in test_sessions:
            cursor.execute('''
                INSERT OR REPLACE INTO user_sessions 
                (session_id, user_ip, user_agent, start_time, country, city, latitude, longitude, date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', session + (datetime.now().date(),))
        
        # Données de test pour les clics
        test_clicks = [
            ('test_session_1', 'btn-contact', 'button', '/', 1),
            ('test_session_1', 'link-about', 'a', '/about', 2),
            ('test_session_2', 'btn-download', 'button', '/downloads', 1),
            ('test_session_3', 'nav-home', 'nav', '/', 1),
        ]
        
        for click in test_clicks:
            cursor.execute('''
                INSERT INTO detailed_clicks 
                (session_id, element_id, element_type, page, sequence_order, timestamp, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', click + (datetime.now().isoformat(), datetime.now().date()))
        
        conn.commit()
        conn.close()
        
        print("✅ Données de test générées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération des données de test: {e}")
        return False

def main():
    """Test complet du système"""
    print("🧪 Test complet du système d'analytics")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Base de données", test_database),
        ("Script de tracking", test_tracking_script),
        ("Dashboard", test_dashboard),
        ("API", test_api),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur lors du test {test_name}: {e}")
            results.append((test_name, False))
    
    # Générer des données de test si tous les tests de base passent
    if all(result for _, result in results[:3]):  # Configuration, DB, Tracking
        generate_test_data()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 Résumé des tests:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests réussis")
    
    if passed == len(results):
        print("🎉 Tous les tests sont passés! Le système est prêt.")
        print("\n🚀 Pour démarrer:")
        print("   1. python api_backend.py")
        print("   2. streamlit run dashboard.py")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 