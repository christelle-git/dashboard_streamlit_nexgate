import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from collections import Counter

"""Compatibilité Streamlit Cloud: fallback de configuration si config_setup.py
n'est pas présent dans le repo minimal déployé."""
try:
    from config_setup import Config
except Exception:
    class Config:
        DASHBOARD_TITLE = "Analytics Avancé - Christelle Lusso"
        DATABASE_PATH = ":memory:"
import requests
import os

st.set_page_config(
    page_title=Config.DASHBOARD_TITLE,
    page_icon="📊",
    layout="wide"
)

# Base de données
def init_database():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Table pour les sessions utilisateur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_ip TEXT,
            user_agent TEXT,
            start_time DATETIME,
            end_time DATETIME,
            country TEXT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            date DATE
        )
    ''')
    
    # Table pour les clics détaillés
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detailed_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            element_id TEXT,
            element_type TEXT,
            page TEXT,
            file_clicked TEXT,
            timestamp DATETIME,
            sequence_order INTEGER,
            date DATE
        )
    ''')
    
    # Table pour les parcours utilisateur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_journeys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            journey_path TEXT,
            total_clicks INTEGER,
            session_duration INTEGER,
            date DATE
        )
    ''')
    
    conn.commit()
    conn.close()

@st.cache_data(ttl=60)  # Cache pendant 1 minute pour les données distantes
def get_remote_analytics_data():
    """Récupère les données depuis le serveur distant"""
    try:
        # Utilise uniquement le fichier local en cas d'indisponibilité du serveur
        local_file = "test_local_data.json"
        if os.path.exists(local_file):
            with open(local_file, 'r') as f:
                data = json.load(f)
        else:
            st.warning("⚠️ Serveur nexgate.ch indisponible et fichier local non trouvé")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        if not data:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        # Convertit les données JSON en DataFrames
        sessions_data = []
        clicks_data = []
        
        for entry in data:
            timestamp = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
            session_id = entry.get('session_id', '')
            
            # Traite les sessions
            if entry.get('type') == 'session_start':
                sessions_data.append({
                    'session_id': session_id,
                    'user_ip': entry.get('client_ip', ''),
                    'user_agent': entry.get('user_agent', ''),
                    'start_time': timestamp,
                    'end_time': timestamp,  # À améliorer si on a les données de fin
                    'country': entry.get('country', ''),
                    'city': entry.get('city', ''),
                    'latitude': entry.get('latitude'),
                    'longitude': entry.get('longitude'),
                    'date': timestamp.date()
                })
            
            # Traite les clics
            elif entry.get('type') == 'click':
                clicks_data.append({
                    'session_id': session_id,
                    'element_id': entry.get('element_id', ''),
                    'element_type': entry.get('element_type', ''),
                    'page': entry.get('page', ''),
                    'file_clicked': entry.get('file_clicked', ''),
                    'timestamp': timestamp,
                    'sequence_order': entry.get('sequence_order', 0),
                    'date': timestamp.date()
                })
        
        sessions_df = pd.DataFrame(sessions_data)
        clicks_df = pd.DataFrame(clicks_data)
        
        # Crée un DataFrame vide pour les parcours (à implémenter si nécessaire)
        journeys_df = pd.DataFrame()
        
        return sessions_df, clicks_df, journeys_df
        
    except Exception as e:
        st.warning(f"Impossible de récupérer les données distantes: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def get_local_analytics_data():
    """Récupère les données depuis la base locale"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    
    # Données de sessions
    sessions_query = """
    SELECT * FROM user_sessions 
    WHERE date >= date('now', '-30 days')
    ORDER BY start_time DESC
    """
    sessions_df = pd.read_sql_query(sessions_query, conn)
    
    # Données de clics détaillés
    clicks_query = """
    SELECT * FROM detailed_clicks 
    WHERE date >= date('now', '-30 days')
    ORDER BY timestamp DESC
    """
    clicks_df = pd.read_sql_query(clicks_query, conn)
    
    # Données de parcours
    journeys_query = """
    SELECT * FROM user_journeys 
    WHERE date >= date('now', '-30 days')
    ORDER BY date DESC
    """
    journeys_df = pd.read_sql_query(journeys_query, conn)
    
    conn.close()
    return sessions_df, clicks_df, journeys_df

@st.cache_data(ttl=1, show_spinner=False)  # Cache réduit à 1 seconde pour des mises à jour immédiates
def get_analytics_data():
    """Récupère les données depuis le serveur web"""
    try:
        # Récupère les données depuis votre serveur web
        response = requests.get('https://christellelusso.nexgate.ch/analytics_data.json', timeout=10)
        if response.status_code == 200:
            data = response.json()
    
            # Convertit les données JSON en DataFrames
            sessions_data = []
            clicks_data = []
            
            for entry in data:
                if entry.get('type') == 'session_start':
                    sessions_data.append({
                        'session_id': entry.get('session_id', ''),
                        'user_ip': entry.get('client_ip', ''),
                        'user_agent': entry.get('user_agent', ''),
                        'start_time': entry.get('timestamp', ''),
                        'country': entry.get('country', ''),
                        'city': entry.get('city', ''),
                        'latitude': entry.get('latitude', 0),
                        'longitude': entry.get('longitude', 0),
                        'date': entry.get('timestamp', '')[:10] if entry.get('timestamp') else ''
                    })
                elif entry.get('type') == 'session_end':
                    # Met à jour la session existante avec les données de fin
                    session_id = entry.get('session_id', '')
                    # Cherche si cette session existe déjà dans sessions_data
                    for session in sessions_data:
                        if session['session_id'] == session_id:
                            session['end_time'] = entry.get('timestamp', '')
                            session['session_duration'] = entry.get('session_duration', 0)
                            session['click_count'] = entry.get('click_count', 0)
                            break
                    else:
                        # Si la session n'existe pas, on la crée avec les données de fin
                        sessions_data.append({
                            'session_id': session_id,
                            'user_ip': entry.get('client_ip', ''),
                            'user_agent': entry.get('user_agent', ''),
                            'start_time': None,  # Pas de début de session
                            'end_time': entry.get('timestamp', ''),
                            'country': entry.get('country', ''),
                            'city': entry.get('city', ''),
                            'latitude': entry.get('latitude', 0),
                            'longitude': entry.get('longitude', 0),
                            'date': entry.get('timestamp', '')[:10] if entry.get('timestamp') else '',
                            'session_duration': entry.get('session_duration', 0),
                            'click_count': entry.get('click_count', 0)
                        })
                elif entry.get('type') == 'click':
                    clicks_data.append({
                        'session_id': entry.get('session_id', ''),
                        'element_id': entry.get('element_id', ''),
                        'element_type': entry.get('element_type', ''),
                        'page': entry.get('page', ''),
                        'file_clicked': entry.get('file_clicked', ''),
                        'timestamp': entry.get('timestamp', ''),
                        'sequence_order': entry.get('sequence_order', 0),
                        'date': entry.get('timestamp', '')[:10] if entry.get('timestamp') else '',
                        'country': entry.get('country', ''),
                        'city': entry.get('city', ''),
                        'latitude': entry.get('latitude', 0),
                        'longitude': entry.get('longitude', 0)
                    })
            
            sessions_df = pd.DataFrame(sessions_data)
            clicks_df = pd.DataFrame(clicks_data)
            journeys_df = pd.DataFrame()  # À implémenter si nécessaire
            
            # Enrichit les sessions avec les données de géolocalisation des clics
            if not clicks_df.empty and not sessions_df.empty:
                # Récupère les données de géolocalisation depuis les clics
                location_data = clicks_df[['session_id', 'country', 'city', 'latitude', 'longitude']].dropna(subset=['country', 'city'])
    
                if not location_data.empty:
                    # Prend la première occurrence de géolocalisation par session
                    location_data = location_data.groupby('session_id').first().reset_index()
                    
                    # Fusionne avec les sessions
                    sessions_df = sessions_df.merge(location_data, on='session_id', how='left', suffixes=('', '_click'))
                    
                    # Remplit les valeurs manquantes
                    sessions_df['country'] = sessions_df['country'].fillna(sessions_df['country_click']).fillna('Non spécifié')
                    sessions_df['city'] = sessions_df['city'].fillna(sessions_df['city_click']).fillna('Non spécifié')
                    sessions_df['latitude'] = sessions_df['latitude'].fillna(sessions_df['latitude_click']).fillna(0)
                    sessions_df['longitude'] = sessions_df['longitude'].fillna(sessions_df['longitude_click']).fillna(0)
                    
                    # Supprime les colonnes en double
                    sessions_df = sessions_df.drop(['country_click', 'city_click', 'latitude_click', 'longitude_click'], axis=1, errors='ignore')
            
            return sessions_df, clicks_df, journeys_df, "web"  # Retourne la source
        else:
            # Fallback vers les données locales
            local_sessions, local_clicks, local_journeys = get_local_analytics_data()
            return local_sessions, local_clicks, local_journeys, "local"
            
    except Exception as e:
        # Fallback vers les données locales
        local_sessions, local_clicks, local_journeys = get_local_analytics_data()
        return local_sessions, local_clicks, local_journeys, "local"



def analyze_user_journey(clicks_df):
    """Analyse les parcours utilisateur"""
    if clicks_df.empty:
        return pd.DataFrame(), []
    
    # Groupe par session et crée les parcours
    journey_data = []
    common_paths = []
    
    for session_id in clicks_df['session_id'].unique():
        session_clicks = clicks_df[clicks_df['session_id'] == session_id].sort_values('sequence_order')
        
        if len(session_clicks) > 1:
            # Crée le chemin du parcours
            path = []
            files_clicked = []
            
            for _, click in session_clicks.iterrows():
                if click['page']:
                    path.append(click['page'])
                if click['file_clicked']:
                    files_clicked.append(click['file_clicked'])
            
            if path:
                journey_str = ' → '.join(path)
                files_str = ', '.join(files_clicked) if files_clicked else 'Aucun fichier'
                
                journey_data.append({
                    'session_id': session_id,
                    'parcours': journey_str,
                    'fichiers_cliques': files_str,
                    'nombre_clics': len(session_clicks),
                    'duree_estimee': f"{len(session_clicks) * 30}s"  # Estimation basique
                })
                
                common_paths.append(journey_str)
    
    journey_df = pd.DataFrame(journey_data)
    
    # Trouve les parcours les plus communs
    if common_paths:
        path_counts = Counter(common_paths)
        top_paths = path_counts.most_common(10)
    else:
        top_paths = []
    
    return journey_df, top_paths

def main():
    st.title("📊 Dashboard Analytics Avancé")
    st.sidebar.header("🔧 Options")
    
    # Initialize database
    init_database()
    
    # Récupération des données
    try:
        sessions_df, clicks_df, journeys_df, data_source = get_analytics_data()
        
        # Indicateur de source de données
        if data_source == "web":
            st.success(f"✅ Données récupérées depuis le serveur web (nexgate.ch) - {datetime.now().strftime('%H:%M:%S')}")
        else:
            st.info(f"ℹ️ Données récupérées depuis la base locale - {datetime.now().strftime('%H:%M:%S')}")
            
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        st.info("Assurez-vous que la base de données est initialisée et contient des données.")
        return
    
    # Filtres dans la sidebar
    date_range = st.sidebar.selectbox(
        "Période d'analyse",
        ["7 derniers jours", "30 derniers jours", "Tout"]
    )
    
    show_realtime = st.sidebar.checkbox("Actualisation automatique", value=False)
    
    if show_realtime:
        st.sidebar.info("🔄 Actualisation toutes les 30 secondes")
    
    # Bouton de rafraîchissement manuel
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔄 Rafraîchir"):
            st.cache_data.clear()
            st.rerun()
    with col2:
        if st.button("🗑️ Vider Cache"):
            st.cache_data.clear()
            st.success("Cache vidé !")
    
    # Métriques principales
    st.subheader("📈 Métriques Principales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sessions = len(sessions_df['session_id'].unique()) if not sessions_df.empty else 0
        st.metric("Sessions Totales", total_sessions)
    
    with col2:
        total_clicks = len(clicks_df) if not clicks_df.empty else 0
        st.metric("Clics Totaux", total_clicks)
    
    with col3:
        unique_countries = int(sessions_df['country'].nunique()) if not sessions_df.empty else 0
        st.metric("Pays Uniques", unique_countries)
    
    with col4:
        total_sessions = len(sessions_df) if not sessions_df.empty else 0
        st.metric("Sessions Totales", total_sessions)
    
    # Onglets pour différentes analyses
    tab1, tab2, tab3 = st.tabs(["🌍 Géolocalisation", "🛤️ Parcours Utilisateurs", "📁 Fichiers Cliqués"])
    
    with tab1:
        st.subheader("🌍 Géolocalisation des Sessions")
        
        if not sessions_df.empty:
            # Vérifie si nous avons des données de géolocalisation
            has_location_data = 'country' in sessions_df.columns or 'city' in sessions_df.columns
            
            # Détails des sessions avec géolocalisation
            st.subheader("📍 Détails des Sessions")
            
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
            
            # Affiche les sessions avec géolocalisation
            display_columns = ['session_id', 'country', 'city', 'start_time', 'user_ip']
            
            # Filtre les colonnes existantes
            available_columns = [col for col in display_columns if col in location_data.columns]
            location_display = location_data[available_columns].copy()
            
            # Renomme les colonnes pour l'affichage
            column_mapping = {
                'session_id': 'Session ID',
                'country': 'Pays',
                'city': 'Ville',
                'start_time': 'Heure de Début',
                'user_ip': 'IP Utilisateur',
            }
            location_display.columns = [column_mapping.get(col, col) for col in location_display.columns]
            
            st.dataframe(location_display, use_container_width=True)
            
            # Statistiques de géolocalisation
            st.subheader("📈 Statistiques de Géolocalisation")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                unique_countries = location_data['country'].nunique() if 'country' in location_data.columns else 0
                st.metric("Pays Uniques", unique_countries)
            
            with col2:
                unique_cities = location_data['city'].nunique() if 'city' in location_data.columns else 0
                st.metric("Villes Uniques", unique_cities)
            
            with col3:
                total_sessions = len(location_data)
                st.metric("Total Sessions", total_sessions)
        else:
            st.info("Aucune donnée de session disponible")
    
    with tab2:
        st.subheader("🛤️ Analyse des Parcours Utilisateurs")
        
        if not clicks_df.empty:
            journey_df, top_paths = analyze_user_journey(clicks_df)
            
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
                st.info("Aucun parcours utilisateur détecté")
        else:
            st.info("Aucune donnée de clics disponible")
    
    with tab3:
        st.subheader("📁 Analyse des Fichiers Cliqués")
        
        if not clicks_df.empty:
            files_data = clicks_df[clicks_df['file_clicked'].notna()]
            
            if not files_data.empty:
                # Top fichiers
                file_counts = files_data['file_clicked'].value_counts().head(10)
                fig = px.bar(x=file_counts.index, y=file_counts.values,
                           title="Top 10 des Fichiers les Plus Cliqués")
                fig.update_xaxes(title="Fichiers")
                fig.update_yaxes(title="Nombre de Clics")
                st.plotly_chart(fig, use_container_width=True)
                
                # Types de fichiers
                st.subheader("📊 Types de Fichiers")
                files_data_copy = files_data.copy()
                files_data_copy['file_extension'] = files_data_copy['file_clicked'].astype(str).str.split('.').str[-1]
                ext_counts = files_data_copy['file_extension'].value_counts()
                
                fig2 = px.pie(values=ext_counts.values, names=ext_counts.index,
                            title="Répartition par Type de Fichier")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Aucun fichier cliqué détecté")
        else:
            st.info("Aucune donnée de clics disponible")
    
    # Section d'export
    st.subheader("💾 Export des Données")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Télécharger Sessions"):
            csv = sessions_df.to_csv(index=False)
            st.download_button(
                label="Sessions CSV",
                data=csv,
                file_name=f"sessions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📥 Télécharger Clics"):
            csv = clicks_df.to_csv(index=False)
            st.download_button(
                label="Clics CSV",
                data=csv,
                file_name=f"clicks_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📥 Télécharger Parcours"):
            if not journeys_df.empty:
                csv = journeys_df.to_csv(index=False)
                st.download_button(
                    label="Parcours CSV",
                    data=csv,
                    file_name=f"journeys_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    # Auto-refresh
    if show_realtime:
        st.rerun()

if __name__ == "__main__":
    main()