import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import requests

# Streamlit Cloud: aucune dépendance à config_setup.py nécessaire
APP_TITLE = "Analytics Avancé - Christelle Lusso"

st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")

@st.cache_data(ttl=60)
def get_analytics_data():
    """Récupère les données avec fallbacks (HTTPS → HTTP → GitHub raw → fichier local). Retourne sessions_df, clicks_df."""
    urls = [
        'https://christellelusso.nexgate.ch/analytics_data.json',
        'http://christellelusso.nexgate.ch/analytics_data.json',
        'https://raw.githubusercontent.com/christelle-git/dashboard_streamlit_nexgate/streamlit-deploy/analytics_data.json'
    ]

    data = None
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                break
        except Exception:
            continue

    if data is None:
        try:
            import json as _json
            with open('analytics_data.json', 'r') as f:
                data = _json.load(f)
        except Exception as e:
            st.error(f"Impossible de récupérer les données (HTTPS/HTTP/GitHub/local): {e}")
            return pd.DataFrame(), pd.DataFrame()

    sessions, clicks = [], []
    for entry in data:
        if entry.get('type') == 'session_start':
            sessions.append({
                'session_id': entry.get('session_id', ''),
                'timestamp': entry.get('timestamp', ''),
                'country': entry.get('country', ''),
                'city': entry.get('city', ''),
                'client_ip': entry.get('client_ip', ''),
                'latitude': entry.get('latitude', 0),
                'longitude': entry.get('longitude', 0)
            })
        elif entry.get('type') == 'click':
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
    st.title("📊 Dashboard Analytics – Streamlit")

    sessions_df, clicks_df = get_analytics_data()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sessions", sessions_df['session_id'].nunique() if not sessions_df.empty else 0)
    with col2:
        st.metric("Clics", len(clicks_df) if not clicks_df.empty else 0)
    with col3:
        st.metric("Pays uniques", sessions_df['country'].nunique() if not sessions_df.empty and 'country' in sessions_df.columns else 0)

    tab1, tab2 = st.tabs(["🌍 Sessions", "📁 Fichiers cliqués"])
    
    with tab1:
        if sessions_df.empty:
            st.info("Aucune session")
        else:
            df = sessions_df.copy()
            df['Date'] = pd.to_datetime(df['timestamp']).dt.strftime('%d/%m/%Y %H:%M')
            st.dataframe(df[['Date', 'client_ip', 'country', 'city']], use_container_width=True)
    
    with tab2:
        if clicks_df.empty:
            st.info("Aucun clic")
        else:
            files = clicks_df['file_clicked'].dropna()
            if not files.empty:
                counts = files.value_counts().head(10)
                fig = px.bar(x=counts.index, y=counts.values, title="Top fichiers cliqués")
                fig.update_xaxes(title="Fichier")
                fig.update_yaxes(title="Clics")
                st.plotly_chart(fig, use_container_width=True)
            st.dataframe(clicks_df[['timestamp', 'page', 'file_clicked']].fillna(''), use_container_width=True)


if __name__ == "__main__":
    main()


