# Dashboard Streamlit – Analytics (Nexgate)

Objectif: déployer rapidement le dashboard en tant que web app sur Streamlit Cloud, en lisant les données depuis `https://christellelusso.nexgate.ch/analytics_data.json`.

Fichiers importants
- `dashboard.py` (main app)
- `config_setup.py` (config centralisée – aucune variable obligatoire)
- `requirements.txt` (dépendances pour Streamlit Cloud)
- `.streamlit/config.toml` (options d’UI – optionnel)

Déploiement sur Streamlit Cloud (résumé)
1. Créer un repo GitHub (ou une branche dédiée)
2. Pousser ces fichiers au root du repo
3. Sur Streamlit Cloud: New app → choisir le repo/branche → Main file: `dashboard.py` → Deploy

Notes
- Les données sont lues côté app via `requests` depuis Nexgate; aucun fichier JSON local n’est requis.
- Le stockage local (SQLite) est optionnel et éphémère sur Streamlit Cloud.

## Déploiement Streamlit Cloud via branche orpheline

Pour publier uniquement l’app (sans le reste du projet), utiliser une branche orpheline minimale.

Étapes:
- Créer la branche locale orpheline:
  ```bash
  git switch --orphan streamlit-deploy
  ```
- Ajouter seulement les fichiers requis:
  ```bash
  git add -f dashboard.py requirements.txt .streamlit/config.toml
  git commit -m "Initial Streamlit Cloud app (fichiers minimaux)"
  ```
- Pousser cette branche vers le repo dédié:
  ```bash
  git remote set-url origin https://github.com/christelle-git/dashboard_streamlit_nexgate.git
  git push -u origin streamlit-deploy
  ```
- Sur Streamlit Cloud: New app → repo/branche ci‑dessus → Main file: `dashboard.py` → Deploy

## Stocker le token GitHub de façon sécurisée (sans le pousser)

Option A – Fichier `~/.netrc` (simple)
1. Éditer `~/.netrc`:
   ```
   machine github.com
     login christelle-git
     password VOTRE_TOKEN_GH_ICI
   ```
2. Protéger le fichier:
   ```bash
   chmod 600 ~/.netrc
   ```

Option B – Script `GIT_ASKPASS` (temporaire)
1. Créer `~/.git-askpass-github`:
   ```bash
   #!/bin/sh
   case "$1" in
     *Username*) echo "christelle-git" ;;
     *Password*) echo "VOTRE_TOKEN_GH_ICI" ;;
   esac
   ```
2. Protéger le script:
   ```bash
   chmod 700 ~/.git-askpass-github
   ```
3. Utiliser pour pousser:
   ```bash
   GIT_ASKPASS=~/.git-askpass-github git push -u origin streamlit-deploy
   ```

Remarques:
- Ces fichiers sont hors dépôt (dans votre HOME) et ne doivent jamais être ajoutés au repo.
- Vous pouvez révoquer le token à tout moment dans GitHub → Settings → Developer settings → Personal access tokens.