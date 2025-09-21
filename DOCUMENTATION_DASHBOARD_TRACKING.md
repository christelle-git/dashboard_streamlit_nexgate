# 📊 Documentation du Dashboard de Tracking Analytics

## 🎯 Vue d'ensemble

Ce dashboard de tracking analytics permet de visualiser et analyser les données de visite d'un site web en temps réel. Il collecte les interactions utilisateurs, la géolocalisation, et génère des rapports détaillés.

## 🏗️ Architecture du Système

### **Composants principaux :**

1. **Frontend (Site web)** : `index.html` avec `tracker_v6.js`
2. **API Backend** : `api.php` pour collecter les données
3. **Base de données** : `analytics_data.json` (fichier JSON)
4. **Dashboard** : `dashboard_simple.py` (Streamlit)
5. **Scripts de déploiement** : Scripts shell pour l'automatisation

### **Flux de données :**

```
Utilisateur → Site Web → Tracker JS → API PHP → analytics_data.json → Dashboard Streamlit
```

## 📁 Structure des Fichiers

```
app-streamlit-nexgate/
├── 📊 Dashboard
│   ├── dashboard_simple.py          # Dashboard principal
│   ├── dashboard_v6_simple.py       # Version alternative
│   └── dashboard.py                  # Version originale
│
├── 🎯 Tracker JavaScript
│   ├── tracker_v5.js                # Tracker de base
│   ├── tracker_v6_improved.js       # Tracker complet
│   └── system_nexgate.js            # Système de tracking
│
├── 🌐 Site Web
│   ├── index.html                   # Page principale
│   ├── index_nexgate.html           # Version Nexgate
│   └── style.css                    # Styles CSS
│
├── 🔌 API Backend
│   ├── api.php                      # API principale
│   ├── api_nexgate.php              # API Nexgate
│   └── api_nexgate_fixed.php        # API corrigée
│
├── 📊 Données
│   ├── analytics_data.json          # Données de production
│   └── analytics_data_v6.json       # Données de test
│
├── 🧪 Tests et Diagnostic
│   ├── test_tracker_debug.html      # Page de test interactive
│   ├── test_session_end.py          # Test des événements
│   └── debug_dashboard_data.py      # Diagnostic des données
│
├── 🚀 Déploiement
│   ├── start_all.sh                 # Script de lancement
│   ├── start_dashboard_original.sh  # Lancement dashboard original
│   └── deploy.sh                    # Script de déploiement
│
└── 📚 Documentation
    ├── DOCUMENTATION_DASHBOARD_TRACKING.md
    ├── OPTIONS_DASHBOARDS.md
    └── notes.md
```

## 🔧 Configuration et Installation

### **1. Prérequis**

- Python 3.11+
- Node.js (pour le développement)
- Serveur web (Apache/Nginx)
- PHP 7.4+

### **2. Installation locale**

```bash
# Cloner le repository
git clone https://github.com/votre-repo/dashboard-tracking.git
cd dashboard-tracking

# Créer l'environnement virtuel
python3 -m venv streamlit_env
source streamlit_env/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le dashboard
./start_all.sh
```

### **3. Configuration de production**

```bash
# Variables d'environnement
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export ANALYTICS_DATA_URL=https://christellelusso.nexgate.ch/analytics_data.json
```

## 📊 Fonctionnalités du Dashboard

### **1. Géolocalisation des Sessions**
- **Carte interactive** avec Plotly
- **Tableau détaillé** des sessions
- **Tri chronologique** (plus récentes en premier)
- **Colonnes** : Date, Heure, IP, Pays, Ville, Coordonnées

### **2. Tracking par Fichier**
- **Analyse des clics** par page/fichier
- **Statistiques** de popularité
- **Graphiques** de distribution

### **3. Parcours Utilisateurs**
- **Détails des parcours** par session
- **Séquence des clics** chronologique
- **Métriques** : Durée, nombre de clics

### **4. Métriques Globales**
- **Total des sessions**
- **Sessions uniques**
- **Durée moyenne**
- **Clics totaux**

## 🎯 Types d'Événements Trackés

### **1. session_start**
```json
{
  "type": "session_start",
  "session_id": "session_1756292264308_r90cr7ckm",
  "timestamp": "2025-08-27T10:57:44.309Z",
  "user_agent": "Mozilla/5.0...",
  "page": "/",
  "referrer": "https://google.com",
  "language": "fr",
  "timezone": "Europe/Paris"
}
```

### **2. click**
```json
{
  "type": "click",
  "session_id": "session_1756292264308_r90cr7ckm",
  "timestamp": "2025-08-27T10:57:50.000Z",
  "page": "/",
  "element_type": "a",
  "sequence_order": 1,
  "x_coordinate": 100,
  "y_coordinate": 200,
  "gps_latitude": 47.0241,
  "gps_longitude": 4.8389
}
```

### **3. session_end**
```json
{
  "type": "session_end",
  "session_id": "session_1756292264308_r90cr7ckm",
  "timestamp": "2025-08-27T10:57:57.971Z",
  "duration": 13662,
  "click_count": 3
}
```

## 🔄 Workflow de Développement

### **1. Développement local**
```bash
# Lancer le dashboard en mode développement
./start_dashboard_original.sh

# Tester les modifications
# Le dashboard se rafraîchit automatiquement
```

### **2. Tests**
```bash
# Tester le tracker
open test_tracker_debug.html

# Tester les données
python test_session_end.py
```

### **3. Déploiement**
```bash
# Commiter les changements
git add .
git commit -m "Description des changements"
git push origin main

# Déployer sur le serveur
./deploy.sh
```

## 🛠️ Maintenance et Monitoring

### **1. Surveillance des performances**
- **Logs** : Vérifier les logs du serveur
- **Métriques** : Surveiller l'utilisation CPU/RAM
- **Erreurs** : Monitorer les erreurs JavaScript

### **2. Sauvegarde des données**
```bash
# Sauvegarde quotidienne
cp analytics_data.json "backup/analytics_data_$(date +%Y%m%d).json"
```

### **3. Mise à jour**
```bash
# Mise à jour du code
git pull origin main
pip install -r requirements.txt
```

## 🔒 Sécurité

### **1. Protection des données**
- **HTTPS** obligatoire en production
- **Validation** des données d'entrée
- **Sanitisation** des logs

### **2. Accès au dashboard**
- **Authentification** (optionnelle)
- **IP whitelist** (recommandé)
- **Rate limiting** sur l'API

## 📈 Évolutions Futures

### **1. Fonctionnalités prévues**
- **Authentification** utilisateur
- **Export** des données (CSV, PDF)
- **Alertes** en temps réel
- **API REST** pour intégrations

### **2. Améliorations techniques**
- **Base de données** SQL (PostgreSQL)
- **Cache** Redis pour les performances
- **Docker** pour la containerisation
- **CI/CD** avec GitHub Actions

## 🐛 Dépannage

### **Problèmes courants :**

1. **Dashboard ne se lance pas**
   - Vérifier le port 8501
   - Vérifier les dépendances Python

2. **Données manquantes**
   - Vérifier l'API `api.php`
   - Vérifier le fichier `analytics_data.json`

3. **Géolocalisation incorrecte**
   - Vérifier les permissions GPS
   - Vérifier l'API de géolocalisation

### **Logs utiles :**
```bash
# Logs du dashboard
tail -f nohup.out

# Logs du serveur web
tail -f /var/log/apache2/error.log
```

## 📞 Support

Pour toute question ou problème :
1. Consulter cette documentation
2. Vérifier les logs
3. Tester avec `test_tracker_debug.html`
4. Créer une issue GitHub

## 🌐 Déploiement sur Nexgate (Hébergeur Web-FTP)

### **Problématique**
Nexgate ne propose qu'un accès Web-FTP, pas d'SSH ni de terminal. Impossible d'installer Python ou de lancer des services.

### **Solution Recommandée : Dashboard PHP**

1. **Fichiers à uploader :**
   - `dashboard_php.php` - Dashboard principal
   - `tracker_v6_improved.js` - Tracker amélioré
   - `test_tracker_debug.html` - Page de test

2. **Accès au dashboard :**
   ```
   https://christellelusso.nexgate.ch/dashboard_php.php
   ```

3. **Avantages :**
   - ✅ Fonctionne sur tous les hébergeurs PHP
   - ✅ Pas de dépendances externes
   - ✅ Mise à jour via Web-FTP
   - ✅ Interface moderne avec Bootstrap
   - ✅ Cartes interactives avec Leaflet

### **Alternative : Service Externe**

Pour garder Streamlit, déployer sur :
- **Streamlit Cloud** (gratuit) : `https://votre-app.streamlit.app`
- **VPS** (payant) : Votre propre serveur

Voir `GUIDE_DEPLOIEMENT_NEXGATE.md` pour les détails complets.

---

**Version :** 1.0  
**Dernière mise à jour :** 1er septembre 2025  
**Auteur :** Christelle Lusso
