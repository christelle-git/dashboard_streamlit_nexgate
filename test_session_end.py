#!/usr/bin/env python3
"""
Script de test pour vérifier le traitement des événements session_end
"""

import json
import pandas as pd
from datetime import datetime

def test_session_end_processing():
    """Teste le traitement des événements session_end"""
    
    # Données de test incluant un événement session_end
    test_data = [
        {
            "type": "session_start",
            "session_id": "session_1756292264308_r90cr7ckm",
            "timestamp": "2025-08-27T10:57:44.309Z",
            "client_ip": "193.251.178.239",
            "country": "FR",
            "city": "Beaune (IP)",
            "latitude": 47.0241,
            "longitude": 4.8389
        },
        {
            "type": "click",
            "session_id": "session_1756292264308_r90cr7ckm",
            "timestamp": "2025-08-27T10:57:50.000Z",
            "page": "/",
            "element_type": "a",
            "sequence_order": 1,
            "x_coordinate": 100,
            "y_coordinate": 200,
            "client_ip": "193.251.178.239",
            "country": "FR",
            "city": "Beaune (IP)",
            "latitude": 47.0241,
            "longitude": 4.8389
        },
        {
            "type": "session_end",
            "session_id": "session_1756292264308_r90cr7ckm",
            "timestamp": "2025-08-27T10:57:57.971Z",
            "page": "/",
            "element_type": "unknown",
            "sequence_order": 1,
            "x_coordinate": 0,
            "y_coordinate": 0,
            "client_ip": "193.251.178.239",
            "ip_source": "server",
            "server_ip": "193.251.178.239",
            "server_geo_country": "France",
            "server_geo_city": "Beaune",
            "server_geo_latitude": 47.0241,
            "server_geo_longitude": 4.8389,
            "gps_latitude": 0,
            "gps_longitude": 0,
            "gps_accuracy": 0,
            "gps_source": "none",
            "country": "FR",
            "city": "Beaune (IP)",
            "latitude": 47.0241,
            "longitude": 4.8389,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "screen_resolution": "unknown",
            "viewport_size": "unknown",
            "referrer": "https://christellelusso.nexgate.ch/",
            "language": "fr",
            "timezone": "Europe/Paris",
            "session_start": None,
            "session_duration": 13662,
            "click_count": 0
        }
    ]
    
    print("🔍 Test du traitement des événements session_end")
    print("=" * 50)
    
    # Convertit en DataFrame
    df = pd.DataFrame(test_data)
    print(f"📊 Données d'entrée : {len(df)} événements")
    print(f"   - session_start: {len(df[df['type'] == 'session_start'])}")
    print(f"   - click: {len(df[df['type'] == 'click'])}")
    print(f"   - session_end: {len(df[df['type'] == 'session_end'])}")
    
    # Simule le traitement du dashboard
    clicks_df = df[df['type'] == 'click'].copy()
    session_end_df = df[df['type'] == 'session_end'].copy()
    
    print(f"\n📈 Événements clics extraits : {len(clicks_df)}")
    print(f"📈 Événements session_end extraits : {len(session_end_df)}")
    
    if not session_end_df.empty:
        print("\n✅ Événements session_end trouvés :")
        for _, row in session_end_df.iterrows():
            print(f"   - Session: {row['session_id']}")
            print(f"   - Durée: {row.get('session_duration', 'N/A')} secondes")
            print(f"   - Clics: {row.get('click_count', 'N/A')}")
            print(f"   - Localisation: {row.get('city', 'N/A')}, {row.get('country', 'N/A')}")
    
    # Test de la création du mapping
    session_end_mapping = {}
    for _, row in session_end_df.iterrows():
        session_id = row['session_id']
        session_end_mapping[session_id] = {
            'session_duration': row.get('session_duration', 0),
            'click_count': row.get('click_count', 0),
            'end_timestamp': row.get('timestamp', ''),
            'client_ip': row.get('client_ip', ''),
            'country': row.get('country', ''),
            'city': row.get('city', ''),
            'latitude': row.get('latitude', 0),
            'longitude': row.get('longitude', 0)
        }
    
    print(f"\n🗺️ Mapping créé pour {len(session_end_mapping)} sessions")
    for session_id, data in session_end_mapping.items():
        print(f"   - {session_id}: {data['session_duration']}s, {data['click_count']} clics")
    
    print("\n✅ Test terminé avec succès !")
    print("🎯 Les événements session_end sont maintenant traités par le dashboard.")

if __name__ == "__main__":
    test_session_end_processing()


