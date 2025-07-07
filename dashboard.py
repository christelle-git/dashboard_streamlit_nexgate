import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from collections import Counter
import folium
from streamlit_folium import folium_static
from config_setup import Config
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
            duration_seconds INTEGER,
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
                    'duration_seconds': 0,  # À calculer si on a les données de fin
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

@st.cache_data(ttl=60)  # Cache pendant 1 minute
def get_analytics_data():
    """Combine les données locales et distantes"""
    # Récupère les données distantes
    remote_sessions, remote_clicks, remote_journeys = get_remote_analytics_data()
    
    # Récupère les données locales
    local_sessions, local_clicks, local_journeys = get_local_analytics_data()
    
    # Combine les données (priorité aux données distantes si disponibles)
    if not remote_sessions.empty:
        sessions_df = remote_sessions
    else:
        sessions_df = local_sessions
    
    if not remote_clicks.empty:
        clicks_df = remote_clicks
    else:
        clicks_df = local_clicks
    
    if not remote_journeys.empty:
        journeys_df = remote_journeys
    else:
        journeys_df = local_journeys
    
    return sessions_df, clicks_df, journeys_df

def create_world_map(sessions_df):
    """Crée une carte mondiale des connexions"""
    if sessions_df.empty or sessions_df[['latitude', 'longitude']].isna().all().all():
        return None
    
    # Filtre les données avec coordonnées valides
    geo_data = sessions_df.dropna(subset=['latitude', 'longitude'])
    
    if geo_data.empty:
        return None
    
    # Centre la carte
    center_lat = geo_data['latitude'].mean()
    center_lon = geo_data['longitude'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=2)
    
    # Groupe les sessions par localisation
    location_counts = geo_data.groupby(['latitude', 'longitude', 'city', 'country']).size().reset_index(name='count')
    
    for _, row in location_counts.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=min(row['count'] * 2, 20),  # Taille proportionnelle
            popup=f"{row['city']}, {row['country']}<br>Sessions: {row['count']}",
            color='red',
            fill=True,
            fillOpacity=0.7
        ).add_to(m)
    
    return m

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
        sessions_df, clicks_df, journeys_df = get_analytics_data()
        
        # Indicateur de source de données
        remote_sessions, remote_clicks, _ = get_remote_analytics_data()
        if not remote_sessions.empty or not remote_clicks.empty:
            st.success("✅ Données récupérées depuis le fichier local (serveur nexgate.ch indisponible)")
        else:
            st.info("ℹ️ Données récupérées depuis la base locale")
            
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
        avg_duration = sessions_df['duration_seconds'].mean() if not sessions_df.empty else 0
        st.metric("Durée Moyenne", f"{avg_duration:.0f}s")
    
    with col4:
        unique_countries = sessions_df['country'].nunique() if not sessions_df.empty else 0
        st.metric("Pays Uniques", unique_countries)
    
    # Onglets pour différentes analyses
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Géolocalisation", "🛤️ Parcours Utilisateurs", "📁 Fichiers Cliqués", "⏱️ Temps de Session"])
    
    with tab1:
        st.subheader("🗺️ Carte des Connexions")
        
        if not sessions_df.empty:
            # Carte mondiale
            world_map = create_world_map(sessions_df)
            if world_map:
                folium_static(world_map, width=1200, height=600)
            else:
                st.info("Aucune donnée de géolocalisation disponible")
            
            # Tableau des pays
            st.subheader("📊 Statistiques par Pays")
            if not sessions_df.empty:
                country_stats = sessions_df.groupby('country').agg({
                    'session_id': 'count',
                    'duration_seconds': 'mean'
                }).round(2)
                country_stats.columns = ['Nombre de Sessions', 'Durée Moyenne (s)']
                st.dataframe(country_stats.sort_values('Nombre de Sessions', ascending=False))
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
                files_data['file_extension'] = files_data['file_clicked'].str.split('.').str[-1]
                ext_counts = files_data['file_extension'].value_counts()
                
                fig2 = px.pie(values=ext_counts.values, names=ext_counts.index,
                            title="Répartition par Type de Fichier")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Aucun fichier cliqué détecté")
        else:
            st.info("Aucune donnée de clics disponible")
    
    with tab4:
        st.subheader("⏱️ Analyse du Temps de Session")
        
        if not sessions_df.empty:
            # Distribution des durées
            fig = px.histogram(sessions_df, x='duration_seconds', nbins=20,
                             title="Distribution des Durées de Session")
            fig.update_xaxes(title="Durée (secondes)")
            fig.update_yaxes(title="Nombre de Sessions")
            st.plotly_chart(fig, use_container_width=True)
            
            # Évolution temporelle
            st.subheader("📈 Évolution de la Durée Moyenne")
            if not sessions_df.empty:
                daily_duration = sessions_df.groupby('date')['duration_seconds'].mean().reset_index()
                fig2 = px.line(daily_duration, x='date', y='duration_seconds',
                             title="Durée Moyenne par Jour")
                st.plotly_chart(fig2, use_container_width=True)
            
            # Statistiques détaillées
            st.subheader("📊 Statistiques Détaillées")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Durée Minimale", f"{sessions_df['duration_seconds'].min():.0f}s")
                st.metric("Durée Maximale", f"{sessions_df['duration_seconds'].max():.0f}s")
            
            with col2:
                st.metric("Médiane", f"{sessions_df['duration_seconds'].median():.0f}s")
                st.metric("Écart-type", f"{sessions_df['duration_seconds'].std():.0f}s")
        else:
            st.info("Aucune donnée de session disponible")
    
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