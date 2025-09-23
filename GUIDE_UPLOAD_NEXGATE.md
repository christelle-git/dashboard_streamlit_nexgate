# 🚀 Guide d'Upload sur Nexgate

## 📁 Fichiers à uploader

### **Fichiers principaux :**
- `dashboard_php.php` → **Racine** de votre site
- `tracker_v6_improved.js` → **Racine** de votre site

### **Fichiers de protection :**
- `.htaccess` → **Racine** de votre site (chez Nexgate il peut apparaître comme `htaccess` sans le point)
- `.htpasswd` → **Racine** de votre site

## 🔧 Étapes d'upload

### **1. Connexion Web-FTP :**
1. Allez sur votre espace Nexgate
2. Connectez-vous avec vos identifiants
3. Accédez au gestionnaire de fichiers

### **2. Upload des fichiers :**
1. **Sélectionnez** le dossier racine (où est `index.html`)
2. **Uploadez** les fichiers :
   - `dashboard_php.php`
   - `tracker_v6_improved.js`
   - `.htaccess` (ou `htaccess` selon Web‑FTP)
   - `.htpasswd`
   - `check_new_sessions.php`
   - `send_alert.php`

### **3. Vérification :**
- Vérifiez que tous les fichiers sont présents
- Vérifiez que `.htaccess` et `.htpasswd` sont bien uploadés

## 🧪 Test d'accès

### **URL du dashboard :**
```
https://christellelusso.nexgate.ch/dashboard_php.php
```

### **Ce qui doit se passer :**
1. **Pop-up de connexion** apparaît
2. **Login :** `admin`
3. **Mot de passe :** [celui que vous avez choisi]
4. **Dashboard s'affiche** après authentification

## 🔒 Sécurité

### **Protection activée :**
- ✅ Dashboard protégé par mot de passe
- ✅ Données analytics protégées
- ✅ Pas d'indexation Google possible
- ✅ Accès contrôlé

### **Identifiants :**
- **Utilisateur :** `admin`
- **Mot de passe :** [celui que vous avez défini]

## 🚨 Dépannage

### **Si le pop-up n'apparaît pas :**
- Vérifiez que `.htaccess` est bien uploadé
- Chez Nexgate, le fichier peut s'afficher comme `htaccess` sans point: c'est acceptable
- Vérifiez que `.htpasswd` est bien uploadé
- Vérifiez les permissions des fichiers

### **Si l'authentification échoue :**
- Vérifiez le nom d'utilisateur : `admin`
- Vérifiez le mot de passe
- Vérifiez que `.htpasswd` est dans le bon dossier

## ✉️ Tester l'alerte email (anti-boucle)

1. Ouvrez `https://christellelusso.nexgate.ch/check_new_sessions.php`
2. Si de nouvelles `session_start` (hors IP fixe) sont présentes depuis les 24 dernières heures, un **email récapitulatif unique** est envoyé.
3. Le script applique un **cooldown de 10 minutes** et ne renvoie pas deux fois la même session (`notified_sessions.json`).

Astuce: pour un test immédiat, créez une session externe (mobile 4G, navigation privée).

## 📞 Support

Si vous avez des problèmes, contactez le support Nexgate ou consultez la documentation de votre hébergeur.
