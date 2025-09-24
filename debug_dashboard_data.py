#!/usr/bin/env python3
"""
Script de debug pour vérifier les données du dashboard
"""

import json
import pandas as pd
from datetime import datetime
import sys
import os

# Ajouter le répertoire courant au path pour importer les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_dashboard_data():
    """Debug les données du dashboard"""
    
    print("🔍 Debug des données du dashboard")
    print("=" * 50)
    
    # Charger les données depuis le fichier JSON
    try:
        with open('analytics_data.json', 'r') as f:
            data = json.load(f)
        print(f"✅ Données chargées depuis analytics_data.json: {len(data)} événements")
    except Exception as e:
        print(f"❌ Erreur chargement analytics_data.json: {e}")
        return
    
    # Convertir en DataFrame
    df = pd.DataFrame(data)
    print(f"📊 DataFrame créé avec {len(df)} lignes et {len(df.columns)} colonnes")
    print(f"📋 Colonnes: {list(df.columns)}")
    
    # Analyser les types d'événements
    event_types = df['type'].value_counts()
    print(f"\n📈 Types d'événements:")
    for event_type, count in event_types.items():
        print(f"   - {event_type}: {count}")
    
    # Chercher spécifiquement la session de Beaune
    beaune_session = df[df['session_id'] == 'session_1756292264308_r90cr7ckm']
    print(f"\n🎯 Session de Beaune trouvée: {len(beaune_session)} événements")
    
    if not beaune_session.empty:
        print("📋 Détails de la session de Beaune:")
        for _, row in beaune_session.iterrows():
            print(f"   - Type: {row['type']}")
            print(f"   - Timestamp: {row.get('timestamp', 'N/A')}")
            print(f"   - IP: {row.get('client_ip', 'N/A')}")
            print(f"   - Ville: {row.get('city', 'N/A')}")
            print(f"   - Pays: {row.get('country', 'N/A')}")
            print(f"   - Session duration: {row.get('session_duration', 'N/A')}")
            print(f"   - Click count: {row.get('click_count', 'N/A')}")
            print("   ---")
    
    # Simuler le traitement du dashboard
    print("\n🔄 Simulation du traitement du dashboard...")
    
    # Séparer les clics et les sessions
    clicks_df = df[df['type'] == 'click'].copy()
    session_end_df = df[df['type'] == 'session_end'].copy()
    
    print(f"📈 Clics extraits: {len(clicks_df)}")
    print(f"📈 Session_end extraits: {len(session_end_df)}")
    
    # Créer le mapping session_end
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
    
    print(f"🗺️ Mapping session_end créé: {len(session_end_mapping)} sessions")
    
    # Simuler la création des sessions
    sessions_data = []
    
    # Ajouter les sessions basées sur les clics
    if not clicks_df.empty:
        # Compter les clics par session
        clicks_per_session = clicks_df.groupby('session_id').size().reset_index(name='click_count')
        
        # Adapter aux données classiques ET V6
        agg_columns = {
            'timestamp': ['min', 'max']  # début et fin de session
        }
        
        # Colonnes classiques
        if 'country' in clicks_df.columns:
            agg_columns['country'] = 'first'
        if 'city' in clicks_df.columns:
            agg_columns['city'] = 'first'
        if 'latitude' in clicks_df.columns:
            agg_columns['latitude'] = 'first'
        if 'longitude' in clicks_df.columns:
            agg_columns['longitude'] = 'first'
        if 'client_ip' in clicks_df.columns:
            agg_columns['client_ip'] = 'first'
        
        sessions_df = clicks_df.groupby('session_id').agg(agg_columns).reset_index()
        
        # Renommer les colonnes
        new_columns = ['session_id', 'session_start', 'session_end']
        for col in agg_columns.keys():
            if col != 'timestamp':
                new_columns.append(col)
        
        sessions_df.columns = new_columns
        sessions_data.append(sessions_df)
    
    # Ajouter les sessions basées sur session_end
    if session_end_mapping:
        for session_id, end_data in session_end_mapping.items():
            # Vérifier si cette session existe déjà
            session_exists = False
            for existing_df in sessions_data:
                if session_id in existing_df['session_id'].values:
                    session_exists = True
                    break
            
            if not session_exists:
                # Créer une nouvelle session basée sur session_end
                new_session = {
                    'session_id': session_id,
                    'session_start': None,
                    'session_end': end_data['end_timestamp'],
                    'client_ip': end_data['client_ip'],
                    'country': end_data['country'],
                    'city': end_data['city'],
                    'latitude': end_data['latitude'],
                    'longitude': end_data['longitude'],
                    'session_duration_from_end': end_data['session_duration'],
                    'click_count_from_end': end_data['click_count'],
                    'end_timestamp_from_end': end_data['end_timestamp']
                }
                
                new_df = pd.DataFrame([new_session])
                sessions_data.append(new_df)
                print(f"✅ Nouvelle session créée: {session_id}")
    
    # Combiner toutes les sessions
    if sessions_data:
        final_sessions_df = pd.concat(sessions_data, ignore_index=True)
        print(f"\n📊 Sessions finales: {len(final_sessions_df)} sessions")
        print(f"📋 Colonnes finales: {list(final_sessions_df.columns)}")
        
        # Chercher la session de Beaune dans les sessions finales
        beaune_final = final_sessions_df[final_sessions_df['session_id'] == 'session_1756292264308_r90cr7ckm']
        if not beaune_final.empty:
            print("\n🎯 Session de Beaune dans les sessions finales:")
            for col in beaune_final.columns:
                value = beaune_final.iloc[0][col]
                print(f"   - {col}: {value}")
            
            # Test de création des colonnes Date/Heure
            print("\n🕐 Test de création des colonnes Date/Heure:")
            
            if 'end_timestamp_from_end' in beaune_final.columns:
                timestamp_value = beaune_final.iloc[0]['end_timestamp_from_end']
                print(f"   - end_timestamp_from_end: {timestamp_value}")
                
                if pd.notna(timestamp_value) and timestamp_value:
                    try:
                        date_obj = pd.to_datetime(timestamp_value, utc=True).tz_convert('Europe/Paris').date()
                        time_obj = pd.to_datetime(timestamp_value, utc=True).tz_convert('Europe/Paris').time()
                        print(f"   ✅ Date créée: {date_obj}")
                        print(f"   ✅ Heure créée: {time_obj}")
                    except Exception as e:
                        print(f"   ❌ Erreur conversion: {e}")
                else:
                    print(f"   ❌ Timestamp vide ou null")
            else:
                print(f"   ❌ Colonne end_timestamp_from_end non trouvée")
        else:
            print("❌ Session de Beaune non trouvée dans les sessions finales")
    else:
        print("❌ Aucune session créée")

if __name__ == "__main__":
    debug_dashboard_data()


