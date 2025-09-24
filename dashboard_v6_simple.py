import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import requests
import time

st.set_page_config(
    page_title="Dashboard Analytics V6 - Version Simplifiée",
    page_icon="📍",
    layout="wide"
)

def get_analytics_data_v6():
    """Récupère les données V6 depuis le serveur web"""
    try:
        response = requests.get('https://christellelusso.nexgate.ch/analytics_data_v6.json', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data, "✅ Données V6 récupérées depuis le serveur web"
        else:
            return [], f"❌ Erreur HTTP: {response.status_code}"
    except Exception as e:
        return [], f"❌ Serveur web indisponible ({e})"

def get_test_data_v6():
    """Retourne des données de test V6 simplifiées"""
    return [
        {
            "type": "click",
            "session_id": "test_session_1",
            "page": "drawing/mystic.jpg",
            "timestamp": "2025-07-29T15:30:00Z",
            "client_ip": "192.168.1.100",
            "ip_source": "ipify.org",
            "gps_latitude": 48.8566,
            "gps_longitude": 2.3522,
            "gps_accuracy": 10,
            "gps_source": "browser_gps",
            "geo_country": "France",
            "geo_city": "Paris",
            "geo_source": "ipapi.co"
        },
        {
            "type": "click",
            "session_id": "test_session_2",
            "page": "pdf/thesis.pdf",
            "timestamp": "2025-07-29T16:00:00Z",
            "client_ip": "192.168.1.101",
            "ip_source": "ipify.org",
            "gps_latitude": 46.2044,
            "gps_longitude": 6.1432,
            "gps_accuracy": 15,
            "gps_source": "browser_gps",
            "geo_country": "Suisse",
            "geo_city": "Genève",
            "geo_source": "ipapi.co"
        },
        {
            "type": "click",
            "session_id": "test_session_3",
            "page": "pdf/abstract_lusso.pdf",
            "timestamp": "2025-07-29T16:15:00Z",
            "client_ip": "192.168.1.102",
            "ip_source": "ipify.org",
            "gps_latitude": 0,
            "gps_longitude": 0,
            "gps_accuracy": 0,
            "gps_source": "none",
            "geo_country": "Canada",
            "geo_city": "Montréal",
            "geo_source": "ipapi.co"
        }
    ]

def process_data_v6_simple(data):
    """Traite les données JSON V6 de manière simplifiée"""
    if not data:
        return pd.DataFrame(), pd.DataFrame()
    
    # Convertit en DataFrame
    df = pd.DataFrame(data)
    
    # Séparer les clics et les sessions
    clicks_df = df[df['type'] == 'click'].copy() if 'click' in df['type'].values else pd.DataFrame()
    
    if not clicks_df.empty:
        # Créer un DataFrame de sessions simplifié
        sessions_data = []
        
        for session_id in clicks_df['session_id'].unique():
            session_clicks = clicks_df[clicks_df['session_id'] == session_id]
            
            # Première et dernière activité
            timestamps = pd.to_datetime(session_clicks['timestamp'])
            session_start = timestamps.min()
            session_end = timestamps.max()
            
            # Données de la session
            first_click = session_clicks.iloc[0]
            
            session_data = {
                'session_id': session_id,
                'session_start': session_start,
                'session_end': session_end,
                'duration_seconds': (session_end - session_start).total_seconds(),
                'click_count': len(session_clicks),
                'client_ip': first_click.get('client_ip', 'Non spécifié'),
                'ip_source': first_click.get('ip_source', 'Non spécifié'),
                'gps_latitude': first_click.get('gps_latitude', 0),
                'gps_longitude': first_click.get('gps_longitude', 0),
                'gps_accuracy': first_click.get('gps_accuracy', 0),
                'gps_source': first_click.get('gps_source', 'none'),
                'geo_country': first_click.get('geo_country', 'Non spécifié'),
                'geo_city': first_click.get('geo_city', 'Non spécifié'),
                'geo_source': first_click.get('geo_source', 'Non spécifié')
            }
            
            sessions_data.append(session_data)
        
        sessions_df = pd.DataFrame(sessions_data)
    else:
        sessions_df = pd.DataFrame()
    
    return sessions_df, clicks_df

def create_simple_gps_chart(sessions_df):
    """Crée un graphique GPS simple"""
    if sessions_df.empty:
        return None
    
    # Filtrer les sessions avec GPS
    gps_sessions = sessions_df[
        (sessions_df['gps_source'] != 'none') & 
        (sessions_df['gps_latitude'] != 0) & 
        (sessions_df['gps_longitude'] != 0)
    ].copy()
    
    if gps_sessions.empty:
        return None
    
    # Créer le graphique
    fig = go.Figure()
    
    fig.add_trace(go.Scattergeo(
        lon=gps_sessions['gps_longitude'],
        lat=gps_sessions['gps_latitude'],
        mode='markers',
        name='Positions GPS',
        marker=dict(
            size=10,
            color='red',
            symbol='circle'
        ),
        text=gps_sessions['session_id'],
        hovertemplate='<b>Session: %{text}</b><br>' +
                     'Lat: %{lat:.4f}<br>' +
                     'Lon: %{lon:.4f}<br>' +
                     'Précision: ' + gps_sessions['gps_accuracy'].astype(str) + 'm<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title='Positions GPS des Sessions',
        geo=dict(
            scope='world',
            projection_type='equirectangular',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
        ),
        height=400
    )
    
    return fig

def main():
    st.title("📍 Dashboard Analytics V6 - Version Simplifiée")
    st.markdown("**Version avec séparation IP et GPS - Gestion robuste des données**")
    
    # Récupération des données
    data, status = get_analytics_data_v6()
    
    if not data:
        st.warning("⚠️ Aucune donnée V6 disponible. Utilisation des données de test.")
        data = get_test_data_v6()
        status = "🧪 Données de test utilisées"
    
    st.info(status)
    
    # Traitement des données
    sessions_df, clicks_df = process_data_v6_simple(data)
    
    if sessions_df.empty:
        st.warning("Aucune session trouvée dans les données.")
        return
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sessions totales", len(sessions_df))
    
    with col2:
        gps_sessions = len(sessions_df[sessions_df['gps_source'] != 'none'])
        st.metric("Sessions avec GPS", f"{gps_sessions} ({gps_sessions/len(sessions_df)*100:.1f}%)")
    
    with col3:
        total_clicks = len(clicks_df) if not clicks_df.empty else 0
        st.metric("Clics totaux", total_clicks)
    
    with col4:
        avg_duration = sessions_df['duration_seconds'].mean() if 'duration_seconds' in sessions_df.columns else 0
        st.metric("Durée moyenne", f"{avg_duration:.1f}s")
    
    st.markdown("---")
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["📊 Vue d'ensemble", "🌐 Données IP", "📍 Données GPS"])
    
    with tab1:
        st.subheader("Vue d'ensemble des sessions")
        
        # Tableau des sessions
        display_columns = ['session_id', 'session_start', 'duration_seconds', 'click_count']
        
        # Ajouter les colonnes disponibles
        for col in ['client_ip', 'gps_source', 'geo_city', 'geo_country']:
            if col in sessions_df.columns:
                display_columns.append(col)
        
        display_sessions = sessions_df[display_columns].copy()
        
        # Formater les timestamps
        if 'session_start' in display_sessions.columns:
            display_sessions['session_start'] = display_sessions['session_start'].dt.strftime('%H:%M:%S')
        
        # Formater la durée
        if 'duration_seconds' in display_sessions.columns:
            display_sessions['duration_seconds'] = display_sessions['duration_seconds'].round(1)
        
        st.dataframe(display_sessions, use_container_width=True)
    
    with tab2:
        st.subheader("Données IP et Géolocalisation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'ip_source' in sessions_df.columns:
                st.markdown("**Sources d'IP**")
                ip_sources = sessions_df['ip_source'].value_counts()
                fig_ip = px.pie(values=ip_sources.values, names=ip_sources.index, title="Répartition des sources d'IP")
                st.plotly_chart(fig_ip, use_container_width=True)
        
        with col2:
            if 'geo_country' in sessions_df.columns:
                st.markdown("**Pays par géolocalisation IP**")
                countries = sessions_df['geo_country'].value_counts().head(10)
                fig_countries = px.bar(x=countries.values, y=countries.index, orientation='h', title="Top 10 des pays")
                st.plotly_chart(fig_countries, use_container_width=True)
        
        # Tableau des données IP
        st.markdown("**Détails des données IP**")
        ip_columns = ['session_id']
        for col in ['client_ip', 'ip_source', 'geo_city', 'geo_country', 'geo_source']:
            if col in sessions_df.columns:
                ip_columns.append(col)
        
        if len(ip_columns) > 1:
            ip_details = sessions_df[ip_columns].copy()
            st.dataframe(ip_details, use_container_width=True)
        else:
            st.info("Aucune donnée IP disponible")
    
    with tab3:
        st.subheader("Données GPS")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'gps_source' in sessions_df.columns:
                st.markdown("**Disponibilité GPS**")
                gps_availability = sessions_df['gps_source'].value_counts()
                fig_gps = px.pie(values=gps_availability.values, names=gps_availability.index, title="Disponibilité du GPS")
                st.plotly_chart(fig_gps, use_container_width=True)
        
        with col2:
            gps_sessions = sessions_df[sessions_df['gps_source'] != 'none']
            if not gps_sessions.empty and 'gps_accuracy' in gps_sessions.columns:
                st.markdown("**Précision GPS**")
                fig_accuracy = px.histogram(gps_sessions, x='gps_accuracy', 
                                          title="Distribution de la précision GPS (mètres)",
                                          nbins=10)
                st.plotly_chart(fig_accuracy, use_container_width=True)
        
        # Carte des positions GPS
        gps_chart = create_simple_gps_chart(sessions_df)
        if gps_chart:
            st.plotly_chart(gps_chart, use_container_width=True)
        else:
            st.info("Aucune donnée GPS disponible pour la carte")
    
    # Informations techniques
    with st.expander("ℹ️ Informations techniques"):
        st.markdown("""
        **Version simplifiée V6 :**
        
        - **Séparation IP/GPS** : Les données d'IP et de GPS sont stockées séparément
        - **Gestion robuste** : Gère les champs manquants et les données de test
        - **Sources multiples** : Chaque donnée indique sa source
        - **Visualisations** : Graphiques et cartes interactives
        
        **Champs principaux :**
        - `gps_latitude`, `gps_longitude`, `gps_accuracy`, `gps_source`
        - `ip_source`, `geo_source`
        - `geo_country`, `geo_city`
        """)

if __name__ == "__main__":
    main() 