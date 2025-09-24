# 📊 Documentation du Dashboard de Tracking Analytics

## Sommaire

- [🎯 Vue d'ensemble](#-vue-densemble)
- [🏗️ Architecture du Système](#️-architecture-du-système)
- [📁 Structure des Fichiers](#-structure-des-fichiers)
- [🔧 Configuration et Installation](#-configuration-et-installation)
- [🏗️ Architecture et Options de Déploiement](#️-architecture-et-options-de-déploiement)
  - [Comparaison des solutions de déploiement](#comparaison-des-solutions-de-déploiement-)
  - [Parité d’UI avec le dashboard Nexgate (PHP)](#parité-dui-avec-le-dashboard-nexgate-php)
  - [Mode Production – Source unique Nexgate](#mode-production--source-unique-nexgate-sans-fallback)
  - [Dépannage – Accès HTTPS depuis Streamlit Cloud](#dépannage--accès-https-depuis-streamlit-cloud)
- [📊 Fonctionnalités du Dashboard](#-fonctionnalités-du-dashboard)
- [🎯 Types d'Événements Trackés](#-types-déénements-trackés)
- [🔄 Workflow de Développement](#-workflow-de-développement)
- [🛠️ Maintenance et Monitoring](#️-maintenance-et-monitoring)
- [🔒 Sécurité](#-sécurité)
- [📈 Évolutions Futures](#-évolutions-futures)
- [🐛 Dépannage](#-dépannage)
- [📞 Support](#-support)
- [🌐 Déploiement sur Nexgate (Hébergeur Web-FTP)](#-déploiement-sur-nexgate-hébergeur-web-ftp)

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

## 🏗️ Architecture et Options de Déploiement

### **Architecture actuelle de votre hébergement :**
- **Site web** : GitHub Pages (`https://christellelusso.github.io/`)
- **API + Données** : Nexgate (`https://christellelusso.nexgate.ch/`)
- **Dashboard** : À déployer (voir options ci-dessous)

### **Qu'est-ce qu'un VPS ?**

**VPS = Virtual Private Server** (Serveur Privé Virtuel)

- **Définition :** Un serveur informatique "virtuel" que vous louez chez un hébergeur
- **Exemples d'hébergeurs :** DigitalOcean, OVH, Scaleway, AWS, Google Cloud
- **Prix :** 5-20€/mois pour un petit serveur
- **Avantages :** 
  - Accès complet (SSH, terminal)
  - Installation libre (Python, Docker, etc.)
  - Contrôle total du serveur
  - Déploiement automatisé avec `deploy.sh`
- **Inconvénients :** 
  - Plus cher que l'hébergement web classique
  - Plus complexe à gérer
  - Nécessite des connaissances techniques

### **Comparaison des solutions de déploiement :**

| Aspect | Dashboard PHP | Streamlit Cloud | VPS + Streamlit |
|--------|---------------|-----------------|-----------------|
| **Coût** | Gratuit | Gratuit | 5-20€/mois |
| **Hébergement** | Nexgate | Streamlit | VPS externe |
| **Technologie** | PHP + HTML/JS | Python + Streamlit | Python + Streamlit |
| **Installation** | Upload Web-FTP | Déploiement Git | SSH + Docker |
| **Fonctionnalités** | Basiques | Avancées | Avancées |
| **Maintenance** | Manuelle | Automatique | Automatique |
| **Complexité** | Simple | Moyenne | Complexe |
| **Contrôle** | Limité | Moyen | Total |

### **Déploiement Streamlit Cloud via branche orpheline (recommandé pour partage rapide)**

Objectif: publier une web app minimale sans exposer tout le dépôt.

Étapes synthétiques:

1. Créer une branche orpheline locale (sans historique):
```
git switch --orphan streamlit-deploy
```
2. Ajouter seulement les fichiers requis (exemples):
```
git add -f dashboard.py requirements.txt .streamlit/config.toml
git commit -m "Initial Streamlit Cloud app (fichiers minimaux)"
```
3. Pousser la branche vers un repo public dédié:
```
git remote set-url origin https://github.com/christelle-git/dashboard_streamlit_nexgate.git
git push -u origin streamlit-deploy
```
4. Sur Streamlit Cloud: New app → sélectionner le repo/branche ci‑dessus → Main file: `dashboard.py` → Deploy

Notes:
- Cette branche ne contient que l’app; aucune donnée/secret.
- Les données sont lues via HTTP depuis `analytics_data.json` sur Nexgate.

### **Parité d’UI avec le dashboard Nexgate (PHP)**

La version Streamlit a été alignée pour correspondre aux vues du dashboard PHP Nexgate:

- Titre: `Tracking nexgate Christelle`.
- Bandeau d’état indiquant la source des données Nexgate.
- Onglets et libellés identiques:
  - "🌍 Géolocalisation": tableau trié du plus récent au plus ancien, colonnes `Date`, `Heure`, `Session ID`, `Pays`, `Ville`, `IP Utilisateur`.
  - "📁 Tracking par Fichier": graphique barres "Fichiers les plus cliqués" + tableau des clics (Date, page, fichier).
  - "🚶 Parcours Utilisateurs": Top 5 des parcours + tableau détaillé par session.

Pour obtenir cette UI sur Streamlit Cloud, assurez‑vous de pousser la branche `streamlit-deploy` après modification locale:
```
git switch streamlit-deploy
git merge main   # pour récupérer les dernières améliorations UI
git push -u origin streamlit-deploy
```

### **Mode Production – Source unique Nexgate (sans fallback)**

Depuis le 24/09/2025, le dashboard Streamlit (branche `streamlit-deploy`) lit les données UNIQUEMENT depuis:

```
https://christellelusso.nexgate.ch/analytics_data.json
```

Si Nexgate est indisponible, l’app affiche un message explicite et ne charge pas de données (aucun fallback automatique vers GitHub/local).

Motivation:
- garantir que les utilisateurs externes voient exactement les données de Nexgate
- éviter les divergences entre un JSON GitHub et Nexgate

### **Dépannage – Accès HTTPS depuis Streamlit Cloud**

Symptôme: bandeau rouge du type « Nexgate indisponible » avec erreur `Connection refused`.

**Diagnostic effectué** ✅ :
- **TLS/SSL** : Certificat Let's Encrypt valide (expire 29/11/2025)
- **Port 443** : Ouvert et fonctionnel  
- **Fichier** : Accessible publiquement (HTTP 200, Content-Type: application/json, 167 KB)
- **Réseau local** : `curl` fonctionne parfaitement

**Cause identifiée** : Filtrage IP/anti-bot Nexgate qui bloque les requêtes depuis Streamlit Cloud (AWS)

**Message type pour le support Nexgate** :
```
Sujet : Blocage des requêtes depuis Streamlit Cloud (AWS) vers analytics_data.json

Bonjour,

Je rencontre un problème d'accès à mon fichier analytics_data.json depuis Streamlit Cloud.

URL : https://christellelusso.nexgate.ch/analytics_data.json
Symptôme : "Connection refused" depuis Streamlit Cloud (hébergé sur AWS)
Test local : ✅ Accessible depuis mon réseau (curl fonctionne)

Pouvez-vous vérifier s'il y a un filtrage IP ou anti-bot qui bloque les requêtes 
depuis les IPs AWS de Streamlit Cloud ?

Solutions possibles :
1. Whitelister les IPs sortantes AWS (région Streamlit Cloud)
2. Désactiver le blocage anti-bot pour /analytics_data.json
3. Autoriser les requêtes GET publiques avec User-Agent standard

Merci pour votre aide.
```

**Vérifications techniques** :
```bash
# Test de connectivité (doit retourner 200 OK)
curl -Iv https://christellelusso.nexgate.ch/analytics_data.json

# Vérification du certificat SSL
openssl s_client -connect christellelusso.nexgate.ch:443 -servername christellelusso.nexgate.ch
```

### **Vérifier rapidement côté app**

Dans l’interface Streamlit:
- si bandeau rouge + message `Connection refused`, l’application est fonctionnelle mais Nexgate refuse la connexion
- dès que `curl -I` renvoie 200 et que Nexgate est accessible depuis Internet, un simple « Rerun » recharge les données

### **Script deploy.sh - Quand l'utiliser ?**

Le script `deploy.sh` est **UNIQUEMENT** pour les VPS externes :

- ❌ **Nexgate** : Impossible (pas d'SSH)
- ❌ **GitHub Pages** : Impossible (statique uniquement)
- ✅ **VPS** : Utilisable avec `./deploy.sh production`
- ✅ **Streamlit Cloud** : Déploiement automatique via Git

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

### **3. Gestion sécurisée du token GitHub (pour `git push`)**

Ne jamais committer un token. Méthodes recommandées sans exposition:

- Option A – Fichier `~/.netrc` (simple):
```
machine github.com
  login christelle-git
  password VOTRE_TOKEN_GH_ICI
```
Puis protéger: `chmod 600 ~/.netrc`.

- Option B – Script `GIT_ASKPASS` local (temporaire):
```
#!/bin/sh
case "$1" in
  *Username*) echo "christelle-git" ;;
  *Password*) echo "VOTRE_TOKEN_GH_ICI" ;;
esac
```
Sauver dans `~/.git-askpass-github`, protéger: `chmod 700 ~/.git-askpass-github`, puis:
```
GIT_ASKPASS=~/.git-askpass-github git push -u origin streamlit-deploy
```

- Option C – Fichier caché dans le HOME: `.token_github` (non versionné)
  1. Créer `~/.token_github` contenant uniquement le token
  2. Protéger: `chmod 600 ~/.token_github`
  3. Utiliser ponctuellement:
```
GIT_ASKPASS=<(printf '#!/bin/sh\ncase "$1" in\n*Username*) echo "christelle-git" ;;\n*Password*) cat ~/.token_github ;;\nesac\n') git push -u origin streamlit-deploy
```
  (sur macOS zsh/bash, <( … ) crée un script éphémère en mémoire)

Astuce: ajouter `.token_github` à `.gitignore` pour éviter tout ajout accidentel.

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

### **Architecture de votre hébergement actuel :**
- **Site web** : GitHub Pages (`https://christellelusso.github.io/`)
- **API + Données** : Nexgate (`https://christellelusso.nexgate.ch/`)
- **Dashboard** : À déployer sur Nexgate (PHP) ou VPS (Streamlit)

### **Solution Recommandée : Dashboard PHP**

1. **Fichiers à uploader sur Nexgate :**
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
   - ✅ Gratuit (utilise votre hébergement Nexgate)

### **Alternative : Service Externe**

Pour garder Streamlit, déployer sur :
- **Streamlit Cloud** (gratuit) : `https://votre-app.streamlit.app`
- **VPS** (payant, 5-20€/mois) : Votre propre serveur

### **Comparaison des solutions :**

| Solution | Coût | Complexité | Fonctionnalités | Maintenance |
|----------|------|------------|-----------------|-------------|
| **Dashboard PHP** | Gratuit | Simple | Bonnes | Manuelle (Web-FTP) |
| **Streamlit Cloud** | Gratuit | Moyenne | Excellentes | Automatique (Git) |
| **VPS + Streamlit** | 5-20€/mois | Complexe | Excellentes | Automatique (Git) |

Voir `GUIDE_DEPLOIEMENT_NEXGATE.md` pour les détails complets.

---

**Version :** 1.0  
**Dernière mise à jour :** 1er septembre 2025  
**Auteur :** Christelle Lusso
