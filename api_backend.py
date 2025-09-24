from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import requests
import re
from urllib.parse import urlparse
from config_setup import Config

app = Flask(__name__)
CORS(app, origins=Config.ALLOWED_ORIGINS)  # CORS configuré avec les origines autorisées

# Configuration depuis le fichier config
DATABASE_PATH = Config.DATABASE_PATH

def init_database():
    """Initialise la base de données avec toutes les tables nécessaires"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Table des sessions utilisateur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            user_ip TEXT,
            user_agent TEXT,
            start_time DATETIME,
            end_time DATETIME,
            duration_seconds INTEGER,
            country TEXT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            timezone TEXT,
            language TEXT,
            screen_resolution TEXT,
            referrer TEXT,
            total_clicks INTEGER DEFAULT 0,
            pages_visited INTEGER DEFAULT 0,
            date DATE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des clics détaillés
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detailed_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            element_id TEXT,
            element_type TEXT,
            element_class TEXT,
            element_text TEXT,
            page TEXT,
            file_clicked TEXT,
            file_extension TEXT,
            timestamp DATETIME,
            sequence_order INTEGER,
            x_coordinate INTEGER,
            y_coordinate INTEGER,
            date DATE,
            FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
        )
    ''')
    
    # Table des parcours utilisateur
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_journeys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            journey_path TEXT,
            journey_data TEXT,
            total_clicks INTEGER,
            session_duration INTEGER,
            date DATE,
            FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
        )
    ''')
    
    # Table des événements personnalisés
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            event_name TEXT,
            event_data TEXT,
            page TEXT,
            timestamp DATETIME,
            date DATE,
            FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
        )
    ''')
    
    # Table des téléchargements de fichiers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            file_url TEXT,
            file_name TEXT,
            file_extension TEXT,
            element_text TEXT,
            page TEXT,
            timestamp DATETIME,
            sequence_order INTEGER,
            date DATE,
            FOREIGN KEY (session_id) REFERENCES user_sessions (session_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée avec succès!")

@app.route('/api/track', methods=['POST'])
def track_event():
    """Endpoint principal pour recevoir les données de tracking"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Aucune donnée reçue'}), 400
        
        event_type = data.get('type')
        session_id = data.get('session_id')
        
        if not event_type or not session_id:
            return jsonify({'error': 'Type d\'événement et session_id requis'}), 400
        
        # Traitement selon le type d'événement
        if event_type == 'session_start':
            return handle_session_start(data)
        elif event_type == 'click':
            return handle_click_event(data)
        elif event_type == 'file_download':
            return handle_file_download(data)
        elif event_type == 'session_end':
            return handle_session_end(data)
        else:
            return jsonify({'error': f'Type d\'événement non supporté: {event_type}'}), 400
            
    except Exception as e:
        if Config.DEBUG:
            print(f"Erreur dans track_event: {e}")
        return jsonify({'error': 'Erreur interne du serveur'}), 500

def handle_session_start(data):
    """Gère le démarrage d'une session"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO user_sessions 
            (session_id, user_ip, user_agent, start_time, country, city, 
             latitude, longitude, timezone, language, screen_resolution, 
             referrer, date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('session_id'),
            request.remote_addr,
            data.get('user_agent'),
            data.get('start_time'),
            data.get('country'),
            data.get('city'),
            data.get('latitude'),
            data.get('longitude'),
            data.get('timezone'),
            data.get('language'),
            data.get('screen_resolution'),
            data.get('referrer'),
            datetime.now().date(),
            datetime.now()
        ))
        
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Session démarrée'})
        
    except Exception as e:
        if Config.DEBUG:
            print(f"Erreur dans handle_session_start: {e}")
        return jsonify({'error': 'Erreur lors du démarrage de session'}), 500
    finally:
        conn.close()

def handle_click_event(data):
    """Gère les événements de clic"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO detailed_clicks 
            (session_id, element_id, element_type, element_class, element_text,
             page, timestamp, sequence_order, x_coordinate, y_coordinate, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('session_id'),
            data.get('element_id'),
            data.get('element_type'),
            data.get('element_class'),
            data.get('element_text'),
            data.get('page'),
            data.get('timestamp'),
            data.get('sequence_order'),
            data.get('x_coordinate'),
            data.get('y_coordinate'),
            datetime.now().date()
        ))
        
        # Mettre à jour le compteur de clics dans la session
        cursor.execute('''
            UPDATE user_sessions 
            SET total_clicks = total_clicks + 1 
            WHERE session_id = ?
        ''', (data.get('session_id'),))
        
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Clic enregistré'})
        
    except Exception as e:
        if Config.DEBUG:
            print(f"Erreur dans handle_click_event: {e}")
        return jsonify({'error': 'Erreur lors de l\'enregistrement du clic'}), 500
    finally:
        conn.close()

def handle_file_download(data):
    """Gère les téléchargements de fichiers"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO file_downloads 
            (session_id, file_url, file_name, file_extension, element_text,
             page, timestamp, sequence_order, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('session_id'),
            data.get('file_url'),
            data.get('file_name'),
            data.get('file_extension'),
            data.get('element_text'),
            data.get('page'),
            data.get('timestamp'),
            data.get('sequence_order'),
            datetime.now().date()
        ))
        
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Téléchargement enregistré'})
        
    except Exception as e:
        if Config.DEBUG:
            print(f"Erreur dans handle_file_download: {e}")
        return jsonify({'error': 'Erreur lors de l\'enregistrement du téléchargement'}), 500
    finally:
        conn.close()

def handle_session_end(data):
    """Gère la fin d'une session"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        duration = data.get('duration_seconds', 0)
        
        cursor.execute('''
            UPDATE user_sessions 
            SET end_time = ?, duration_seconds = ?
            WHERE session_id = ?
        ''', (data.get('end_time'), duration, data.get('session_id')))
        
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Session terminée'})
        
    except Exception as e:
        if Config.DEBUG:
            print(f"Erreur dans handle_session_end: {e}")
        return jsonify({'error': 'Erreur lors de la fin de session'}), 500
    finally:
        conn.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de santé de l'API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    init_database()
    print(f"🚀 API Analytics démarrée sur http://localhost:{Config.API_PORT}")
    print(f"📊 Dashboard accessible sur http://localhost:{Config.DASHBOARD_PORT}")
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=Config.API_PORT)