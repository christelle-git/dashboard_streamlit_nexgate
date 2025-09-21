# 🚀 Guide d'Upload sur Nexgate

## 📁 Fichiers à uploader

### **Fichiers principaux :**
- `dashboard_php.php` → **Racine** de votre site
- `tracker_v6_improved.js` → **Racine** de votre site

### **Fichiers de protection :**
- `.htaccess` → **Racine** de votre site
- `.htpasswd` → **Racine** de votre site

## 🔧 Étapes d'upload

### **1. Connexion Web-FTP :**
1. Allez sur votre espace Nexgate
2. Connectez-vous avec vos identifiants
3. Accédez au gestionnaire de fichiers

### **2. Upload des fichiers :**
1. **Sélectionnez** le dossier racine (où est `index.html`)
2. **Uploadez** les 4 fichiers :
   - `dashboard_php.php`
   - `tracker_v6_improved.js`
   - `.htaccess`
   - `.htpasswd`

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
- Vérifiez que `.htpasswd` est bien uploadé
- Vérifiez les permissions des fichiers

### **Si l'authentification échoue :**
- Vérifiez le nom d'utilisateur : `admin`
- Vérifiez le mot de passe
- Vérifiez que `.htpasswd` est dans le bon dossier

## 📞 Support

Si vous avez des problèmes, contactez le support Nexgate ou consultez la documentation de votre hébergeur.
