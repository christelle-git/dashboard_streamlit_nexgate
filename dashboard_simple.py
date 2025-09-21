import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import requests
import time
import os
import re
from collections import Counter

st.set_page_config(
    page_title="Dashboard Analytics Simplifié",
    page_icon="📊",
    layout="wide"
)

# Auto-refresh toutes les 5 secondes
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

current_time = time.time()
if current_time - st.session_state.last_refresh > 5:
    st.session_state.last_refresh = current_time
    st.rerun()

@st.cache_data(ttl=5, show_spinner=False)
def get_analytics_data():
    """Récupère les données depuis le serveur web"""
    # Essaie d'abord le serveur web avec les vraies données
    try:
        response = requests.get('https://christellelusso.nexgate.ch/analytics_data.json', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data, "✅ Données récupérées depuis le serveur web (nexgate.ch)"
        else:
            st.error(f"Erreur HTTP: {response.status_code}")
            return [], "❌ Erreur lors de la récupération des données"
    except Exception as e:
        # En cas d'erreur, essaie l'API Flask locale
        try:
            st.warning(f"⚠️ Serveur web inaccessible ({e}). Tentative avec l'API locale...")
            response = requests.get('http://localhost:5001/api/health', timeout=5)
            if response.status_code == 200:
                return [], "🔄 API locale disponible - Utilisez le dashboard complet (./start_all.sh)"
            else:
                return [], "❌ Serveur web et API locale indisponibles"
        except:
            return [], "❌ Serveur web indisponible (bloqué par proxy/VPN). Utilisez le dashboard à la maison ou désactivez le proxy."

def get_test_data():
    """Retourne des données de test pour le développement"""
    return [
        {
            "type": "click",
            "session_id": "test_session_1",
            "page": "drawing/mystic.jpg",
            "timestamp": "2025-07-29T15:30:00Z",
            "country": "France",
            "city": "Paris",
            "client_ip": "192.168.1.100"
        },
        {
            "type": "click",
            "session_id": "test_session_1",
            "page": "pdf/thesis.pdf",
            "timestamp": "2025-07-29T15:32:00Z",
            "country": "France",
            "city": "Paris",
            "client_ip": "192.168.1.100"
        },
        {
            "type": "click",
            "session_id": "test_session_2",
            "page": "drawing/crazy_love_cp_clean.jpg",
            "timestamp": "2025-07-29T16:00:00Z",
            "country": "Suisse",
            "city": "Genève",
            "client_ip": "192.168.1.101"
        },
        {
            "type": "click",
            "session_id": "test_session_3",
            "page": "pdf/abstract_lusso.pdf",
            "timestamp": "2025-07-29T16:15:00Z",
            "country": "Canada",
            "city": "Montréal",
            "client_ip": "192.168.1.102"
        }
    ]

@st.cache_data(ttl=300, show_spinner=False)  # Cache 5 minutes pour la liste des fichiers
def get_available_files():
    """Récupère la liste des fichiers disponibles sur le site"""
    try:
        # Récupère la page principale pour extraire les liens
        response = requests.get('https://christellelusso.nexgate.ch/', timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # Extrait tous les liens vers des fichiers
            file_patterns = [
                r'href=["\']([^"\']*\.(?:jpg|jpeg|png|gif|pdf|doc|docx|txt))["\']',
                r'src=["\']([^"\']*\.(?:jpg|jpeg|png|gif|pdf|doc|docx|txt))["\']'
            ]
            
            found_files = set()
            for pattern in file_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    # Nettoie le chemin et extrait le nom de fichier
                    if match.startswith('/'):
                        match = match[1:]
                    if match.startswith('http'):
                        # URL complète, extrait le nom de fichier
                        filename = os.path.basename(match)
                    else:
                        # Chemin relatif
                        filename = os.path.basename(match)
                    
                    if filename and '.' in filename:
                        found_files.add(filename)
            
            # Ajoute aussi les fichiers connus des dossiers drawing et pdf
            known_files = [
                # Images du dossier drawing
                "BD_criterium.jpg", "books_stack_cp.jpg", "crazy_love_cp_clean.jpg", 
                "dense_cp.JPG", "finger_noze_2.jpg", "flying_to_the_moon.png", 
                "funny_games.png", "joke_maths_cp.jpg", "lenny_cp.jpg", 
                "massue_tot_cp.jpg", "mystic.jpg", "navier_stokes_green_tv_cp.jpg", 
                "paperPhys_cp.jpg", "pastel.png", "pop_art.png", "run_run.JPG", 
                "school_cp.jpg", "sparkling.jpg", "sport_training.jpg", "wake_up.jpg",
                # PDFs du dossier pdf
                "abstract_lusso.pdf", "canum.pdf", "controle1.pdf", "controle2.pdf", 
                "controle3.pdf", "devoir.pdf", "documentation_pres.pdf", "efrei_2025.pdf", 
                "gdt.pdf", "indus_pres.pdf", "poster_ihp.pdf", "poster_roscoff.pdf", 
                "presentation_christelle.pdf", "presentation_ljll.pdf", 
                "S4SM_algebre_TD1_2012.pdf", "S4SM-algebre-TD2-2012.pdf", 
                "S4SM-algebre-TD3.pdf", "S4SM-algebre-TD4-2012.pdf", "S4SM-exam-2012.pdf", 
                "td1_algebre.pdf", "td1.pdf", "td2_algebre.pdf", "td2.pdf", 
                "td3_algebre_copie.pdf", "td3_algebre.pdf", "td3.pdf", "td4_algebre.pdf", 
                "td4.pdf", "td5_algebre.pdf", "td6_algebre.pdf", "td7_algebre.pdf", 
                "thesis.pdf"
            ]
            
            # Combine les fichiers trouvés et connus
            all_files = list(found_files.union(set(known_files)))
            all_files.sort()
            
            return all_files
            
    except Exception as e:
        st.error(f"Erreur lors de la récupération des fichiers: {e}")
        # Fallback vers la liste de base
        return [
            "BD_criterium.jpg", "books_stack_cp.jpg", "crazy_love_cp_clean.jpg", 
            "dense_cp.JPG", "finger_noze_2.jpg", "flying_to_the_moon.png", 
            "funny_games.png", "joke_maths_cp.jpg", "lenny_cp.jpg", 
            "massue_tot_cp.jpg", "mystic.jpg", "navier_stokes_green_tv_cp.jpg", 
            "paperPhys_cp.jpg", "pastel.png", "pop_art.png", "run_run.JPG", 
            "school_cp.jpg", "sparkling.jpg", "sport_training.jpg", "wake_up.jpg",
            "abstract_lusso.pdf", "canum.pdf", "controle1.pdf", "controle2.pdf", 
            "controle3.pdf", "devoir.pdf", "documentation_pres.pdf", "efrei_2025.pdf", 
            "gdt.pdf", "indus_pres.pdf", "poster_ihp.pdf", "poster_roscoff.pdf", 
            "presentation_christelle.pdf", "presentation_ljll.pdf", 
            "S4SM_algebre_TD1_2012.pdf", "S4SM-algebre-TD2-2012.pdf", 
            "S4SM-algebre-TD3.pdf", "S4SM-algebre-TD4-2012.pdf", "S4SM-exam-2012.pdf", 
            "td1_algebre.pdf", "td1.pdf", "td2_algebre.pdf", "td2.pdf", 
            "td3_algebre_copie.pdf", "td3_algebre.pdf", "td3.pdf", "td4_algebre.pdf", 
            "td4.pdf", "td5_algebre.pdf", "td6_algebre.pdf", "td7_algebre.pdf", 
            "thesis.pdf"
        ]

def process_data(data):
    """Traite les données JSON en DataFrames"""
    if not data:
        return pd.DataFrame(), pd.DataFrame()
    
    # Convertit en DataFrame
    df = pd.DataFrame(data)
    
    # Séparer les clics et les sessions
    clicks_df = df[df['type'] == 'click'].copy() if 'click' in df['type'].values else pd.DataFrame()
    
    # Traiter les événements session_end pour enrichir les données
    session_end_df = df[df['type'] == 'session_end'].copy() if 'session_end' in df['type'].values else pd.DataFrame()
    
    # Si on a des événements session_end, on peut les utiliser pour enrichir les sessions
    if not session_end_df.empty:
        # Créer un mapping session_id -> données de fin de session
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
    
    # Traitement des données
    if not clicks_df.empty:
        # Compter les clics par session
        clicks_per_session = clicks_df.groupby('session_id').size().reset_index(name='click_count')
        
        # Adapter aux données classiques ET V6 de l'hébergeur
        agg_columns = {
            'timestamp': ['min', 'max']  # début et fin de session
        }
        
        # PRIORITÉ 1: Colonnes classiques (qui existent dans vos données)
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
            
        # PRIORITÉ 2: Colonnes V6 (si les classiques n'existent pas)
        if 'country' not in agg_columns and 'geo_country' in clicks_df.columns:
            agg_columns['geo_country'] = 'first'
        if 'city' not in agg_columns and 'geo_city' in clicks_df.columns:
            agg_columns['geo_city'] = 'first'
        if 'latitude' not in agg_columns and 'gps_latitude' in clicks_df.columns:
            agg_columns['gps_latitude'] = 'first'
        if 'longitude' not in agg_columns and 'gps_longitude' in clicks_df.columns:
            agg_columns['gps_longitude'] = 'first'
        
        sessions_df = clicks_df.groupby('session_id').agg(agg_columns).reset_index()
        
        # Renommer les colonnes
        new_columns = ['session_id', 'session_start', 'session_end']
        for col in agg_columns.keys():
            if col != 'timestamp':
                new_columns.append(col)
        
        sessions_df.columns = new_columns
        
        # Créer des colonnes compatibles avec l'ancien format
        # Si on a déjà les colonnes classiques, les utiliser directement
        if 'country' not in sessions_df.columns and 'geo_country' in sessions_df.columns:
            sessions_df['country'] = sessions_df['geo_country']
        if 'city' not in sessions_df.columns and 'geo_city' in sessions_df.columns:
            sessions_df['city'] = sessions_df['geo_city']
        if 'latitude' not in sessions_df.columns and 'gps_latitude' in sessions_df.columns:
            sessions_df['latitude'] = sessions_df['gps_latitude']
        if 'longitude' not in sessions_df.columns and 'gps_longitude' in sessions_df.columns:
            sessions_df['longitude'] = sessions_df['gps_longitude']
        
        # Enrichir avec les données session_end si disponibles
        if 'session_end_mapping' in locals() and session_end_mapping:
            # Ajouter les colonnes de session_end
            sessions_df['session_duration_from_end'] = sessions_df['session_id'].map(
                lambda x: session_end_mapping.get(x, {}).get('session_duration', 0)
            )
            sessions_df['click_count_from_end'] = sessions_df['session_id'].map(
                lambda x: session_end_mapping.get(x, {}).get('click_count', 0)
            )
            sessions_df['end_timestamp_from_end'] = sessions_df['session_id'].map(
                lambda x: session_end_mapping.get(x, {}).get('end_timestamp', '')
            )
            sessions_df['client_ip_from_end'] = sessions_df['session_id'].map(
                lambda x: session_end_mapping.get(x, {}).get('client_ip', '')
            )
            
            # Utiliser les données de session_end pour les sessions qui n'ont pas de clics
            sessions_created = 0
            for session_id, end_data in session_end_mapping.items():
                if session_id not in sessions_df['session_id'].values:
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
                    sessions_df = pd.concat([sessions_df, pd.DataFrame([new_session])], ignore_index=True)
                    sessions_created += 1
        
        # Calculer la durée de session (en secondes)
        sessions_df['session_start'] = pd.to_datetime(sessions_df['session_start'])
        sessions_df['session_end'] = pd.to_datetime(sessions_df['session_end'])
        sessions_df['duration_seconds'] = (sessions_df['session_end'] - sessions_df['session_start']).dt.total_seconds()
        
        # Utiliser la durée depuis session_end si disponible
        if 'session_duration_from_end' in sessions_df.columns:
            sessions_df['duration_seconds'] = sessions_df['session_duration_from_end'].fillna(sessions_df['duration_seconds'])
        
        # Utiliser client_ip depuis session_end si client_ip n'existe pas
        if 'client_ip_from_end' in sessions_df.columns:
            if 'client_ip' not in sessions_df.columns:
                sessions_df['client_ip'] = sessions_df['client_ip_from_end']
            else:
                sessions_df['client_ip'] = sessions_df['client_ip'].fillna(sessions_df['client_ip_from_end'])
        
        sessions_df = sessions_df.merge(clicks_per_session, on='session_id', how='left')
    else:
        sessions_df = pd.DataFrame()
    
    return sessions_df, clicks_df

def extract_filename_from_page(page_path):
    """Extrait le nom du fichier depuis le chemin de la page"""
    if not page_path or page_path == '/':
        return 'Page principale'
    
    # Enlève le '/' du début
    if page_path.startswith('/'):
        page_path = page_path[1:]
    
    # Extensions de fichiers à détecter (majuscules et minuscules)
    file_extensions = [
        '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.html', '.htm',
        '.JPG', '.JPEG', '.PNG', '.GIF', '.PDF', '.DOC', '.DOCX', '.TXT', '.HTML', '.HTM'
    ]
    
    # Vérifie si c'est un fichier avec extension
    for ext in file_extensions:
        if page_path.endswith(ext):
            # Extrait juste le nom du fichier sans le chemin
            filename = os.path.basename(page_path)
            return filename
    
    # Si c'est un chemin vers un dossier (comme pdf/thesis.pdf)
    if '/' in page_path:
        filename = os.path.basename(page_path)
        # Vérifie si le nom extrait a une extension
        for ext in file_extensions:
            if filename.endswith(ext):
                return filename
        return page_path
    
    # Si c'est une URL complète, extrait le nom de fichier
    if page_path.startswith('http'):
        try:
            from urllib.parse import urlparse
            parsed = urlparse(page_path)
            filename = os.path.basename(parsed.path)
            if filename:
                return filename
        except:
            pass
    
    # Sinon c'est probablement un lien interne
    return f'Lien: {page_path}'

def analyze_user_journey(clicks_df, sessions_df):
    """Analyse les parcours utilisateur"""
    # Groupe par session et crée les parcours
    journey_data = []
    common_paths = []
    
    # Traite d'abord les sessions avec des clics
    for session_id in clicks_df['session_id'].unique():
        session_clicks = clicks_df[clicks_df['session_id'] == session_id]
        
        # Trie par sequence_order si la colonne existe, sinon par timestamp
        if 'sequence_order' in session_clicks.columns:
            session_clicks = session_clicks.sort_values('sequence_order')
        elif 'timestamp' in session_clicks.columns:
            session_clicks = session_clicks.sort_values('timestamp')
        
        if len(session_clicks) >= 1:  # Inclut les sessions avec 1 seul clic
            # Crée le chemin du parcours
            path = []
            files_clicked = []
            
            for _, click in session_clicks.iterrows():
                if click['page']:
                    path.append(click['page'])
                # Vérifie si la colonne file_clicked existe
                if 'file_clicked' in click and click['file_clicked']:
                    files_clicked.append(click['file_clicked'])
                # Sinon, essaie d'extraire le fichier depuis la page
                elif click['page'] and any(ext in click['page'].lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt']):
                    filename = extract_filename_from_page(click['page'])
                    if filename != 'Page principale':
                        files_clicked.append(filename)
            
            if path:
                journey_str = ' → '.join(path)
                files_str = ', '.join(files_clicked) if files_clicked else 'Aucun fichier'
                
                # Récupère la ville depuis sessions_df
                city = 'Non spécifié'
                if not sessions_df.empty and 'session_id' in sessions_df.columns and 'city' in sessions_df.columns:
                    session_info = sessions_df[sessions_df['session_id'] == session_id]
                    if not session_info.empty:
                        city = session_info.iloc[0]['city'] if pd.notna(session_info.iloc[0]['city']) else 'Non spécifié'
                
                journey_data.append({
                    'session_id': session_id,
                    'ville': city,
                    'parcours': journey_str,
                    'fichiers_cliques': files_str,
                    'nombre_clics': len(session_clicks),
                    'duree_estimee': f"{len(session_clicks) * 30}s"  # Estimation basique
                })
                
                common_paths.append(journey_str)
    
    # Ajoute les sessions sans clics
    if not sessions_df.empty:
        sessions_with_clicks = set(clicks_df['session_id'].unique())
        sessions_without_clicks = sessions_df[~sessions_df['session_id'].isin(sessions_with_clicks)]
        
        for _, session in sessions_without_clicks.iterrows():
            city = session.get('city', 'Non spécifié') if pd.notna(session.get('city')) else 'Non spécifié'
            
            journey_data.append({
                'session_id': session['session_id'],
                'ville': city,
                'parcours': 'Aucun parcours (session sans clics)',
                'fichiers_cliques': 'Aucun fichier',
                'nombre_clics': 0,
                'duree_estimee': '0s'
            })
    
    journey_df = pd.DataFrame(journey_data)
    
    # Trouve les parcours les plus communs
    if common_paths:
        path_counts = Counter(common_paths)
        top_paths = path_counts.most_common(10)
    else:
        top_paths = []
    
    return journey_df, top_paths

def main():
    st.set_page_config(
        page_title="Tracking nexgate Christelle",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Tracking nexgate Christelle")
    st.markdown("---")
    
    # Récupération des données
    data, status = get_analytics_data()
    st.info(status)
    
    # Traitement des données
    sessions_df, clicks_df = process_data(data)
    
    # Métriques principales
    col1, col2 = st.columns(2)
    
    with col1:
        total_clicks = len(clicks_df) if not clicks_df.empty else 0
        st.metric("Clics Totaux", total_clicks)
    
    with col2:
        total_sessions = len(sessions_df) if not sessions_df.empty else 0
        st.metric("Sessions Totales", total_sessions)
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["🌍 Géolocalisation", "📊 Tracking par fichier", "🛤️ Parcours Utilisateurs"])
    
    with tab1:
        st.subheader("🌍 Géolocalisation des Sessions")
        
        if not sessions_df.empty:
            # Prépare les données pour l'affichage
            location_data = sessions_df.copy()
            
            # Ajoute des colonnes manquantes si nécessaire
            if 'country' not in location_data.columns:
                location_data['country'] = 'Non spécifié'
            if 'city' not in location_data.columns:
                location_data['city'] = 'Non spécifié'
            if 'latitude' not in location_data.columns:
                location_data['latitude'] = 0
            if 'longitude' not in location_data.columns:
                location_data['longitude'] = 0
            
            # Créer des colonnes Date et Heure en UTC+2 (Paris)
            
            # Essayer session_start d'abord pour les sessions qui ont un session_start
            if 'session_start' in location_data.columns:
                try:
                    # Filtrer les sessions qui ont un session_start valide
                    mask = location_data['session_start'].notna()
                    if mask.any():
                        location_data.loc[mask, 'date'] = pd.to_datetime(location_data.loc[mask, 'session_start'], utc=True).dt.tz_convert('Europe/Paris').dt.date
                        location_data.loc[mask, 'time'] = pd.to_datetime(location_data.loc[mask, 'session_start'], utc=True).dt.tz_convert('Europe/Paris').dt.time
                except Exception as e:
                    st.write(f"❌ Erreur avec session_start: {e}")
            
            # Essayer end_timestamp_from_end pour les sessions qui n'ont pas encore de date/heure
            if 'end_timestamp_from_end' in location_data.columns:
                try:
                    # Filtrer les sessions qui n'ont pas encore de date/heure et qui ont un end_timestamp_from_end
                    mask = (location_data['date'].isna() | (location_data['date'] == 'Non spécifié')) & location_data['end_timestamp_from_end'].notna()
                    if mask.any():
                        location_data.loc[mask, 'date'] = pd.to_datetime(location_data.loc[mask, 'end_timestamp_from_end'], utc=True).dt.tz_convert('Europe/Paris').dt.date
                        location_data.loc[mask, 'time'] = pd.to_datetime(location_data.loc[mask, 'end_timestamp_from_end'], utc=True).dt.tz_convert('Europe/Paris').dt.time
                except Exception as e:
                    st.write(f"❌ Erreur avec end_timestamp_from_end: {e}")
            
            # Essayer timestamp pour les sessions qui n'ont pas encore de date/heure
            if 'timestamp' in location_data.columns:
                try:
                    # Filtrer les sessions qui n'ont pas encore de date/heure et qui ont un timestamp
                    mask = (location_data['date'].isna() | (location_data['date'] == 'Non spécifié')) & location_data['timestamp'].notna()
                    if mask.any():
                        location_data.loc[mask, 'date'] = pd.to_datetime(location_data.loc[mask, 'timestamp'], utc=True).dt.tz_convert('Europe/Paris').dt.date
                        location_data.loc[mask, 'time'] = pd.to_datetime(location_data.loc[mask, 'timestamp'], utc=True).dt.tz_convert('Europe/Paris').dt.time
                except Exception as e:
                    st.write(f"❌ Erreur avec timestamp: {e}")
            
            # Remplir les valeurs manquantes par défaut
            if 'date' not in location_data.columns:
                location_data['date'] = 'Non spécifié'
            else:
                location_data['date'] = location_data['date'].fillna('Non spécifié')
            
            if 'time' not in location_data.columns:
                location_data['time'] = 'Non spécifié'
            else:
                location_data['time'] = location_data['time'].fillna('Non spécifié')
            
            # Affiche les sessions avec géolocalisation, Date et Heure
            display_columns = ['date', 'time', 'session_id', 'country', 'city', 'client_ip']
            available_columns = [col for col in display_columns if col in location_data.columns]
            location_display = location_data[available_columns].copy()
            
            # Renomme les colonnes pour l'affichage
            column_mapping = {
                'date': 'Date',
                'time': 'Heure',
                'session_id': 'Session ID',
                'country': 'Pays',
                'city': 'Ville',
                'client_ip': 'IP Utilisateur'
            }
            location_display.columns = [column_mapping.get(col, col) for col in location_display.columns]
            
            # Trier par ordre chronologique (plus récent en premier)
            try:
                # Créer une colonne datetime pour le tri
                location_display['datetime_sort'] = pd.to_datetime(location_display['Date'].astype(str) + ' ' + location_display['Heure'].astype(str), errors='coerce')
                # Trier par datetime décroissant (plus récent en premier)
                location_display = location_display.sort_values('datetime_sort', ascending=False)
                # Supprimer la colonne de tri temporaire
                location_display = location_display.drop('datetime_sort', axis=1)
            except Exception as e:
                st.write(f"⚠️ Impossible de trier chronologiquement: {e}")
            
            st.dataframe(location_display, use_container_width=True)
            
            # Liste des pays et villes uniques
            col1, col2 = st.columns(2)
            
            with col1:
                if 'country' in location_data.columns:
                    unique_countries = location_data['country'].dropna().unique()
                    unique_countries = [c for c in unique_countries if c != 'Non spécifié' and c is not None]
                    if unique_countries:
                        st.subheader("🌍 Pays Uniques")
                        for country in sorted(unique_countries):
                            st.write(f"• {country}")
                    else:
                        st.subheader("🌍 Pays Uniques")
                        st.write("Aucun pays spécifié")
                else:
                    st.subheader("🌍 Pays Uniques")
                    st.write("Données non disponibles")
            
            with col2:
                if 'city' in location_data.columns:
                    unique_cities = location_data['city'].dropna().unique()
                    unique_cities = [c for c in unique_cities if c != 'Non spécifié' and c is not None]
                    if unique_cities:
                        st.subheader("🏙️ Villes Uniques")
                        for city in sorted(unique_cities):
                            st.write(f"• {city}")
                    else:
                        st.subheader("🏙️ Villes Uniques")
                        st.write("Aucune ville spécifiée")
                else:
                    st.subheader("🏙️ Villes Uniques")
                    st.write("Données non disponibles")
        else:
            st.info("Aucune donnée de session disponible")
    
    with tab2:
        st.subheader("📊 Tracking par fichier")
        
        # Récupère la liste dynamique des fichiers
        all_files = get_available_files()
        
        # Sépare les fichiers par type
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.JPG', '.JPEG', '.PNG', '.GIF']
        pdf_extensions = ['.pdf', '.PDF']
        
        image_files = []
        pdf_files = []
        
        for file in all_files:
            if any(file.endswith(ext) for ext in image_extensions):
                image_files.append(file)
            elif any(file.endswith(ext) for ext in pdf_extensions):
                pdf_files.append(file)
        
        if not clicks_df.empty:
            # Extrait les noms de fichiers depuis les pages cliquées
            clicks_df['filename'] = clicks_df['page'].apply(extract_filename_from_page)
            
            # Compte les clics par fichier
            file_clicks = clicks_df['filename'].value_counts().reset_index()
            file_clicks.columns = ['Fichier', 'Nombre de Clics']
            
            # Crée les DataFrames pour images et PDFs
            images_df = pd.DataFrame({'Fichier': image_files})
            pdfs_df = pd.DataFrame({'Fichier': pdf_files})
            
            # Fusionne avec les clics existants pour les images
            if not images_df.empty:
                final_images_df = images_df.merge(file_clicks, on='Fichier', how='left')
                final_images_df['Nombre de Clics'] = final_images_df['Nombre de Clics'].fillna(0).astype(int)
                final_images_df = final_images_df.sort_values(['Nombre de Clics', 'Fichier'], ascending=[False, True])
            else:
                final_images_df = pd.DataFrame()
            
            # Fusionne avec les clics existants pour les PDFs
            if not pdfs_df.empty:
                final_pdfs_df = pdfs_df.merge(file_clicks, on='Fichier', how='left')
                final_pdfs_df['Nombre de Clics'] = final_pdfs_df['Nombre de Clics'].fillna(0).astype(int)
                final_pdfs_df = final_pdfs_df.sort_values(['Nombre de Clics', 'Fichier'], ascending=[False, True])
            else:
                final_pdfs_df = pd.DataFrame()
            
            # Affiche les tableaux séparés
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🖼️ Images")
                if not final_images_df.empty:
                    st.dataframe(final_images_df, use_container_width=True)
                else:
                    st.info("Aucune image trouvée")
            
            with col2:
                st.subheader("📄 PDFs")
                if not final_pdfs_df.empty:
                    st.dataframe(final_pdfs_df, use_container_width=True)
                else:
                    st.info("Aucun PDF trouvé")
            
        else:
            # Si pas de clics, affiche juste les listes avec 0 clic
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🖼️ Images")
                if image_files:
                    images_df = pd.DataFrame({
                        'Fichier': image_files,
                        'Nombre de Clics': [0] * len(image_files)
                    })
                    images_df = images_df.sort_values('Fichier')
                    st.dataframe(images_df, use_container_width=True)
                else:
                    st.info("Aucune image trouvée")
            
            with col2:
                st.subheader("📄 PDFs")
                if pdf_files:
                    pdfs_df = pd.DataFrame({
                        'Fichier': pdf_files,
                        'Nombre de Clics': [0] * len(pdf_files)
                    })
                    pdfs_df = pdfs_df.sort_values('Fichier')
                    st.dataframe(pdfs_df, use_container_width=True)
                else:
                    st.info("Aucun PDF trouvé")
            
            st.info("Aucun clic enregistré pour le moment")
    
    with tab3:
        st.subheader("🛤️ Analyse des Parcours Utilisateurs")
        
        journey_df, top_paths = analyze_user_journey(clicks_df, sessions_df)
        
        if not journey_df.empty:
            # Parcours les plus communs
            st.subheader("🏆 Parcours les Plus Fréquents")
            if top_paths:
                paths_data = pd.DataFrame(top_paths, columns=['Parcours', 'Fréquence'])
                fig = px.bar(paths_data.head(5), x='Fréquence', y='Parcours', 
                            orientation='h', title="Top 5 des Parcours")
                st.plotly_chart(fig, use_container_width=True)
            
            # Détails des parcours
            st.subheader("📋 Détails des Parcours")
            st.dataframe(journey_df, use_container_width=True)
        else:
            st.info("Aucune session disponible")
    
    # Bouton de rafraîchissement
    if st.sidebar.button("🔄 Rafraîchir les données"):
        st.rerun()

if __name__ == "__main__":
    main() 