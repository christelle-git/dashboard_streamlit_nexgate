import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import requests
import time
import os
import re

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
    try:
        response = requests.get('https://christellelusso.nexgate.ch/analytics_data.json', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data, "✅ Données récupérées depuis le serveur web (nexgate.ch)"
        else:
            st.error(f"Erreur HTTP: {response.status_code}")
            return [], "❌ Erreur lors de la récupération des données"
    except Exception as e:
        st.error(f"Erreur de connexion: {e}")
        return [], "❌ Serveur indisponible"

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
    
    # Traitement des données
    if not clicks_df.empty:
        # Compter les clics par session
        clicks_per_session = clicks_df.groupby('session_id').size().reset_index(name='click_count')
        sessions_df = clicks_df.groupby('session_id').agg({
            'timestamp': ['min', 'max'],  # début et fin de session
            'country': 'first',
            'city': 'first',
            'latitude': 'first',
            'longitude': 'first'
        }).reset_index()
        
        # Renommer les colonnes
        sessions_df.columns = ['session_id', 'session_start', 'session_end', 'country', 'city', 'latitude', 'longitude']
        
        # Calculer la durée de session (en secondes)
        sessions_df['session_start'] = pd.to_datetime(sessions_df['session_start'])
        sessions_df['session_end'] = pd.to_datetime(sessions_df['session_end'])
        sessions_df['duration_seconds'] = (sessions_df['session_end'] - sessions_df['session_start']).dt.total_seconds()
        
        sessions_df = sessions_df.merge(clicks_per_session, on='session_id')
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
    tab1, tab2 = st.tabs(["🌍 Géolocalisation", "📊 Tracking par fichier"])
    
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
            
            # Affiche les sessions avec géolocalisation
            display_columns = ['session_id', 'country', 'city', 'timestamp', 'client_ip']
            available_columns = [col for col in display_columns if col in location_data.columns]
            location_display = location_data[available_columns].copy()
            
            # Renomme les colonnes pour l'affichage
            column_mapping = {
                'session_id': 'Session ID',
                'country': 'Pays',
                'city': 'Ville',
                'timestamp': 'Heure',
                'client_ip': 'IP Utilisateur'
            }
            location_display.columns = [column_mapping.get(col, col) for col in location_display.columns]
            
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
    
    # Bouton de rafraîchissement
    if st.sidebar.button("🔄 Rafraîchir les données"):
        st.rerun()

if __name__ == "__main__":
    main() 