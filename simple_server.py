#!/usr/bin/env python3
"""
Serveur local simple pour tester le tracking analytics
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
from datetime import datetime

class AnalyticsHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/track':
            # Lire les données JSON
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                print(f"📊 Données reçues: {data}")
                
                # Sauvegarder dans un fichier local
                self.save_analytics_data(data)
                
                # Réponse de succès
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                response = {
                    'success': True,
                    'message': 'Data saved successfully',
                    'data_type': data.get('type'),
                    'session_id': data.get('session_id')
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        # Gérer les requêtes preflight CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def save_analytics_data(self, data):
        """Sauvegarde les données analytics dans un fichier local"""
        filename = 'local_analytics_data.json'
        
        # Lire les données existantes
        existing_data = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except:
                existing_data = []
        
        # Ajouter les nouvelles données
        existing_data.append(data)
        
        # Sauvegarder
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Données sauvegardées dans {filename}")

def run_server(port=8000):
    """Démarre le serveur local"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, AnalyticsHandler)
    print(f"🚀 Serveur démarré sur http://localhost:{port}")
    print(f"📊 API tracking: http://localhost:{port}/api/track")
    print("Appuyez sur Ctrl+C pour arrêter")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")
        httpd.server_close()

if __name__ == '__main__':
    run_server() 