import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests

# Streamlit Cloud: aucune dépendance à config_setup.py nécessaire
APP_TITLE = "Tracking nexgate Christelle"

st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")

@st.cache_data(ttl=60)
def get_analytics_data():
    # Récupère les données depuis Nexgate uniquement. Pas de fallback.
    try:
        response = requests.get(
            'https://christellelusso.nexgate.ch/analytics_data.json',
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except Exception as err:
        st.error("Nexgate indisponible: impossible de charger les données en production.")
        st.caption(str(err))
        return pd.DataFrame(), pd.DataFrame()

    sessions = []
    clicks = []
            for entry in data:
        t = entry.get('type')
        if t == 'session_start':
            sessions.append({
                        'session_id': entry.get('session_id', ''),
                        'timestamp': entry.get('timestamp', ''),
                        'country': entry.get('country', ''),
                        'city': entry.get('city', ''),
                'client_ip': entry.get('client_ip', ''),
                        'latitude': entry.get('latitude', 0),
                        'longitude': entry.get('longitude', 0)
                    })
        elif t == 'click':
            clicks.append({
                'session_id': entry.get('session_id', ''),
                'timestamp': entry.get('timestamp', ''),
                'page': entry.get('page', ''),
                'file_clicked': entry.get('file_clicked', ''),
                'sequence_order': entry.get('sequence_order', 0)
            })

    return pd.DataFrame(sessions), pd.DataFrame(clicks)


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")
    st.title(APP_TITLE)

    sessions_df, clicks_df = get_analytics_data()

    # Bandeau d'information source
    st.success("Données récupérées depuis le serveur web (nexgate.ch)")

    # Métriques principales (alignées Nexgate)
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Clics Totaux", int(len(clicks_df)) if not clicks_df.empty else 0)
    with c2:
        st.metric("Sessions Totales", int(sessions_df['session_id'].nunique()) if not sessions_df.empty else 0)

    tab1, tab2, tab3 = st.tabs(["🌍 Géolocalisation", "📁 Tracking par fichier", "🚶 Parcours Utilisateurs"])

    # Onglet Géolocalisation (tableau: Date, Heure, Session ID, Pays, Ville, IP)
    with tab1:
        if sessions_df.empty:
            st.info("Aucune session")
        else:
            df = sessions_df.copy()
            df['__ts'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.sort_values('__ts', ascending=False)
            df['Date'] = df['__ts'].dt.date.astype(str)
            df['Heure'] = df['__ts'].dt.strftime('%H:%M:%S')
            df.rename(columns={'session_id': 'Session ID', 'country': 'Pays', 'city': 'Ville', 'client_ip': 'IP Utilisateur'}, inplace=True)
            ordered = ['Date', 'Heure', 'Session ID', 'Pays', 'Ville', 'IP Utilisateur']
            show_cols = [c for c in ordered if c in df.columns]
            st.subheader("🌍 Géolocalisation des Sessions")
            st.dataframe(df[show_cols], use_container_width=True)

    # Onglet Fichiers cliqués
    with tab2:
        st.subheader("📁 Fichiers les Plus Cliqués")
        if clicks_df.empty:
            st.info("Aucun clic")
        else:
            files = clicks_df['file_clicked'].dropna()
            if not files.empty:
                counts = files.value_counts().head(15)
                fig = px.bar(x=counts.index, y=counts.values, title="Fichiers les plus cliqués")
                fig.update_xaxes(title="Fichier")
                fig.update_yaxes(title="Nombre de clics")
                st.plotly_chart(fig, use_container_width=True)
            details = clicks_df.copy()
            details['Date'] = pd.to_datetime(details['timestamp']).dt.strftime('%d/%m/%Y %H:%M')
            st.dataframe(details[['Date', 'page', 'file_clicked']].fillna(''), use_container_width=True)

    # Onglet Parcours Utilisateurs (simplifié)
    with tab3:
        st.subheader("🚶 Parcours Utilisateurs")
        if clicks_df.empty:
            st.info("Aucun parcours disponible")
        else:
            journeys = (
                clicks_df.sort_values('sequence_order')
                .groupby('session_id')['page']
                .apply(lambda s: ' → '.join([p for p in s.astype(str) if p]))
                .reset_index(name='Parcours')
            )
            journeys.rename(columns={'session_id': 'Session ID'}, inplace=True)
            st.dataframe(journeys, use_container_width=True)


if __name__ == "__main__":
    main()


