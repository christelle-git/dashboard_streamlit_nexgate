#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour comparer l'API V5 corrigée et l'API V6 originale
"""

import requests
import json
import time
from datetime import datetime

def test_api(api_url, test_name):
    """Teste une API et retourne les résultats"""
    print(f"\n🧪 Test de {test_name}")
    print("=" * 50)
    
    test_data = {
        "type": "click",
        "session_id": f"test_{test_name}_{int(time.time())}",
        "timestamp": datetime.now().isoformat(),
        "page": "/test_page",
        "element_type": "button",
        "sequence_order": 1,
        "x_coordinate": 100,
        "y_coordinate": 100,
        "client_ip": "8.8.8.8",  # IP Google pour test
        "ip_source": "test",
        "gps_latitude": 0,
        "gps_longitude": 0,
        "gps_accuracy": 0,
        "gps_source": "none",
        "geo_country": "Test",
        "geo_city": "Test City",
        "geo_source": "test"
    }
    
    try:
        print(f"📤 Envoi des données vers {api_url}")
        print(f"📊 Données envoyées: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(api_url, json=test_data, timeout=30)
        
        print(f"📥 Réponse reçue (status: {response.status_code})")
        
        if response.ok:
            result = response.json()
            print(f"✅ Succès: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Vérifier les données de géolocalisation
            if 'summary' in result:
                summary = result['summary']
                print(f"🌍 Résumé géolocalisation:")
                print(f"   - IP Client: {summary.get('ip_client', 'N/A')}")
                print(f"   - IP Source: {summary.get('ip_source', 'N/A')}")
                print(f"   - GPS disponible: {summary.get('gps_available', 'N/A')}")
                print(f"   - Géolocalisation client: {summary.get('geo_client', 'N/A')}")
                print(f"   - Géolocalisation serveur: {summary.get('geo_server', 'N/A')}")
                print(f"   - Cohérence: {summary.get('location_consistency', 'N/A')}")
                print(f"   - Compatible V5: {summary.get('v5_compatible', 'N/A')}")
            
            return True, result
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            try:
                error_result = response.json()
                print(f"📋 Détails erreur: {json.dumps(error_result, indent=2, ensure_ascii=False)}")
            except:
                print(f"📋 Texte erreur: {response.text}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False, None

def main():
    """Fonction principale de test"""
    print("🚀 Test de comparaison des APIs")
    print("=" * 60)
    
    # URLs des APIs à tester
    apis_to_test = [
        {
            "url": "http://localhost:8080/api_nexgate_fixed.php",
            "name": "API V5 Corrigée (locale)"
        },
        {
            "url": "http://localhost:8080/api.php", 
            "name": "API V5 Originale (locale)"
        }
    ]
    
    results = {}
    
    # Tester chaque API
    for api in apis_to_test:
        success, result = test_api(api["url"], api["name"])
        results[api["name"]] = {
            "success": success,
            "result": result
        }
    
    # Afficher le résumé des tests
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for api_name, result in results.items():
        status = "✅ SUCCÈS" if result["success"] else "❌ ÉCHEC"
        print(f"{api_name}: {status}")
        
        if result["success"] and result["result"]:
            # Vérifier la qualité de la géolocalisation
            if 'summary' in result["result"]:
                summary = result["result"]["summary"]
                geo_server = summary.get('geo_server', '')
                
                if 'Non spécifié' in geo_server:
                    print(f"   ⚠️  Géolocalisation serveur: {geo_server}")
                else:
                    print(f"   🌍 Géolocalisation serveur: {geo_server}")
    
    print("\n" + "=" * 60)
    print("💡 RECOMMANDATIONS")
    print("=" * 60)
    
    # Analyser les résultats
    v5_success = results.get("API V5 Corrigée (locale)", {}).get("success", False)
    v5_original_success = results.get("API V5 Originale (locale)", {}).get("success", False)
    
    if v5_success and v5_original_success:
        print("✅ Les deux APIs fonctionnent localement")
        print("🌐 Testez maintenant sur votre hébergeur avec l'API corrigée")
    elif v5_success:
        print("✅ L'API V5 corrigée fonctionne")
        print("❌ L'API V5 originale a des problèmes")
        print("🔧 Utilisez l'API corrigée sur votre hébergeur")
    elif v5_original_success:
        print("✅ L'API V5 originale fonctionne")
        print("❌ L'API V5 corrigée a des problèmes")
        print("🔧 Vérifiez la configuration locale")
    else:
        print("❌ Aucune API ne fonctionne localement")
        print("🔧 Vérifiez que le serveur local est démarré")

if __name__ == "__main__":
    main() 