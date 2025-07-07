# 🚀 Guide de Déploiement sur GitHub Pages

Ce guide vous accompagne étape par étape pour héberger votre site personnel sur GitHub Pages.

## 📋 Prérequis

- Un compte GitHub
- Git installé sur votre machine
- Les fichiers du site prêts (déjà créés)

## 🔧 Étapes de Déploiement

### **Étape 1 : Créer un nouveau repository GitHub**

1. Allez sur [GitHub.com](https://github.com) et connectez-vous
2. Cliquez sur le bouton **"New"** ou **"+"** puis **"New repository"**
3. Configurez votre repository :
   - **Repository name** : `christelle-lusso-site` (ou le nom de votre choix)
   - **Description** : `Site personnel de Christelle Lusso`
   - **Public** : ✅ Cochez cette option (nécessaire pour GitHub Pages gratuit)
   - **Add a README file** : ❌ Décochez (nous avons déjà un README)
   - **Add .gitignore** : ❌ Décochez (nous avons déjà un .gitignore)
4. Cliquez sur **"Create repository"**

### **Étape 2 : Initialiser Git localement**

```bash
# Dans le dossier de votre projet
git init
git add .
git commit -m "Initial commit - Site personnel Christelle Lusso"
```

### **Étape 3 : Connecter au repository GitHub**

```bash
# Remplacez [votre-username] et [nom-du-repo] par vos valeurs
git remote add origin https://github.com/[votre-username]/[nom-du-repo].git
git branch -M main
git push -u origin main
```

### **Étape 4 : Activer GitHub Pages**

#### **Méthode 1 : Via l'interface GitHub (Recommandée)**

1. Allez dans votre repository sur GitHub
2. Cliquez sur **"Settings"** (onglet en haut)
3. Dans le menu de gauche, cliquez sur **"Pages"**
4. Dans la section **"Source"** :
   - Sélectionnez **"Deploy from a branch"**
   - Choisissez la branche **"main"**
   - Sélectionnez le dossier **"/ (root)"**
5. Cliquez sur **"Save"**

#### **Méthode 2 : Via GitHub Actions (Avancée)**

1. Créez le dossier `.github/workflows/` dans votre projet
2. Créez le fichier `.github/workflows/deploy.yml` :

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./
```

### **Étape 5 : Vérifier le déploiement**

1. Attendez quelques minutes que GitHub Pages se déploie
2. Votre site sera accessible à l'adresse :
   ```
   https://[votre-username].github.io/[nom-du-repo]
   ```
3. Par exemple : `https://christellelusso.github.io/christelle-lusso-site`

## 🔄 Mise à Jour du Site

### **Pour modifier le contenu :**

```bash
# Modifiez les fichiers (index.html, etc.)
git add .
git commit -m "Mise à jour du contenu"
git push origin main
```

### **Pour ajouter de nouveaux fichiers PDF :**

1. Placez vos fichiers dans le dossier `pdf/`
2. Mettez à jour les liens dans `index.html`
3. Committez et poussez :

```bash
git add pdf/
git add index.html
git commit -m "Ajout de nouveaux fichiers PDF"
git push origin main
```

## 🎨 Personnalisation

### **Changer les couleurs :**
- Modifiez la couleur principale `#00E673` dans `index.html`
- Cette couleur est utilisée pour les bordures et accents

### **Ajouter de nouvelles sections :**
- Copiez la structure d'une section existante dans `index.html`
- Modifiez le contenu selon vos besoins

### **Changer le nom de domaine (optionnel) :**
1. Achetez un nom de domaine (ex: `christellelusso.com`)
2. Dans les Settings > Pages de votre repository :
   - Ajoutez votre domaine personnalisé
   - Configurez les DNS selon les instructions GitHub

## 🔒 Sécurité et Bonnes Pratiques

### **Sécurité :**
- ✅ Le site est public (nécessaire pour GitHub Pages gratuit)
- ✅ Aucune donnée personnelle sensible n'est exposée
- ✅ Les liens vers les publications pointent vers des archives académiques fiables

### **Bonnes pratiques :**
- ✅ Committez régulièrement vos changements
- ✅ Utilisez des messages de commit descriptifs
- ✅ Testez localement avant de pousser
- ✅ Gardez une copie de sauvegarde locale

## 🐛 Dépannage

### **Le site ne s'affiche pas :**
1. Vérifiez que GitHub Pages est activé dans les Settings
2. Attendez 5-10 minutes pour le déploiement initial
3. Vérifiez l'URL exacte dans les Settings > Pages

### **Les images ne s'affichent pas :**
1. Vérifiez que les chemins des images sont corrects
2. Assurez-vous que les images sont bien commitées
3. Utilisez des chemins relatifs (ex: `./images/photo.jpg`)

### **Erreur 404 :**
1. Vérifiez que le fichier `index.html` est à la racine du repository
2. Assurez-vous que le nom du fichier est exactement `index.html`
3. Vérifiez que le fichier est bien commité et poussé

## 📞 Support

### **En cas de problème :**
1. Vérifiez la documentation GitHub Pages : https://pages.github.com/
2. Consultez les logs de déploiement dans l'onglet "Actions" de votre repository
3. Contactez le support GitHub si nécessaire

### **Pour des questions spécifiques :**
- Ouvrez une Issue sur votre repository GitHub
- Contactez : christelle.lusso@gmail.com

## 🎉 Félicitations !

Votre site est maintenant hébergé sur GitHub Pages et accessible publiquement. 
Le site sera automatiquement mis à jour à chaque push sur la branche main.

---

**Note :** Ce guide a été créé pour remplacer temporairement nexgate.ch. 
Une fois que le serveur original sera de nouveau accessible, vous pourrez 
récupérer les vraies images et fichiers PDF. 