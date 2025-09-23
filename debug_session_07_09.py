#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de debug pour la session du 07/09
"""

import json
import requests
from collections import defaultdict

def debug_session_07_09():
    print("=== DEBUG SESSION 07/09 ===\n")
    
    # Récupérer les données
    try:
        response = requests.get('https://christellelusso.nexgate.ch/analytics_data.json', timeout=10)
        data = response.json()
    except Exception as e:
        print(f"❌ Erreur : Impossible de récupérer les données: {e}")
        return
    
    print(f"📊 Total d'événements : {len(data)}\n")
    
    # Filtrer les événements du 07/09
    events_07_09 = [event for event in data if event.get('timestamp', '').startswith('2025-09-07')]
    
    print(f"📅 Événements du 07/09 : {len(events_07_09)}\n")
    
    # Grouper par session_id
    sessions = defaultdict(lambda: {
        'session_id': '',
        'events': [],
        'types': set(),
        'cities': set(),
        'countries': set(),
        'latitudes': set(),
        'longitudes': set(),
        'click_count': 0,
        'session_duration': 0
    })
    
    for event in events_07_09:
        session_id = event.get('session_id', 'unknown')
        sessions[session_id]['session_id'] = session_id
        sessions[session_id]['events'].append(event)
        sessions[session_id]['types'].add(event.get('type', 'unknown'))
        
        if 'city' in event:
            sessions[session_id]['cities'].add(event['city'])
        if 'country' in event:
            sessions[session_id]['countries'].add(event['country'])
        if 'latitude' in event and event['latitude']:
            sessions[session_id]['latitudes'].add(event['latitude'])
        if 'longitude' in event and event['longitude']:
            sessions[session_id]['longitudes'].add(event['longitude'])
        if 'click_count' in event and event['click_count'] is not None:
            sessions[session_id]['click_count'] = max(sessions[session_id]['click_count'], event['click_count'])
        if 'session_duration' in event and event['session_duration'] is not None:
            sessions[session_id]['session_duration'] = max(sessions[session_id]['session_duration'], event['session_duration'])
    
    print(f"🔍 Sessions trouvées : {len(sessions)}\n")
    
    for session_id, session in sessions.items():
        print(f"=== SESSION: {session_id} ===")
        print(f"Types d'événements : {', '.join(session['types'])}")
        print(f"Villes : {', '.join(session['cities'])}")
        print(f"Pays : {', '.join(session['countries'])}")
        print(f"Latitudes : {', '.join(map(str, session['latitudes']))}")
        print(f"Longitudes : {', '.join(map(str, session['longitudes']))}")
        print(f"Nombre de clics : {session['click_count']}")
        print(f"Durée : {session['session_duration']}ms")
        print(f"Nombre d'événements : {len(session['events'])}")
        
        # Vérifier si cette session sera visible sur la carte
        lat = max(session['latitudes']) if session['latitudes'] else 0
        lng = max(session['longitudes']) if session['longitudes'] else 0
        city = list(session['cities'])[0] if session['cities'] else 'Unknown'
        country = list(session['countries'])[0] if session['countries'] else 'Unknown'
        
        print(f"Coordonnées finales : [{lat}, {lng}]")
        print(f"Ville finale : {city}")
        print(f"Pays final : {country}")
        
        if lat != 0 and lng != 0:
            print("✅ Cette session DEVRAIT apparaître sur la carte")
        else:
            print("❌ Cette session n'apparaîtra PAS sur la carte (pas de coordonnées)")
        
        print()
    
    print("=== FIN DU DEBUG ===")

if __name__ == "__main__":
    debug_session_07_09()
