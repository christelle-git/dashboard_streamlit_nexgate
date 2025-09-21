# 🚀 Guide de Déploiement sur Nexgate

## 📋 Vue d'ensemble

Ce guide explique comment déployer le dashboard de tracking analytics sur l'hébergeur Nexgate, qui ne propose qu'un accès Web-FTP (pas d'SSH).

## 🎯 Options de Déploiement

### **Option 1 : Dashboard PHP (Recommandé)**
- ✅ **Avantages** : Simple, rapide, pas de dépendances externes
- ✅ **Compatibilité** : Fonctionne sur tous les hébergeurs PHP
- ✅ **Maintenance** : Facile à mettre à jour via Web-FTP
- ✅ **Coût** : Gratuit (utilise votre hébergement Nexgate)
- ❌ **Limitations** : Moins de fonctionnalités que Streamlit

### **Option 2 : Dashboard Streamlit + Service Externe**
- ✅ **Avantages** : Fonctionnalités complètes, interface moderne
- ✅ **Flexibilité** : Déploiement sur VPS ou cloud
- ❌ **Complexité** : Nécessite un serveur externe
- ❌ **Coût** : VPS payant (5-20€/mois) ou Streamlit Cloud (gratuit)

### **Architecture de votre hébergement actuel :**
- **Site web** : GitHub Pages (`https://christellelusso.github.io/`)
- **API + Données** : Nexgate (`https://christellelusso.nexgate.ch/`)
- **Dashboard** : À déployer sur Nexgate (PHP) ou VPS (Streamlit)

**⚠️ Important :** Ne supprimez PAS Nexgate ! Il héberge votre API et vos données.

## 🛠️ Déploiement Option 1 : Dashboard PHP

### **Étape 1 : Préparation des fichiers**

1. **Fichiers à uploader sur Nexgate :**
   ```
   📁 christellelusso.nexgate.ch/
   ├── 📄 dashboard_php.php          # Dashboard principal
   ├── 📄 analytics_data.json        # Données (déjà présent)
   ├── 📄 api.php                    # API (déjà présent)
   ├── 📄 tracker_v6_improved.js     # Tracker amélioré
   ├── 📄 index.html                 # Site principal (à mettre à jour)
   └── 📄 test_tracker_debug.html    # Page de test
   ```

2. **Mettre à jour index.html :**
   - Remplacer le tracker par `tracker_v6_improved.js`
   - Ajouter un lien vers le dashboard

### **Étape 2 : Upload via Web-FTP**

1. **Se connecter à Nexgate Web-FTP**
   - Aller sur l'interface Nexgate
   - Sélectionner le compte FTP `christellelusso`

2. **Uploader les fichiers**
   - Glisser-déposer `dashboard_php.php`
   - Glisser-déposer `tracker_v6_improved.js`
   - Glisser-déposer `test_tracker_debug.html`

3. **Vérifier les permissions**
   - S'assurer que `analytics_data.json` est accessible en lecture
   - Vérifier que `api.php` fonctionne

### **Étape 3 : Test et validation**

1. **Tester le dashboard :**
   ```
   https://christellelusso.nexgate.ch/dashboard_php.php
   ```

2. **Tester le tracker :**
   ```
   https://christellelusso.nexgate.ch/test_tracker_debug.html
   ```

3. **Vérifier les données :**
   - Le dashboard doit afficher les sessions
   - La carte doit montrer les localisations
   - Les statistiques doivent être correctes

## 🚀 Déploiement Option 2 : Streamlit + Service Externe

### **Option 2A : Streamlit Cloud (Gratuit)**

1. **Préparer le repository :**
   ```bash
   # Créer un repository GitHub
   git init
   git add .
   git commit -m "Dashboard de tracking analytics"
   git remote add origin https://github.com/votre-username/dashboard-tracking.git
   git push -u origin main
   ```

2. **Déployer sur Streamlit Cloud :**
   - Aller sur https://share.streamlit.io
   - Connecter le repository GitHub
   - Configurer l'application
   - URL finale : `https://votre-app.streamlit.app`

3. **Configuration :**
   ```python
   # streamlit_app.py
   import streamlit as st
   from dashboard_simple import main
   
   if __name__ == "__main__":
       main()
   ```

### **Option 2B : VPS avec Docker**

1. **Créer un VPS :**
   - DigitalOcean, OVH, ou autre
   - Ubuntu 20.04+
   - Docker installé

2. **Déployer avec Docker :**
   ```bash
   # Sur le VPS
   git clone https://github.com/votre-username/dashboard-tracking.git
   cd dashboard-tracking
   
   # Créer le Dockerfile
   cat > Dockerfile << EOF
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8501
   CMD ["streamlit", "run", "dashboard_simple.py", "--server.port=8501", "--server.address=0.0.0.0"]
   EOF
   
   # Construire et lancer
   docker build -t dashboard-tracking .
   docker run -d -p 8501:8501 --name dashboard dashboard-tracking
   ```

3. **Configuration Nginx (optionnel) :**
   ```nginx
   server {
       listen 80;
       server_name dashboard.christellelusso.com;
       
       location / {
           proxy_pass http://localhost:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

## 🔧 Configuration et Maintenance

### **Variables d'environnement**

Pour le dashboard PHP, créer un fichier `.htaccess` :
```apache
# .htaccess
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^dashboard$ dashboard_php.php [L]

# Cache pour les données
<Files "analytics_data.json">
    ExpiresActive On
    ExpiresByType application/json "access plus 5 minutes"
</Files>
```

### **Mise à jour des données**

Le dashboard PHP se met à jour automatiquement :
- **Cache** : 5 minutes
- **Source** : `analytics_data.json` sur Nexgate
- **Rafraîchissement** : Automatique toutes les 5 minutes

### **Monitoring**

1. **Vérifier les logs :**
   - Logs d'erreur PHP dans Nexgate
   - Logs d'accès au dashboard

2. **Surveiller les performances :**
   - Temps de chargement du dashboard
   - Taille du fichier `analytics_data.json`

## 📊 Accès au Dashboard

### **URLs d'accès :**

1. **Dashboard PHP :**
   ```
   https://christellelusso.nexgate.ch/dashboard_php.php
   ```

2. **Page de test :**
   ```
   https://christellelusso.nexgate.ch/test_tracker_debug.html
   ```

3. **API des données :**
   ```
   https://christellelusso.nexgate.ch/analytics_data.json
   ```

### **Sécurité (optionnel) :**

Ajouter une authentification basique :
```php
// En haut de dashboard_php.php
if (!isset($_SERVER['PHP_AUTH_USER']) || 
    $_SERVER['PHP_AUTH_USER'] !== 'admin' || 
    $_SERVER['PHP_AUTH_PW'] !== 'motdepasse') {
    header('WWW-Authenticate: Basic realm="Dashboard"');
    header('HTTP/1.0 401 Unauthorized');
    die('Accès refusé');
}
```

## 🔄 Workflow de Mise à Jour

### **1. Développement local :**
```bash
# Modifier le code
# Tester localement
git add .
git commit -m "Description des changements"
git push origin main
```

### **2. Déploiement sur Nexgate :**
1. **Télécharger** les fichiers modifiés depuis GitHub
2. **Uploader** via Web-FTP sur Nexgate
3. **Tester** le dashboard en ligne
4. **Vérifier** que tout fonctionne

### **3. Documentation :**
1. **Mettre à jour** `DOCUMENTATION_DASHBOARD_TRACKING.md`
2. **Committer** les changements
3. **Taguer** la version si nécessaire

## 🎯 Recommandation Finale

**Pour votre cas d'usage, je recommande l'Option 1 (Dashboard PHP) :**

✅ **Simple** : Upload via Web-FTP  
✅ **Rapide** : Pas de configuration complexe  
✅ **Fiable** : Fonctionne sur tous les hébergeurs  
✅ **Maintenable** : Facile à mettre à jour  
✅ **Gratuit** : Pas de coût supplémentaire  

Le dashboard PHP offre toutes les fonctionnalités essentielles :
- Visualisation des sessions
- Géolocalisation sur carte
- Statistiques détaillées
- Interface responsive
- Mise à jour automatique

---

**Version :** 1.0  
**Dernière mise à jour :** 1er septembre 2025  
**Auteur :** Christelle Lusso
