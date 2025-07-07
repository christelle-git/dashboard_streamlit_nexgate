# 🌐 Site Personnel - Christelle Lusso

Site personnel de Christelle Lusso, hébergé sur GitHub Pages.

## 📋 Description

Ce site présente le profil professionnel de Christelle Lusso, incluant :
- Ses publications scientifiques
- Ses conférences et présentations
- Son enseignement
- Ses dessins et créations artistiques

## 🚀 Accès au Site

Le site est accessible à l'adresse : `https://[votre-username].github.io/[nom-du-repo]`

## 📁 Structure du Projet

```
├── index.html          # Page principale du site
├── README.md           # Ce fichier
├── dashboard.py        # Dashboard analytics Streamlit
├── requirements.txt    # Dépendances Python
└── pdf/               # Dossier pour les fichiers PDF
    ├── abstract_lusso.pdf
    ├── presentation_ljll.pdf
    └── thesis.pdf
```

## 🛠️ Installation Locale

### Prérequis
- Python 3.8+
- Git

### Étapes d'installation

1. **Cloner le repository**
   ```bash
   git clone https://github.com/[votre-username]/[nom-du-repo].git
   cd [nom-du-repo]
   ```

2. **Installer les dépendances Python** (pour le dashboard)
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer le dashboard analytics** (optionnel)
   ```bash
   streamlit run dashboard.py
   ```

## 🌐 Déploiement sur GitHub Pages

### Méthode 1 : Via l'interface GitHub

1. Allez dans les **Settings** de votre repository
2. Scrollez jusqu'à la section **Pages**
3. Dans **Source**, sélectionnez **Deploy from a branch**
4. Choisissez la branche **main** et le dossier **/ (root)**
5. Cliquez sur **Save**

### Méthode 2 : Via GitHub Actions (recommandé)

1. Créez un fichier `.github/workflows/deploy.yml` :

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

## 📝 Mise à Jour du Site

### Ajouter de nouveaux contenus

1. Modifiez le fichier `index.html`
2. Committez vos changements :
   ```bash
   git add .
   git commit -m "Ajout de nouveaux contenus"
   git push origin main
   ```

### Ajouter des fichiers PDF

1. Placez vos fichiers PDF dans le dossier `pdf/`
2. Mettez à jour les liens dans `index.html`
3. Committez et poussez les changements

## 🔧 Personnalisation

### Modifier le style
- Éditez la section `<style>` dans `index.html`
- Les couleurs principales sont définies avec `#00E673` (vert)

### Ajouter de nouvelles sections
- Copiez la structure d'une section existante
- Modifiez le contenu selon vos besoins

## 📊 Dashboard Analytics

Le projet inclut un dashboard Streamlit pour analyser les statistiques du site :

- **Géolocalisation** des visiteurs
- **Parcours utilisateurs** sur le site
- **Fichiers les plus consultés**
- **Temps de session**

Pour lancer le dashboard :
```bash
streamlit run dashboard.py
```

## 🔒 Sécurité

- Le site utilise uniquement des ressources externes sécurisées (CDN)
- Aucune donnée personnelle n'est stockée
- Les liens vers les publications pointent vers des archives académiques fiables

## 📞 Support

Pour toute question ou problème :
- Ouvrez une **Issue** sur GitHub
- Contactez : christelle.lusso@gmail.com

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

**Note :** Ce site a été créé suite à l'indisponibilité temporaire de nexgate.ch. Les vraies images et fichiers PDF seront restaurés une fois que le serveur original sera de nouveau accessible.
